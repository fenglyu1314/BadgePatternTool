# GitHub Actions 构建指南

## 📋 概述

本文档说明了BadgePatternTool项目的GitHub Actions自动化构建流程，包括不同触发条件和使用方法。

## 🔄 工作流程类型

### 1. 质量检查 (Quality Check)
**文件**: `.github/workflows/quality-check.yml`

**触发条件**:
- 推送到 `develop` 分支
- 忽略文档和图片文件的更改

**执行内容**:
- ✅ 代码质量检查
- ✅ 轻量级测试
- ✅ 项目结构验证
- ❌ 不构建可执行文件

**用途**: 快速验证代码质量，不消耗大量资源

### 2. 构建和测试 (Build and Test)
**文件**: `.github/workflows/build.yml`

**触发条件**:
- 🔧 **手动触发** (workflow_dispatch)
- 📋 Pull Request 到 `main` 分支

**手动触发参数**:
- `branch`: 要构建的分支 (develop/main)
- `run_tests`: 是否运行完整测试 (true/false)

**执行内容**:
- ✅ 代码质量检查
- ✅ 完整测试 (可选)
- ✅ 构建可执行文件
- ✅ 上传构建产物

### 3. 版本发布 (Release)
**文件**: `.github/workflows/release.yml`

**触发条件**:
- 创建版本标签 (v*.*.*)

**执行内容**:
- ✅ 自动构建
- ✅ 创建GitHub Release
- ✅ 上传发布文件

### 4. 手动发布 (Manual Release)
**文件**: `.github/workflows/manual-release.yml`

**触发条件**:
- 🔧 **手动触发** (workflow_dispatch)

**手动触发参数**:
- `version`: 版本号
- `create_release`: 是否创建GitHub Release

## 🚀 使用指南

### 开发阶段

#### 日常开发提交
```bash
# 推送到develop分支
git push origin develop
```
**结果**: 自动触发质量检查，快速验证代码质量

#### 需要完整构建时
1. 访问 GitHub Actions 页面
2. 选择 "Build and Test" 工作流
3. 点击 "Run workflow"
4. 选择参数:
   - Branch: `develop`
   - Run tests: `true`
5. 点击 "Run workflow" 执行

### 发布阶段

#### 自动发布 (推荐)
```bash
# 创建版本标签
git tag v1.6.1
git push origin v1.6.1
```
**结果**: 自动触发完整构建和发布流程

#### 手动发布
1. 访问 GitHub Actions 页面
2. 选择 "Manual Release" 工作流
3. 点击 "Run workflow"
4. 输入版本号和发布选项
5. 点击 "Run workflow" 执行

## 📊 工作流程对比

| 工作流程 | 触发方式 | 构建时间 | 资源消耗 | 适用场景 |
|---------|---------|---------|---------|---------|
| Quality Check | 自动 | ~2分钟 | 低 | 日常开发 |
| Build and Test | 手动/PR | ~8分钟 | 高 | 测试验证 |
| Release | 标签 | ~10分钟 | 高 | 版本发布 |
| Manual Release | 手动 | ~10分钟 | 高 | 紧急发布 |

## 🔧 手动触发步骤

### 1. 访问GitHub Actions
1. 打开项目GitHub页面
2. 点击 "Actions" 标签
3. 在左侧选择要运行的工作流

### 2. 手动触发构建
1. 点击 "Run workflow" 按钮
2. 选择分支和参数
3. 点击绿色的 "Run workflow" 按钮

### 3. 查看构建结果
1. 在Actions页面查看运行状态
2. 点击具体的运行记录查看详情
3. 下载构建产物 (如果有)

## 📋 构建产物说明

### 命名规则
- **手动构建**: `manual-build-{branch}-{sha}`
- **PR构建**: `pr-build-{sha}`
- **发布构建**: `BadgePatternTool-v{version}-Windows.zip`

### 内容说明
- `BadgePatternTool.exe` - 主程序
- `CHANGELOG.md` - 更新日志
- `docs/` - 文档文件 (如果有)

## ⚠️ 注意事项

### 资源使用
- 手动构建会消耗GitHub Actions分钟数
- 建议只在必要时触发完整构建
- 日常开发依赖质量检查即可

### 分支策略
- `develop` 分支: 日常开发，自动质量检查
- `main` 分支: 稳定版本，PR时自动构建
- 版本标签: 自动发布流程

### 故障排除
- 构建失败时检查日志输出
- 质量检查失败时修复代码问题
- 手动构建可以跳过测试以节省时间

## 📞 支持

如有问题，请联系项目维护者或在GitHub Issues中反馈。
