# Build from source on RISC-V

The recorded build used Ray 2.52.0 at `9527a555280fb9837ce73dabf01559c20656a456`, KubeRay v1.5.2 at `9f65eca1d6226d20f9e7c340f2af27cc4a1c9985`, Python 3.11.6, Bazel 6.5.0 and GCC 14.3.1 on openEuler RISC-V.

## Prerequisites

Use a native Linux `riscv64` host. For Bazel and Ray, install JDK 11, GCC and G++, CPython 3.11 with venv and development headers, and the host build tools and development libraries. The openEuler build used Make, CMake, pkgconf, zlib and OpenSSL development headers. Install Bash, Git, curl, tar, unzip, patch, coreutils and file. The operator build downloads Go 1.24.6 itself. Builds need network access for upstream sources and dependencies, and disk space for the source trees and build caches.

Run the following from the repository root with a fresh build directory. `BUILD_ROOT` can be omitted to use `.build-riscv` in the checkout. Set `BUILD_JOBS` to match the host's resources. `PYTHON` and `JAVA_HOME` can select a local CPython 3.11 and JDK 11.

```bash
export BUILD_ROOT="$PWD/.build-riscv"
export BUILD_JOBS=8
bash build/bootstrap-bazel.sh
bash build/build-ray-wheel.sh
bash build/build-kuberay-operator.sh
```

| Script | Output under `BUILD_ROOT` |
| --- | --- |
| [Bootstrap Bazel](../build/bootstrap-bazel.sh) | `tools/bin/bazel` (Bazel 6.5.0) |
| [Build the Ray wheel](../build/build-ray-wheel.sh) | `artifacts/wheels/ray-2.52.0-cp311-cp311-linux_riscv64.whl` |
| [Build the KubeRay operator](../build/build-kuberay-operator.sh) | `artifacts/manager` (Linux RISC-V executable) |

The operator can be built on its own. Each source checkout is created at the pinned version and checked against the commit above. To repeat a stage after its source directory has been created, use a fresh `BUILD_ROOT` for that build. The Ray build checks that the wheel contains `_raylet.so`, `gcs_server` and `raylet`. Ray and operator scripts print SHA-256 checksums for their outputs.

## Source patches

- [`abseil-cpp-riscv-no-rdcycle.patch`](../patches/ray/dependencies/abseil-cpp-riscv-no-rdcycle.patch): use the fallback clock path instead of the RISC-V cycle counter.
- [`boost-context-riscv64.patch`](../patches/ray/dependencies/boost-context-riscv64.patch): select the RISC-V context-switch assembly sources.
- [`ray-source-complete.example.patch`](../patches/ray/ray-source-complete.example.patch): the build script substitutes its Python 3.11 virtual environment path, checks the patch against the pinned Ray checkout, then applies it once. The patch switches the Bazel Python references, adds both dependency patches and registers them with Bazel. The standalone dependency patches are references for reviewing those changes.

Bazel is bootstrapped first from the official 6.5.0 distribution archive. The script already uses the corrected version check, so the [historical bootstrap patch](../patches/ray/bootstrap-version-check.patch) is a reference. KubeRay builds from the pinned v1.5.2 source without a source patch.

## Image recipes

Use a staging directory as the build context for [`images/Dockerfile.operator`](../images/Dockerfile.operator):

```bash
mkdir -p "$BUILD_ROOT/operator-image"
cp "$BUILD_ROOT/artifacts/manager" "$BUILD_ROOT/operator-image/"
docker build --platform linux/riscv64 -f images/Dockerfile.operator \
  -t kuberay-operator-riscv:local "$BUILD_ROOT/operator-image"
```

[`images/Dockerfile.ray`](../images/Dockerfile.ray) takes a RISC-V base image via `BASE_IMAGE`. Its build context needs the newly built Ray wheel and the dependency wheels in `wheelhouse/`, `requirements-dashboard.txt` from `images/`, and the dashboard frontend in `dashboard-build/`. The source build above produces the Ray Core wheel. See the [wheelhouse checksums](wheelhouse-SHA256SUMS) for the dependency set from the recorded build. Published images and wheels are available through the [Quick Start](../README.md#quick-start) and [GitHub Release](https://github.com/nzy0804/kuberay-riscv/releases/tag/riscv-wheels-20261111).

The lab verified the original native build and packaging flow. The repository entry points have been checked for shell syntax and patch application. A fresh end-to-end native build of these scripts remains to be run. Some upstream Python dependencies are resolved during the build, so artifact checksums can differ between builds.
