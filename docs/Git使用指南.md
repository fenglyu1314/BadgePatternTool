# Git版本管理使用指南

## 分支策略

### 主要分支
- **master**: 主分支，存放稳定的发布版本
- **develop**: 开发分支，日常开发工作在此进行

### 功能分支
- **feature/功能名**: 新功能开发分支
- **hotfix/修复名**: 紧急修复分支
- **release/版本号**: 发布准备分支

## 常用命令

### 基础操作
```bash
# 查看状态
git status

# 查看分支
git branch

# 切换分支
git checkout develop
git checkout master

# 创建并切换到新分支
git checkout -b feature/新功能名
```

### 提交规范
```bash
# 添加文件
git add .
git add 文件名

# 提交（遵循提交规范）
git commit -m "feat(ui): 添加图片裁剪功能"
git commit -m "fix(core): 修复导出PDF时的内存泄漏"
git commit -m "docs: 更新README文档"
```

### 分支合并
```bash
# 切换到目标分支
git checkout develop

# 合并功能分支
git merge feature/新功能名

# 删除已合并的功能分支
git branch -d feature/新功能名
```

## 提交信息规范

### 格式
```
type(scope): description

[可选的正文]

[可选的脚注]
```

### 类型说明
- **feat**: 新功能
- **fix**: 修复bug
- **docs**: 文档更新
- **style**: 代码格式调整（不影响功能）
- **refactor**: 代码重构
- **test**: 测试相关
- **chore**: 构建过程或辅助工具的变动

### 示例
```bash
git commit -m "feat(ui): 添加图片缩放功能"
git commit -m "fix(export): 修复PDF导出时图片模糊问题"
git commit -m "docs(readme): 更新安装说明"
git commit -m "refactor(core): 重构图片处理模块"
```

## 发布流程

### 1. 准备发布
```bash
# 从develop创建release分支
git checkout develop
git checkout -b release/v1.0.0

# 更新版本号和CHANGELOG
# 进行最后的测试和修复
```

### 2. 完成发布
```bash
# 合并到master
git checkout master
git merge release/v1.0.0

# 创建标签
git tag -a v1.0.0 -m "Release version 1.0.0"

# 合并回develop
git checkout develop
git merge release/v1.0.0

# 删除release分支
git branch -d release/v1.0.0
```

## 注意事项

1. **提交前检查**: 确保代码能正常运行
2. **提交信息**: 使用规范的提交信息格式
3. **分支管理**: 及时删除已合并的功能分支
4. **版本标签**: 重要版本发布时创建标签
5. **CHANGELOG**: 及时更新版本变更记录
