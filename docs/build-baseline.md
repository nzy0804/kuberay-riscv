# RISC-V build baseline

The recorded build used Ray 2.52.0 at `9527a555280fb9837ce73dabf01559c20656a456`, KubeRay v1.5.2 at `9f65eca1d6226d20f9e7c340f2af27cc4a1c9985`, Python 3.11.6, Bazel 6.5.0 and GCC 14.3.1 on openEuler RISC-V.

## Source patches

- [`abseil-cpp-riscv-no-rdcycle.patch`](../patches/ray/dependencies/abseil-cpp-riscv-no-rdcycle.patch): use the fallback clock path instead of the RISC-V cycle counter.
- [`boost-context-riscv64.patch`](../patches/ray/dependencies/boost-context-riscv64.patch): select the RISC-V context-switch assembly sources.
- [`ray-source-complete.example.patch`](../patches/ray/ray-source-complete.example.patch): example of the associated Ray source changes. The recorded build's local Python path is replaced with `/opt/ray-build-venv/bin/python`; adapt it to the build environment before applying the patch.

## Image recipes

[`images/Dockerfile.ray`](../images/Dockerfile.ray) requires an explicitly supplied RISC-V base image plus the wheelhouse and dashboard build assets in its build context. [`images/Dockerfile.operator`](../images/Dockerfile.operator) packages a separately built KubeRay operator binary.

The original wheels, source checkout, container image archives, and experimental evidence are retained separately. They are not included in this Git repository yet.
