# RISC-V 上的 KubeRay

[English](./README.md) | [简体中文](./README-ZH.md)

在 RISC-V 环境中构建、部署 Ray 和 KubeRay，并研究其性能瓶颈。

本仓库整理项目源码补丁、构建部署材料和实验方法。现有结果来自一台 RISC-V 物理机上的多个 Kubernetes Pod，不能视为跨物理机或跨架构的结果。

## 项目进展

- 已在 RISC-V 上构建 Ray 2.52.0，并为 Abseil、Boost.Context 等依赖准备兼容补丁。
- 已在实验环境验证 Core task、actor、对象传输、KubeRay 部署、手动扩缩容、RayJob 和基础 Serve 部署。
- 50 req/s 实验出现间歇性 Serve 退化。同机对照和 60 分钟验证支持每副本设置 `max_ongoing_requests=2` 能改善表现；这一结果不代表通用容量保证。
- 计划中的两小时验证**尚未完成**：功能验收因探针事件未命中而中止，ABBA 开销对照及主实验均未启动。

项目仍在进行中，干净环境复现和跨架构对照尚待验证。

## 材料与复现

仓库目录和材料清单正在整理。实验室使用的构建脚本和 Kubernetes 配置需要在其他环境使用前检查和调整。已有实验数据、wheelhouse 和容器镜像需要单独备份；文档中记录了位置并不等于已经备份。

## 致谢

本项目基于 [Ray](https://github.com/ray-project/ray) 和 [KubeRay](https://github.com/ray-project/kuberay) 开展，上游组件仍遵循各自的许可证。

