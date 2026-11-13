# Serve performance findings

The evaluation used a single RISC-V host with a Kubernetes cluster and two Serve replicas. The offered rate was 50 requests/s.

## Replica concurrency comparison

Four 780-second pairs compared `max_ongoing_requests=1` (A) with `2` (B), using the order AB, BA, BA, AB. The B runs completed 156,000 requests with zero errors. The A configuration degraded in three of the four pairs; the median paired improvement in correct throughput was 14.67 requests/s. One A run remained stable.

The three degraded A runs showed increased head CPU usage, CPU throttling, and Router runnable wait. The two-slot runs showed lower values for these signals in the same comparisons.

## 60-minute follow-up

With two slots per replica, 180,000 requests were recorded: 179,995 correct and five HTTP 503 responses, with no client timeouts. Correct throughput was 49.9986 requests/s and successful-request RTT p95 was 14.72 ms. Two short latency spikes were observed; the five 503 responses occurred during the later spike. The zero-error stability target was not met.

An initial two-hour diagnostic attempt stopped during functional acceptance because the instrumentation missed a required event. Its overhead comparison and main run did not start.

## Host scan comparison

On 2026-11-12, a same-host comparison held the request rate at 50 requests/s and the per-replica concurrency limit at 2. It measured three 25-minute windows with automatic `kmemleak` scanning enabled, paused, and restored, in that order.

| Automatic scan | Host CPU pulses | Correct requests/s | Error rate | HTTP 503 / timeouts | Successful RTT p95 |
| --- | ---: | ---: | ---: | ---: | ---: |
| Enabled | 2 | 47.314 | 5.372% | 2,503 / 1,526 | 940.0 ms |
| Paused | 0 | 50.000 | 0% | 0 / 0 | 18.72 ms |
| Restored | 3 | 45.837 | 8.327% | 3,915 / 2,330 | 1,384.7 ms |

Each stage contains 75,000 measured requests. All measured errors occurred within the analysis windows around the five CPU pulses. The reversible comparison supports automatic scanning as a trigger for periodic degradation on this host. Earlier tracing found that median feedback wait rose from about 4 ms to 151 ms during ordinary degradation. Most of the increase occurred while awaiting a streaming object reference and its value. Router scheduling delays, retries and queueing amplified the slowdown. The exact kernel path behind the CPU pulses remains open.

The original run finished with a validation failure because its event checker required body consumption even when a request was accepted after the client timed out and was then cancelled. A corrected checker passed offline replay of 230,205 requests (including warm-up, transitions and the tail) and 280,690 dispatch attempts. The original run status and measured performance totals were preserved.

## Concurrency and sustained load with scanning paused

- **Sustained load:** 287,685 requests completed successfully over 95 minutes 54 seconds, with a successful RTT p95 of 18.99 ms and no detected CPU pulses of the same kind. The head container reached its memory limit and the guard stopped the run before the planned two hours. Page cache from instrumentation logs is a possible contributor to the memory growth.
- **Concurrency comparison:** Four 13-minute windows used per-replica limits of 2, 1, 1 and 2. All 156,000 requests succeeded at 50 requests/s. Successful RTT p95 ranged from 13.92 to 14.08 ms. A limit of 2 reduced head CPU use by about 0.06 cores in both pairs, with the same correct throughput and error rate at this offered load.

Raising the limit from 1 to 2 improved sustained throughput in the original environment. With scanning paused, both limits handled 50 requests/s. These results quantify the effect of host and Serve configuration changes. The scan setting was restored and the cleanup audits passed after the interventions.
