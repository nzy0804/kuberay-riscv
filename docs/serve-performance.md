# Serve performance findings

The evaluation used a single RISC-V host with a Kubernetes cluster and two Serve replicas. The offered rate was 50 requests/s.

## Replica concurrency comparison

Four 780-second pairs compared `max_ongoing_requests=1` (A) with `2` (B), using the order AB, BA, BA, AB. The B runs completed 156,000 requests with zero errors. The A configuration degraded in three of the four pairs; the median paired improvement in correct throughput was 14.67 requests/s. One A run remained stable.

The three degraded A runs showed increased head CPU usage, CPU throttling, and Router runnable wait. The two-slot runs showed lower values for these signals in the same comparisons.

## 60-minute follow-up

With two slots per replica, 180,000 requests were recorded: 179,995 correct and five HTTP 503 responses, with no client timeouts. Correct throughput was 49.9986 requests/s and successful-request RTT p95 was 14.72 ms. Two short latency spikes were observed; the five 503 responses occurred during the later spike. The zero-error stability target was not met.

These measurements establish improvement in the tested environment while leaving short-lived stalls for further investigation. The later two-hour diagnostic run did not start: its functional acceptance stopped when an instrumentation event was not observed.
