# Project status

Updated 2026-11-24. The project has validated native RISC-V builds and Kubernetes deployment, completed the ARM64 and RISC-V benchmark rerun, and measured Serve configuration changes and source patch candidates on RISC-V.

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

The November 23–24 rerun completed all 255 formal B1–B6 rounds on each host, with Ray Core checks before and after each stage. It completed the B5 and B6 coverage left partial by earlier ARM control-plane interruptions. B6 covers short windows for sampling overhead and resource diagnosis. The runs record their respective software, network and host conditions. [Cross-platform results and measurement scope](cross-architecture.md)

On RISC-V, raising the per-replica concurrency limit improved throughput under overload. A separate single-replica A/B test found a larger improvement from passing complete small HTTP request bodies with the dispatch, reducing time spent holding replica slots. The source patch was tested in isolated processes and the result applies to that workload. [Configuration and source patch results](serve-performance.md#november-24-source-patch)

## Remaining validation

- Run the public build scripts from a clean native RISC-V environment and exercise the public Quick Start on a RISC-V Kubernetes cluster.
- Extend the experimental request-body optimization measurements to other request sizes, streaming uploads, replica topologies and architectures.
- The planned two-hour Serve stability run with scanning paused reached 95 minutes 54 seconds before the head container memory guard stopped it.
