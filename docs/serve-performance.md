# Serve performance findings

The initial evaluation used one RISC-V Kubernetes host, two Serve replicas and an offered load of 50 requests/s. The November 24 follow-up tested overload and source changes on the same platform. [ARM64 and RISC-V benchmark rerun](cross-architecture.md)

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

## November 24 configuration comparison

With scanning paused and two replicas, raising `max_ongoing_requests` from 1 to 2 increased median correct throughput from 24.33 to 38.83 requests/s under a 100 requests/s lightweight load. All four pairs improved, with a median paired gain of 60.37%. Median error rates were 74.78% and 60.13%, respectively. At 50 requests/s both configurations served every request, with a 7.00% median paired reduction in successful RTT p95 at the higher limit. All 16 formal windows passed the experiment checks, including restoration and cleanup.

## November 24 source patch

The experimental patch sends an already complete, single-frame HTTP request body of up to 4 KiB with the dispatch. The replica reads that frame directly and uses the existing channel for subsequent messages. In the test workload, every request that acquired a replica slot used the inline body in the patched arm, and the probes recorded zero Proxy body fetches in that arm.

The native RISC-V comparison used Ray 2.52.0, one head-only Proxy, one replica and paused host scanning. Each rate-by-limit combination had six order-balanced pairs of 80-second measurement windows. The table shows results for 100 offered requests/s, using the median across the six windows per arm.

| Per-replica limit | Correct throughput (req/s) | Error rate | Successful RTT p95 | Replica slot hold p95 |
| ---: | ---: | ---: | ---: | ---: |
| 1 | 14.86 → 30.62 | 83.89% → 67.53% | 4,826.78 → 4,756.50 ms | 117.12 → 63.91 ms |
| 2 | 28.69 → 100.00 | 69.54% → 0% | 4,674.43 → 13.24 ms | 116.00 → 2.59 ms |

Each pair improved correct throughput at both limits. The median paired gains were 106.75% and 248.49%, respectively. At limit 2, 47,998 of the 48,000 requests completed correctly during measurement and the remaining two completed correctly during drain. At 10 offered requests/s every request succeeded in both arms. Cleanup and scan restoration were verified.

The result applies to the measured small JSON POST workload with diagnostics enabled in both arms. The prototype requires matching support in the Proxy and replica. Large or streamed uploads, other replica topologies and other architectures still need validation. The published images contain the original implementation.

## Other source candidates

| Candidate | Measured outcome on RISC-V |
| --- | --- |
| Untimed streaming feedback wait | Removed an extra async task in the pending path. In 20 paired component tests, median feedback latency fell by 4.45% across pairs. Tail latency, batch time and CPU varied between batches. |
| Replica ASGI response queue | Reused the queue event to await producer completion. Thread CPU per response fell 31.8%–46.4% in the isolated queue tests. Neither HTTP workload met the end-to-end replica CPU target. |
| Router warning coalescing | Reduced repeated warning calls. Both concurrency limits missed the throughput target in the single-replica rerun. |
