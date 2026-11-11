# KubeRay on RISC-V

[English](./README.md) | [简体中文](./README-ZH.md)

Build, deploy, and investigate the performance of Ray and KubeRay on RISC-V.

## Highlights

- Native RISC-V builds of Ray 2.52.0, with Abseil and Boost.Context compatibility patches.
- Kubernetes deployment and validation of Ray Core, RayJob, Serve, manual scaling, and object transfer.
- Performance investigations of Serve routing, feedback, and scheduling at 50 requests/s.

## Progress

Experiments use a single physical RISC-V host with multiple Kubernetes Pods. Same-host comparisons and a 60-minute follow-up showed improved sustained behavior with `max_ongoing_requests=2` per replica.

A two-hour verification is in preparation. Its first functional acceptance stopped when a probe event was not observed; the overhead comparison and main run are pending.

## Materials

The repository is being organized around source patches, build and deployment materials, experiment code, and results. Large assets, including wheels, container images, and raw measurements, are maintained separately.

## Acknowledgments

Built on [Ray](https://github.com/ray-project/ray) and [KubeRay](https://github.com/ray-project/kuberay). Upstream components retain their respective licenses.
