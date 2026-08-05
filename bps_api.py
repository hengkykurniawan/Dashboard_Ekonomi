"""
Shared helpers for talking to the BPS WebAPI (https://webapi.bps.go.id).

Key handling (in priority order):
  1. Environment variable  BPS_API_KEY   <- used by GitHub Actions (a Secret)
  2. Local file            bps_key.txt    <- used for local testing (gitignored)

The key is NEVER printed and NEVER embedded in logged URLs.
"""
from __future__ import annotations

import os
import sys
import time
from pathlib import Path

import requests

BASE = "https://webapi.bps.go.id/v1/api"
NATIONAL_DOMAIN = "0000"          # "Pusat" — all-Indonesia
KEY_FILE = Path(__file__).with_name("bps_key.txt")


def load_key() -> str:
    """Return the BPS API key from env or the local file, or exit with guidance."""
    key = os.environ.get("BPS_API_KEY", "").strip()
    if not key and KEY_FILE.exists():
        key = KEY_FILE.read_text(encoding="utf-8").strip()
    if not key:
        sys.exit(
            "No BPS API key found.\n"
            "  - Local:  put your key in a file named 'bps_key.txt' (gitignored), or\n"
            "  - Set:    $env:BPS_API_KEY = '<key>'   (PowerShell)\n"
            "  - CI:     store it as the GitHub Secret BPS_API_KEY"
        )
    return key


def _redact(url: str, key: str) -> str:
    return url.replace(key, "***") if key else url


class BPSClient:
    def __init__(self, key: str | None = None, domain: str = NATIONAL_DOMAIN):
        self.key = key or load_key()
        self.domain = domain
        self.session = requests.Session()
        self.session.headers.update({"User-Agent": "Dashboard_Ekonomi/1.0 (+github actions)"})
        self._down = False          # circuit breaker: trips on a full outage
        self._consecutive_fail = 0

    # The BPS WebAPI intermittently drops connections from cloud runners
    # (RemoteDisconnected). Retry transient single failures with backoff — but
    # once several calls fail in a row (a full outage), the circuit breaker
    # trips and the rest fail fast so the run doesn't crawl. A later cron run
    # then picks up the data when the API recovers.
    RETRIES = 3
    BACKOFF = 2       # seconds, multiplied by the attempt number
    TRIP_AFTER = 3    # consecutive full failures before failing fast

    def _get(self, path: str) -> dict:
        url = f"{BASE}/{path}/key/{self.key}/"
        tries = 1 if self._down else self.RETRIES
        last_err = None
        for attempt in range(1, tries + 1):
            try:
                r = self.session.get(url, timeout=30)
                r.raise_for_status()
                data = r.json()
                if isinstance(data, dict) and str(data.get("status", "OK")).upper() == "ERROR":
                    raise RuntimeError(f"BPS API error: {data.get('message')}")
                self._consecutive_fail = 0
                self._down = False
                return data
            except (requests.RequestException, ValueError) as e:
                last_err = e
                if attempt < tries:
                    time.sleep(self.BACKOFF * attempt)
        self._consecutive_fail += 1
        if self._consecutive_fail >= self.TRIP_AFTER:
            self._down = True     # stop retrying for the rest of this run
        raise RuntimeError(
            f"BPS request failed for {_redact(url, self.key)} after {tries} tries: {last_err}"
        )

    # ---- catalogue endpoints (used by discover_bps.py) ----
    def list_subjects(self, page: int = 1) -> dict:
        return self._get(f"list/model/subject/lang/ind/domain/{self.domain}/page/{page}")

    def list_variables(self, subject: str | None = None, page: int = 1) -> dict:
        sub = f"/subject/{subject}" if subject else ""
        return self._get(f"list/model/var/lang/ind/domain/{self.domain}{sub}/page/{page}")

    # ---- dynamic data ----
    def periods(self, var: int | str) -> dict:
        """List the available period (th) ids for a variable."""
        return self._get(f"list/model/th/lang/ind/domain/{self.domain}/var/{var}")

    def recent_th(self, var: int | str, years: int = 3) -> str:
        """Semicolon list of the most recent `years` BPS period ids for a variable."""
        payload = self.periods(var)
        data = payload.get("th") or payload.get("data") or []
        rows = data[1] if isinstance(data, list) and len(data) > 1 else data
        ids = [str(r["th_id"]) for r in rows][:years]
        return ";".join(ids) if ids else "0"

    def data(self, var: int | str, th: str = "0") -> dict:
        """
        Raw dynamic-data payload for a variable id (national domain).

        `th` is the BPS period id selection (required by the API): a single id,
        a colon range ("119:126"), or semicolon list ("124;125;126").
        """
        return self._get(f"list/model/data/lang/ind/domain/{self.domain}/var/{var}/th/{th}")


def parse_series(payload: dict, turvar: str = "0", vervar: str | None = None) -> list[tuple]:
    """
    Flatten a BPS dynamic-data payload into a sorted time series.

    Returns a list of (year:int, sub:int, period_label:str, value:float),
    ordered chronologically. Keys in `datacontent` are composite strings:
        vervar + var + turvar + tahun + turtahun
    so we reconstruct them from the id lists in the payload.
    """
    var_list = payload.get("var", []) or payload.get("variabel", [])
    if not var_list:
        return []
    var_id = str(var_list[0]["val"])
    years = {str(y["val"]): y["label"] for y in payload.get("tahun", [])}
    turth = {str(t["val"]): t["label"] for t in payload.get("turtahun", [])}
    vervars = [str(v["val"]) for v in payload.get("vervar", [])]
    if vervar is None:
        # national total is usually the last/own row; fall back to first available
        vervar = vervars[-1] if vervars else "9999"

    content = payload.get("datacontent", {})
    rows: list[tuple] = []
    for yval, ylabel in years.items():
        for tval, tlabel in (turth.items() or {"0": ""}.items()):
            key = f"{vervar}{var_id}{turvar}{yval}{tval}"
            if key in content:
                try:
                    value = float(content[key])
                except (TypeError, ValueError):
                    continue
                label = f"{tlabel} {ylabel}".strip()
                rows.append((int(yval), int(tval), label, value))
    rows.sort(key=lambda r: (r[0], r[1]))
    return rows
