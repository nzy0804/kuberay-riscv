# RISC-V 上的 KubeRay

[English](./README.md) | [简体中文](./README-ZH.md)

在 RISC-V 环境中构建、部署 Ray 和 KubeRay，并研究性能瓶颈。

## 快速开始

准备一个 Kubernetes 测试集群，至少有可调度的 Linux `riscv64` 节点。需要 `kubectl`、Helm 3，以及安装 KubeRay CRD 的权限。operator、一个 head 和一个 worker 共需约 5 核 CPU 和 9 GiB 可分配内存，节点需能访问 Docker Hub。在仓库根目录用 Bash 执行以下命令。

### 1. 安装 operator

部署前检查 Kubernetes context。在测试集群中使用新建的 `ray-riscv-demo` 命名空间，并确认没有其他 operator 监听它。[Helm 配置](./deploy/operator-values.yaml)会把 operator 的监听范围限定到该命名空间，并使用已发布的 RISC-V 镜像。

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

### 2. 部署 RayCluster

[基础示例](./deploy/raycluster/raycluster.yaml)使用 Ray Core 镜像。如果要让两个 Pod 都使用 Ray Serve 镜像，把 apply 命令中的 `deploy/raycluster` 改为 `deploy/raycluster-serve`。

```bash
kubectl -n ray-riscv-demo apply -k deploy/raycluster
kubectl -n ray-riscv-demo wait --for=condition=RayClusterProvisioned \
  raycluster/ray-riscv-quickstart --timeout=10m
kubectl -n ray-riscv-demo get pods -l ray.io/cluster=ray-riscv-quickstart
```

### 3. 运行冒烟测试

[冒烟脚本](./examples/quickstart_smoke.py)从 head 连接集群，确认一个 RISC-V worker 能执行 Ray 任务。两种镜像均可运行此项 Ray Core 检查。

```bash
HEAD_POD=$(kubectl -n ray-riscv-demo get pod \
  -l 'ray.io/cluster=ray-riscv-quickstart,ray.io/node-type=head' \
  -o jsonpath='{.items[0].metadata.name}')
kubectl -n ray-riscv-demo exec -i "$HEAD_POD" -c ray-head -- python - \
  < examples/quickstart_smoke.py
```

预期最后一行为 `PASS: Ray 2.52.0 executed 7^2 = 49 on a riscv64 worker`。如果 Pod 一直 Pending 或镜像拉取失败，用 `kubectl -n ray-riscv-demo describe pod <pod-name>` 查看事件。

### 4. 清理资源

先在 operator 仍运行时删除 RayCluster，以便它完成清理。Helm 会保留集群级 CRD。

```bash
kubectl -n ray-riscv-demo delete raycluster ray-riscv-quickstart --wait --timeout=5m &&
helm uninstall kuberay-riscv -n ray-riscv-demo --wait --timeout 5m &&
kubectl delete namespace ray-riscv-demo --wait --timeout=5m
```

## 当前进展

- 完成 Ray 2.52.0 和 KubeRay v1.5.2 的 RISC-V 原生构建，已发布容器镜像以及 Ray、grpcio 的 Python 3.11 wheel。
- 已验证 Ray Core、RayCluster、手动扩缩容、RayJob 和 RayService，并在单台 RISC-V 宿主机上完成六类基准的初步测量。
- 在 50 req/s 下，可逆对照发现宿主机 `kmemleak` 自动扫描会触发 Serve 周期性退化。暂停扫描后，每副本并发上限为 1 和 2 的对照窗口均跑满 50 req/s，且零错误。[Serve 性能结果](./docs/serve-performance.md)

六类基准的覆盖范围和待验证事项见[项目进展](./docs/project-status.md)。

## 仓库目录

- [源码构建](./docs/build-baseline.md)：构建 Bazel、Ray wheel 和 KubeRay operator。
- [`patches/ray/`](./patches/ray/)：Ray 构建和依赖适配补丁。
- [`images/`](./images/)：Ray 和 operator 的镜像构建文件及 dashboard 依赖。
- [`deploy/`](./deploy/)：Helm 配置和 RayCluster 示例。
- [`examples/`](./examples/)：冒烟测试和验证脚本。
- [已发布的镜像和 wheel](./docs/artifact-inventory.md)
- [`docs/serve-performance.md`](./docs/serve-performance.md)：Serve 性能结果。

## 致谢

本项目基于 [Ray](https://github.com/ray-project/ray) 和 [KubeRay](https://github.com/ray-project/kuberay)，上游组件遵循各自的许可证。
