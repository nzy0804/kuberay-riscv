# RISC-V 上的 KubeRay

[English](./README.md) | [简体中文](./README-ZH.md)

在 RISC-V 环境中构建、部署 Ray 和 KubeRay，并研究性能瓶颈。

## 项目亮点

- 原生构建 Ray 2.52.0，适配 Abseil 和 Boost.Context 等依赖。
- 在 Kubernetes 上部署和验证 Ray Core、RayJob、Serve、手动扩缩容与对象传输。
- 通过 50 req/s 负载实验研究 Serve 路由、反馈和调度。

## 当前进展

实验运行在单台 RISC-V 物理机的多个 Kubernetes Pod 上。同机对照和 60 分钟验证显示，每副本设置 `max_ongoing_requests=2` 后，持续运行表现得到改善。

两小时验证正在准备中：首次功能验收因探针事件未命中而中止，开销对照和主实验待进行。

## 项目材料

仓库围绕源码补丁、构建部署材料、实验代码和结果进行整理。wheel、容器镜像和原始测量数据等大型资产单独保存。

## 致谢

本项目基于 [Ray](https://github.com/ray-project/ray) 和 [KubeRay](https://github.com/ray-project/kuberay)，上游组件遵循各自的许可证。
