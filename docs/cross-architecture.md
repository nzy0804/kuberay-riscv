# ARM64 and RISC-V benchmark rerun

The November 23–24, 2026 rerun completed 255 of 255 formal rounds on each host. Both environments ran Ray 2.52.0 and KubeRay v1.5.2 on a single physical host with one head and two worker Pods. Ray Core checks before and after each stage verified tasks, actors and cross-worker object integrity.

| Benchmark | Formal rounds per host | Metric | ARM64 | RISC-V |
| --- | ---: | --- | ---: | ---: |
| B1 Cluster lifecycle | 10 | From creation response to correct results on both workers, with pre-cached images | 31.294 s | 23.610 s |
| B2 Worker registration | 10 | From scale-up response to a correct result on the added worker | 30.324 s | 20.387 s |
| B3-S0 Tasks and actors | 70 | Resource release to task return in the `DEFAULT` fragmentation case | 73.714 ms | 100.665 ms |
| B4 Object transfer | 120 | First `ray.get` of a 64 MiB object across worker Pods, B→A with two transfers in flight | 105.480 ms | 148.758 ms |
| B5 Serve requests | 30 | Correct throughput at 100 offered requests/s for lightweight HTTP requests | 100.000 req/s | 24.667 req/s |
| B6 Serve sampling | 15 | Ratio of successful-request RTT p95 with extended versus basic sampling at 50 offered requests/s | 1.018× | 1.005× |

The table reports round medians for the named cases, or the median of five ratios for B6. B1 deletion and B2 scale-down recovery were faster on the ARM64 host. ARM64 also had higher throughput and lower p95 latency in all 12 regular B3-S0 task and actor groups. B4 measures traffic between Pods on one host. First and cached reads are reported separately, with SHA-256 timed after each read.

In B5, both hosts completed all six load levels. At 100 offered requests/s for lightweight requests, the median error rate was 0% on ARM64 and 74.475% on RISC-V. At 50 offered requests/s, the median successful RTT p95 was 6.462 ms on ARM64 and 16.402 ms on RISC-V, reversing the ordering in the earlier partial comparison. Correct throughput counts responses received within the measurement window. The error rate accounts for correct responses received during the drain period.

Both hosts passed the B6 sampling-overhead thresholds in the rerun. The ARM64 p95 ratio of 20.060× in the earlier partial comparison did not recur. B6 uses 30-second sampling-overhead windows and 60-second overload windows. An audit found two RISC-V extended samples attributed to the head Pod whose processes belonged to the host root cgroup. These samples were excluded from process attribution. The independent recomputation matched the reported request metrics and container-level counters.

## Comparison conditions

The runs were staged separately and retain their own host, OS, network and image settings. B1, B2, B5 and B6 used the same benchmark code across the two hosts. ARM64 used the versions from its earlier pilots for B3-S0 and B4, and RISC-V used updated frozen versions. These measurements compare the two complete deployments.

The rerun used staged entries to pause automatic `kmemleak` scanning on the RISC-V host during pilot and formal stages, including Core checks, warm-up and drain where applicable. The scanner thread was checked before measurement, and pause and restoration readbacks were archived. The formal stages recorded 2,437 host samples without the scan thread and six verified restorations. Earlier B3-S0 and B4 measurements retain their original conditions, which included automatic scanning and a Hadoop background workload.

A separate same-host B4 check isolated the scan condition for 64 MiB A→B reads with one transfer in flight. The median of first-read round medians was 149.821 ms with the scan active and 89.945 ms with it paused. The SHA-256 medians were 565.134 ms and 563.687 ms.
