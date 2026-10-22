# Copyright 2026 Pouriya Khalilian
# SPDX-License-Identifier: Apache-2.0

"""Privacy-preserving *aggregate* CSV input; no log/prompt capture."""
from __future__ import annotations
import csv
import io
import statistics
from .security import Workspace


def calibrate(ws: Workspace, csv_path: str, interval_seconds: float = 60.0) -> dict:
    if not 0.1 <= interval_seconds <= 86400: raise ValueError("Invalid sampling interval")
    text = ws.text(csv_path)
    rows = list(csv.DictReader(io.StringIO(text)))
    if not rows or len(rows) > 10000: raise ValueError("Telemetry CSV must contain 1-10000 rows")
    required = {"request_count", "mean_service_ms", "error_count"}
    if not required.issubset(set(rows[0])): raise ValueError("Expected CSV headers: request_count,mean_service_ms,error_count")
    count, failures, weighted = 0,0,0.0
    rates = []
    for row in rows:
        try:
            n, err, ms = int(row["request_count"]), int(row["error_count"]), float(row["mean_service_ms"])
        except (ValueError, TypeError): raise ValueError("Telemetry contains invalid numeric values") from None
        if n < 0 or err < 0 or err > n or not 0 < ms < 1e7:
            raise ValueError("Telemetry contains impossible count or duration")
        count += n
        failures += err
        weighted += n*ms
        rates.append(n/interval_seconds)
    mean_ms = weighted/count if count else None
    return {"samples":len(rows), "requests":count, "errors": failures,
            "observed_error_rate":round(failures/count,5) if count else None,
            "estimated_arrival_rps":round(count/(len(rows)*interval_seconds),4),
            "peak_interval_rps":round(max(rates),4),
            "mean_service_ms":round(mean_ms,3) if mean_ms is not None else None,
            "estimated_service_rps_per_replica":round(1000/mean_ms,4) if mean_ms else None,
            "arrival_rate_cv":round(statistics.pstdev(rates)/statistics.mean(rates),4) if len(rates)>1 and statistics.mean(rates) else None,
            "limitations":"Aggregated averages cannot identify queueing distribution, per-replica contention or causality. Do not infer failure probability from a short sample.",
            "privacy":"Only aggregate counts and timings parsed; raw telemetry rows are not echoed."}
