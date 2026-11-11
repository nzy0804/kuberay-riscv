# RISC-V 上的 KubeRay

[English](./README.md) | [简体中文](./README-ZH.md)

在 RISC-V 环境中构建、部署 Ray 和 KubeRay，并研究性能瓶颈。

## 当前进展

- 完成 Ray 2.52.0 的 RISC-V 原生构建，适配 Abseil 和 Boost.Context 等依赖。
- 验证 Ray Core 任务与 actor、对象传输、KubeRay 部署、手动扩缩容、RayJob 和 Serve。
- 将每副本 `max_ongoing_requests` 从 1 调整为 2，改善了 50 req/s 下 Serve 的持续运行表现。两槽位配置在四轮对照中完成 156,000 个请求、错误为 0；后续 60 分钟验证完成 180,000 个请求，其中 5 个返回 HTTP 503。

上述测量运行在单台 RISC-V 物理机的多个 Kubernetes Pod 上。

## 仓库目录

- [`patches/ray/`](./patches/ray/)：Ray 构建和依赖适配补丁。
- [`images/`](./images/)：operator 镜像构建文件和 dashboard 依赖。
- 构建、部署及实验材料正在审阅并陆续整理。

## 致谢

本项目基于 [Ray](https://github.com/ray-project/ray) 和 [KubeRay](https://github.com/ray-project/kuberay)，上游组件遵循各自的许可证。
