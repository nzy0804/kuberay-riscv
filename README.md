# KubeRay on RISC-V

[English](./README.md) | [简体中文](./README-ZH.md)

Build, deploy, and investigate the performance of Ray and KubeRay on RISC-V.

## Progress

- Built Ray 2.52.0 on RISC-V and adapted Abseil and Boost.Context dependencies.
- Validated Ray Core tasks and actors, object transfer, KubeRay deployment, manual scaling, RayJob, and Serve.
- Improved sustained Serve performance at 50 requests/s by increasing `max_ongoing_requests` from 1 to 2 per replica. The two-slot configuration completed 156,000 requests without errors in four comparison runs; a subsequent 60-minute run completed 180,000 requests with five HTTP 503 responses.

The measurements above used multiple Kubernetes Pods on one RISC-V host.

## Repository

- [`patches/ray/`](./patches/ray/) — Ray build and dependency compatibility patches.
- Build, deployment, and experiment materials are being reviewed for publication.

## Acknowledgments

Built on [Ray](https://github.com/ray-project/ray) and [KubeRay](https://github.com/ray-project/kuberay). Upstream components retain their respective licenses.
