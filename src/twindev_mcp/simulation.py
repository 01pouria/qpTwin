# Copyright 2026 Pouriya Khalilian
# SPDX-License-Identifier: Apache-2.0

"""Bounded discrete-event M/M/c proxy for API and inference request queues.

Requests are Poisson and service duration is exponential by assumption.
This is an intentionally limited model, not a faithful GPU inference simulator.
"""
from __future__ import annotations
import heapq
import math
import random
from dataclasses import dataclass

@dataclass(frozen=True)
class Scenario:
    arrival_rps: float
    service_rps_per_replica: float
    replicas: int
    duration_seconds: int = 300
    queue_limit: int = 1000
    failed_replicas: int = 0
    seed: int = 42
    slo_p95_ms: float = 1200

    def __post_init__(self):
        for value in (self.arrival_rps,self.service_rps_per_replica,self.slo_p95_ms):
            if type(value) not in (int,float) or not math.isfinite(value):
                raise ValueError("Rates and SLO must be finite numbers")
        if type(self.replicas) is not int or type(self.duration_seconds) is not int or type(self.failed_replicas) is not int or type(self.queue_limit) is not int or type(self.seed) is not int:
            raise ValueError("Replicas, duration, failures, queue and seed must be integers")
        if not 0 < self.arrival_rps <= 20000: raise ValueError("arrival_rps must be between 0 and 20000")
        if not 0 < self.service_rps_per_replica <= 20000: raise ValueError("service_rps_per_replica must be between 0 and 20000")
        if not 1 <= self.replicas <= 1024: raise ValueError("replicas out of range")
        if not 0 <= self.failed_replicas < self.replicas: raise ValueError("failed_replicas must leave at least one replica")
        if not 1 <= self.duration_seconds <= 3600: raise ValueError("duration_seconds out of range")
        if self.arrival_rps * self.duration_seconds > 100_000: raise ValueError("Simulation exceeds 100000 expected arrivals")
        if not 0 <= self.queue_limit <= 100_000: raise ValueError("queue_limit out of range")
        if not 0 < self.slo_p95_ms <= 600_000: raise ValueError("slo_p95_ms out of range")


def _percentile(values: list[float], p: float) -> float | None:
    if not values: return None
    vs = sorted(values)
    idx = (len(vs)-1) * p
    i = int(idx)
    return vs[i] + (vs[min(i+1,len(vs)-1)] - vs[i])*(idx-i)


def simulate(s: Scenario) -> dict:
    r = random.Random(s.seed)
    capacity = s.replicas - s.failed_replicas
    available = [0.0] * capacity
    heapq.heapify(available)
    waiting_start_times = []
    end_times = []
    response_ms = []
    queue_wait_ms = []
    busy_seconds = 0.0
    max_queue = 0
    blocked = arrivals = 0
    t = 0.0
    while True:
        t += r.expovariate(s.arrival_rps)
        if t >= s.duration_seconds: break
        arrivals += 1
        while waiting_start_times and waiting_start_times[0] <= t:
            heapq.heappop(waiting_start_times)
        # Queue length is requests not started yet. Each replica reserves service slots.
        earliest = heapq.heappop(available)
        start = max(t, earliest)
        if start > t and len(waiting_start_times) >= s.queue_limit:
            blocked += 1
            heapq.heappush(available, earliest)
            continue
        service_time = r.expovariate(s.service_rps_per_replica)
        end = start + service_time
        heapq.heappush(available, end)
        if start > t:
            heapq.heappush(waiting_start_times, start)
        max_queue = max(max_queue, len(waiting_start_times))
        queue_wait_ms.append((start-t)*1000)
        response_ms.append((end-t)*1000)
        end_times.append(end)
        busy_seconds += max(0.0, min(end, s.duration_seconds) - min(max(start, 0.0), s.duration_seconds))
    accepted = arrivals - blocked
    p95 = _percentile(response_ms, 0.95)
    completions = sum(x <= s.duration_seconds for x in end_times)
    return {
        "assumptions": "Poisson arrivals, iid exponential service time; replicas are homogeneous; fixed failures throughout scenario; finite FIFO queue",
        "input": s.__dict__, "arrivals": arrivals, "accepted": accepted, "rejected": blocked,
        "rejection_rate": round(blocked/arrivals, 5) if arrivals else 0.0,
        "completed_within_window": completions,
        "throughput_rps": round(completions/s.duration_seconds, 3),
        "effective_replicas": capacity, "offered_load_ratio": round(s.arrival_rps/(capacity*s.service_rps_per_replica),4),
        "estimated_utilization": round(min(1.0,busy_seconds/(capacity*s.duration_seconds)),4),
        "max_waiting_queue": max_queue,
        "mean_latency_ms": round(sum(response_ms)/len(response_ms),2) if response_ms else None,
        "p50_latency_ms": round(_percentile(response_ms, .5),2) if response_ms else None,
        "p95_latency_ms": round(p95,2) if p95 is not None else None,
        "p95_queue_wait_ms": round(_percentile(queue_wait_ms,.95),2) if queue_wait_ms else None,
        "meets_p95_slo": p95 is not None and p95 <= s.slo_p95_ms,
        "warning": "Synthetic probabilistic scenario, not a production guarantee. Calibrate with observed traffic/service distributions.",
    }


def compare(base: Scenario, candidate: Scenario) -> dict:
    a, b = simulate(base), simulate(candidate)
    p95_a, p95_b = a["p95_latency_ms"], b["p95_latency_ms"]
    return {"baseline": a, "candidate": b, "difference": {
        "p95_latency_ms": round(p95_b - p95_a,2) if p95_a is not None and p95_b is not None else None,
        "rejection_rate": round(b["rejection_rate"]-a["rejection_rate"],5),
        "throughput_rps": round(b["throughput_rps"]-a["throughput_rps"],3)
    }, "caution": "Use comparable seeds and observed parameter distributions before architectural decisions."}
