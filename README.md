# KubeRay on RISC-V

[English](./README.md) | [简体中文](./README-ZH.md)

Build, deploy, and investigate the performance of Ray and KubeRay on RISC-V.

## Quick Start

Use a Kubernetes test cluster with schedulable Linux `riscv64` nodes, `kubectl`, Helm 3, and permission to install KubeRay's CRDs. Allow about 5 CPUs and 9 GiB of allocatable capacity for the operator, one head, and one worker. The nodes need access to Docker Hub. Run the commands below from the repository root in a Bash shell.

### 1. Install the operator

Check your context before deploying. Use a fresh `ray-riscv-demo` namespace on a test cluster where no other operator watches that namespace. The [Helm values](./deploy/operator-values.yaml) scope the operator to the release namespace and select the published RISC-V image.

```bash
kubectl config current-context
kubectl get nodes -l kubernetes.io/arch=riscv64 -L kubernetes.io/os
helm repo add kuberay https://ray-project.github.io/kuberay-helm/
helm repo update kuberay
helm install kuberay-riscv kuberay/kuberay-operator --version 1.5.2 \
  --namespace ray-riscv-demo --create-namespace \
  -f deploy/operator-values.yaml --wait --timeout 10m
kubectl wait --for=condition=Established crd/rayclusters.ray.io --timeout=60s
```

### 2. Deploy the RayCluster

Use the [base example](./deploy/raycluster/raycluster.yaml) for Ray Core. To use the Ray Serve image on both Pods, replace `deploy/raycluster` with `deploy/raycluster-serve` in the apply command.

```bash
kubectl -n ray-riscv-demo apply -k deploy/raycluster
kubectl -n ray-riscv-demo wait --for=condition=RayClusterProvisioned \
  raycluster/ray-riscv-quickstart --timeout=10m
kubectl -n ray-riscv-demo get pods -l ray.io/cluster=ray-riscv-quickstart
```

### 3. Run the smoke test

The [test](./examples/quickstart_smoke.py) connects from the head and checks that a RISC-V worker executes a Ray task. Both image variants support this Ray Core check.

```bash
HEAD_POD=$(kubectl -n ray-riscv-demo get pod \
  -l 'ray.io/cluster=ray-riscv-quickstart,ray.io/node-type=head' \
  -o jsonpath='{.items[0].metadata.name}')
kubectl -n ray-riscv-demo exec -i "$HEAD_POD" -c ray-head -- python - \
  < examples/quickstart_smoke.py
```

Expected final line: `PASS: Ray 2.52.0 executed 7^2 = 49 on a riscv64 worker`. If a Pod stays Pending or fails to pull an image, check its events with `kubectl -n ray-riscv-demo describe pod <pod-name>`.

### 4. Clean up

Delete the RayCluster while the operator is still running so it can complete cleanup. Helm retains the cluster-wide CRDs.

```bash
kubectl -n ray-riscv-demo delete raycluster ray-riscv-quickstart --wait --timeout=5m &&
helm uninstall kuberay-riscv -n ray-riscv-demo --wait --timeout 5m &&
kubectl delete namespace ray-riscv-demo --wait --timeout=5m
```

## Progress

- Built Ray 2.52.0 on RISC-V and adapted Abseil and Boost.Context dependencies.
- Validated Ray Core tasks and actors, object transfer, KubeRay deployment, manual scaling, RayJob, and Serve.
- Improved sustained Serve performance at 50 requests/s by increasing `max_ongoing_requests` from 1 to 2 per replica. The two-slot configuration completed 156,000 requests without errors in four comparison runs; a subsequent 60-minute run completed 180,000 requests with five HTTP 503 responses.

The measurements above used multiple Kubernetes Pods on one RISC-V host.

## Repository

- [Build from source](./docs/build-baseline.md) — Bazel, the Ray wheel and the KubeRay operator.
- [`patches/ray/`](./patches/ray/) — Ray build and dependency compatibility patches.
- [`images/`](./images/) — Ray and operator image recipes and dashboard dependencies.
- [`deploy/`](./deploy/) — Helm values and RayCluster examples.
- [`examples/`](./examples/) — smoke tests and validation drivers.
- [`docs/serve-performance.md`](./docs/serve-performance.md) — verified Serve performance findings.
- Further build, deployment, and experiment materials are being reviewed for publication.

## Acknowledgments

Built on [Ray](https://github.com/ray-project/ray) and [KubeRay](https://github.com/ray-project/kuberay). Upstream components retain their respective licenses.
