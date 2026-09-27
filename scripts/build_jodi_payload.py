#!/usr/bin/env python3
"""Build a small, auditable JODI crude-oil payload from the official bulk file."""

from __future__ import annotations

import csv
import hashlib
import io
import json
import sys
import urllib.request
import zipfile
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path

SOURCE_URL = "https://www.jodidata.org/_resources/files/downloads/oil-data/world_primary_csv.zip?iid=24"
ARCHIVE_MEMBER = "NewProcedure_Primary_CSV.csv"
HISTORY_MONTHS = 24
COUNTRIES = {
    "AE": "United Arab Emirates",
    "BR": "Brazil",
    "CA": "Canada",
    "CN": "China",
    "IN": "India",
    "IQ": "Iraq",
    "KW": "Kuwait",
    "KZ": "Kazakhstan",
    "MX": "Mexico",
    "NG": "Nigeria",
    "NO": "Norway",
    "RU": "Russia",
    "SA": "Saudi Arabia",
    "US": "United States",
}
FLOW_UNITS = {
    "INDPROD": "KBD",
    "TOTIMPSB": "KBD",
    "TOTEXPSB": "KBD",
    "REFINOBS": "KBD",
    "CLOSTLV": "KBBL",
    "STOCKCH": "KBBL",
}


def download() -> bytes:
    request = urllib.request.Request(
        SOURCE_URL,
        headers={
            "Accept": "application/zip,application/octet-stream;q=0.9,*/*;q=0.8",
            "User-Agent": "CrudeIntelligenceIndia/1.0 (+https://crudeintel.in)",
        },
    )
    with urllib.request.urlopen(request, timeout=180) as response:
        if response.status != 200:
            raise RuntimeError(f"JODI download failed with HTTP {response.status}")
        body = response.read()
    if len(body) < 100_000 or body[:2] != b"PK":
        raise RuntimeError("JODI returned an invalid or unexpectedly small ZIP archive")
    return body


def parse(archive_bytes: bytes) -> tuple[list[dict[str, object]], str]:
    selected: dict[tuple[str, str, str], list[dict[str, object]]] = defaultdict(list)
    max_period = ""
    with zipfile.ZipFile(io.BytesIO(archive_bytes)) as archive:
        if ARCHIVE_MEMBER not in archive.namelist():
            raise RuntimeError(f"JODI archive does not contain {ARCHIVE_MEMBER}")
        with archive.open(ARCHIVE_MEMBER) as binary:
            text = io.TextIOWrapper(binary, encoding="utf-8-sig", newline="")
            reader = csv.DictReader(text)
            required = {
                "REF_AREA", "TIME_PERIOD", "ENERGY_PRODUCT", "FLOW_BREAKDOWN",
                "UNIT_MEASURE", "OBS_VALUE", "ASSESSMENT_CODE",
            }
            if not required.issubset(reader.fieldnames or []):
                raise RuntimeError("JODI CSV schema does not match the controlled import contract")
            for row in reader:
                if row["ENERGY_PRODUCT"] != "CRUDEOIL":
                    continue
                period = row["TIME_PERIOD"]
                if period > max_period:
                    max_period = period
                country = row["REF_AREA"]
                flow = row["FLOW_BREAKDOWN"]
                unit = row["UNIT_MEASURE"]
                if country not in COUNTRIES or FLOW_UNITS.get(flow) != unit:
                    continue
                try:
                    value = float(row["OBS_VALUE"])
                except (TypeError, ValueError):
                    continue
                assessment = row["ASSESSMENT_CODE"]
                if assessment not in {"1", "2", "3"}:
                    continue
                selected[(country, flow, unit)].append(
                    {
                        "countryCode": country,
                        "countryName": COUNTRIES[country],
                        "period": period,
                        "flowCode": flow,
                        "unit": unit,
                        "value": value,
                        "assessmentCode": assessment,
                    }
                )
    observations: list[dict[str, object]] = []
    for values in selected.values():
        values.sort(key=lambda item: str(item["period"]))
        observations.extend(values[-HISTORY_MONTHS:])
    observations.sort(
        key=lambda item: (
            str(item["countryCode"]), str(item["flowCode"]),
            str(item["unit"]), str(item["period"]),
        )
    )
    if not max_period or len(observations) < 500:
        raise RuntimeError(f"JODI filter produced an implausible payload ({len(observations)} observations)")
    return observations, max_period


def main() -> None:
    output = Path(sys.argv[1] if len(sys.argv) > 1 else "jodi-payload.json")
    archive_bytes = download()
    observations, max_period = parse(archive_bytes)
    payload = {
        "schemaVersion": "jodi-oil-v1",
        "sourceUrl": SOURCE_URL,
        "downloadedAt": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
        "sourceSha256": hashlib.sha256(archive_bytes).hexdigest(),
        "maxPeriod": max_period,
        "historyMonths": HISTORY_MONTHS,
        "observations": observations,
    }
    encoded = json.dumps(payload, separators=(",", ":"), ensure_ascii=True).encode("utf-8")
    if len(encoded) > 2_000_000:
        raise RuntimeError(f"JODI payload exceeds the 2 MB contract ({len(encoded)} bytes)")
    output.write_bytes(encoded)
    print(json.dumps({
        "output": str(output),
        "bytes": len(encoded),
        "observations": len(observations),
        "maxPeriod": max_period,
        "sourceSha256": payload["sourceSha256"],
    }))


if __name__ == "__main__":
    main()
