# Project status

Updated 2026-11-13 from the RISC-V build and validation records. The functional and performance measurements used Kubernetes Pods on a single physical RISC-V host.

## Build and deployment

Ray 2.52.0 and KubeRay v1.5.2 have native RISC-V build and deployment evidence. The repository provides [build scripts](build-baseline.md), [released wheels and images](artifact-inventory.md), and a [Kubernetes Quick Start](../README.md#quick-start). Lab validation covered task and actor execution, object integrity, manual worker scaling, a successful RayJob, and RayService creation, update, and removal.

## Benchmark coverage

| Area | Completed coverage |
| --- | --- |
| B1 Cluster lifecycle | Creation through first successful task, deletion and recreation with cached images and a ready operator |
| B2 Worker registration | Registration, first task on the added worker, and recovery during manual 2 → 3 → 2 scaling |
| B3 Tasks and actors | Default and spread scheduling, fixed workloads, concurrency, resource fragmentation and contention between long and short tasks |
| B4 Object transfer | Same-worker and cross-worker Pod reads, first and cached reads, both directions, and concurrent transfers |
| B5 Serve requests | Throughput, latency, errors and timeouts for a two-replica Serve deployment |
| B6 Sustained load and resource use | Host CPU pulses, head CPU throttling, Router wait and the effect of per-replica concurrency. [Results and run limits](serve-performance.md) |

## Remaining validation

- Run the public build scripts from a clean native RISC-V environment and exercise the public Quick Start on a RISC-V Kubernetes cluster.
- Run the planned Core and B3 comparison on a native x86_64 or aarch64 reference host with matched workloads and resource settings. The comparison is at the planning stage.
- Record the head container memory breakdown and a full two-hour stability result if required for final acceptance. The latest long run stopped at the memory guard after 95 minutes 54 seconds.
