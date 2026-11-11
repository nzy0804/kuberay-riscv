# KubeRay on RISC-V

[English](./README.md) | [简体中文](./README-ZH.md)

Build, deploy, and investigate the performance of Ray and KubeRay on RISC-V.

This repository collects the project's source patches, build and deployment materials, and experiment methodology. Results are based on a single physical RISC-V host running multiple Kubernetes Pods; they should not be interpreted as multi-machine or cross-architecture results.

## Project status

- Ray 2.52.0 was built on RISC-V, with compatibility patches for dependencies including Abseil and Boost.Context.
- Core tasks, actors, object transfer, KubeRay deployment, manual scaling, RayJob, and a basic Serve deployment were validated in the lab.
- At 50 requests/s, experiments showed intermittent Serve degradation. A same-host comparison and a 60-minute follow-up support improved behavior with `max_ongoing_requests=2` per replica; this is not a universal capacity guarantee.
- The planned two-hour verification has **not completed**. Its functional acceptance stopped after an instrumentation event was not observed; the ABBA overhead test and the main run did not start.

The project remains a work in progress. Clean-room reproducibility and cross-architecture comparisons remain to be validated.

## Materials and reproducibility

The repository structure and material inventory are being prepared. Build scripts and Kubernetes manifests from the lab require review and adaptation before use in another environment. Existing experiment data, wheelhouses, and container images require separate backups; a reference in documentation is not a backup.

## Attribution

This work builds on [Ray](https://github.com/ray-project/ray) and [KubeRay](https://github.com/ray-project/kuberay). Upstream components retain their respective licenses.

