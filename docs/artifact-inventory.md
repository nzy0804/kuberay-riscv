# Artifact inventory

## Python wheels

The [RISC-V wheel release](https://github.com/nzy0804/kuberay-riscv/releases/tag/riscv-wheels-20261111) contains the following CPython 3.11 builds. The published SHA-256 values match the verified build artifacts.

| File | Size (bytes) | SHA-256 |
| --- | ---: | --- |
| `ray-2.52.0-cp311-cp311-linux_riscv64.whl` | 43,602,520 | `b14177588ae8d360b24f210ed2e97fddfcb3de034095ddbfb6d45672dca79d69` |
| `grpcio-1.76.0-cp311-cp311-linux_riscv64.whl` | 7,065,034 | `62c27c56a8ba8183dd44e83f0a9127f42928f958acdffa57bb305b5182c09324` |

The [wheelhouse checksum list](wheelhouse-SHA256SUMS) also covers the base and Serve dependency sets held in separate backups.

## Container images

The following tags and manifest digests were verified on Docker Hub on 2026-11-13. All three images target `linux/riscv64`.

| Image | Manifest digest |
| --- | --- |
| [`niuziyu/ray-riscv:2.52.0`](https://hub.docker.com/r/niuziyu/ray-riscv/tags) | `sha256:a7e6bd7806dfcec4a9d33d4e594a3896d21e28ae5da7cbb76789b2b3b63d2d9c` |
| [`niuziyu/ray-serve-riscv:2.52.0`](https://hub.docker.com/r/niuziyu/ray-serve-riscv/tags) | `sha256:b5f855d284e9c6863fd53bb9bca20b212e338f775493bbe6101bc347ae25ba81` |
| [`niuziyu/kuberay-operator-riscv:v1.5.2`](https://hub.docker.com/r/niuziyu/kuberay-operator-riscv/tags) | `sha256:e195a7638f5b905a083a547b50bdd34778dfc7650eb2b1892fe57d155c367b97` |

See the [Quick Start](../README.md#quick-start) for deployment or [build from source](build-baseline.md) for the pinned revisions and toolchain.
