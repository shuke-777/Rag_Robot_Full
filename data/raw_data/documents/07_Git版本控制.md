# Git 版本控制完全指南

## 1. Git 简介

Git 是一个分布式版本控制系统，用于跟踪文件的变化和协作开发。

### 1.1 核心概念

- **仓库 (Repository)**: 存储项目历史记录的数据库
- **提交 (Commit)**: 项目的一个快照
- **分支 (Branch)**: 独立的开发线
- **远程 (Remote)**: 托管在服务器上的仓库

## 2. 基础命令

### 2.1 初始化仓库

```bash
# 初始化新仓库
git init

# 克隆远程仓库
git clone https://github.com/user/repo.git

# 配置用户信息
git config --global user.name "Your Name"
git config --global user.email "your.email@example.com"
```

### 2.2 基本操作

```bash
# 查看状态
git status

# 添加文件到暂存区
git add file.txt
git add .  # 添加所有文件

# 提交更改
git commit -m "提交信息"

# 查看提交历史
git log
git log --oneline
git log --graph --all
```

## 3. 分支管理

### 3.1 分支操作

```bash
# 创建分支
git branch feature-x

# 切换分支
git checkout feature-x

# 创建并切换分支
git checkout -b feature-x

# 查看分支
git branch
git branch -a  # 查看所有分支（包括远程）

# 删除分支
git branch -d feature-x
git branch -D feature-x  # 强制删除
```

### 3.2 合并分支

```bash
# 合并分支
git checkout main
git merge feature-x

# 解决冲突后
git add .
git commit -m "合并feature-x"
```

## 4. 远程操作

### 4.1 远程仓库

```bash
# 查看远程仓库
git remote -v

# 添加远程仓库
git remote add origin https://github.com/user/repo.git

# 推送到远程
git push origin main
git push -u origin main  # 设置上游分支

# 从远程拉取
git pull origin main
git fetch origin  # 只获取，不合并
```

## 5. 撤销操作

```bash
# 撤销工作区的修改
git checkout -- file.txt

# 撤销暂存区的修改
git reset HEAD file.txt

# 撤销提交
git reset --soft HEAD~1  # 保留修改
git reset --hard HEAD~1  # 丢弃修改

# 撤销远程提交
git revert <commit-hash>
```

## 6. 标签管理

```bash
# 创建标签
git tag v1.0.0
git tag -a v1.0.0 -m "版本1.0.0"

# 查看标签
git tag

# 推送标签
git push origin v1.0.0
git push origin --tags  # 推送所有标签

# 删除标签
git tag -d v1.0.0
git push origin :refs/tags/v1.0.0
```

## 7. 最佳实践

### 7.1 提交信息规范

```
<type>(<scope>): <subject>

<body>

<footer>
```

类型 (type):
- feat: 新功能
- fix: 修复bug
- docs: 文档更新
- style: 代码格式调整
- refactor: 重构
- test: 测试相关
- chore: 构建或辅助工具

示例:
```bash
git commit -m "feat(auth): 添加用户登录功能

实现了基于JWT的用户认证系统
- 登录接口
- Token验证
- 用户信息获取

Closes #123"
```

### 7.2 分支策略

**Git Flow**:
- `main`: 生产环境
- `develop`: 开发环境
- `feature/*`: 功能分支
- `release/*`: 发布分支
- `hotfix/*`: 紧急修复

## 8. 常用场景

### 8.1 修改最后一次提交

```bash
# 修改提交信息
git commit --amend -m "新的提交信息"

# 添加遗漏的文件
git add forgotten_file.txt
git commit --amend --no-edit
```

### 8.2 暂存工作

```bash
# 暂存当前修改
git stash

# 查看暂存列表
git stash list

# 恢复暂存
git stash pop
git stash apply stash@{0}

# 删除暂存
git stash drop stash@{0}
```

### 8.3 查看差异

```bash
# 查看工作区和暂存区的差异
git diff

# 查看暂存区和最后一次提交的差异
git diff --staged

# 查看两个提交之间的差异
git diff commit1 commit2
```

## 9. .gitignore 文件

```gitignore
# Python
__pycache__/
*.py[cod]
*.so
.env
venv/

# IDE
.vscode/
.idea/
*.swp

# 操作系统
.DS_Store
Thumbs.db

# 项目特定
config/secrets.yaml
*.log
```

## 10. 常见问题解决

### 10.1 解决冲突

```bash
# 1. 拉取最新代码
git pull origin main

# 2. 如果有冲突，手动编辑文件
# 查找<<<<<<< HEAD标记

# 3. 解决后标记为已解决
git add conflicted_file.txt

# 4. 完成合并
git commit -m "解决合并冲突"
```

### 10.2 回退到某个版本

```bash
# 查看提交历史
git log --oneline

# 回退（保留修改）
git reset --soft <commit-hash>

# 回退（丢弃修改）
git reset --hard <commit-hash>

# 推送到远程（需要强制）
git push --force origin main
```

## 总结

Git 是开发者必备的工具，掌握这些命令和概念可以大大提高协作效率：
- 基础操作：init, add, commit, push, pull
- 分支管理：branch, checkout, merge
- 撤销操作：reset, revert, checkout
- 远程协作：remote, fetch, push, pull
- 最佳实践：规范的提交信息、合理的分支策略
