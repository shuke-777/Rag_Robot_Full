# Docker 容器化技术入门

## 1. Docker 简介

Docker 是一个开源的容器化平台，用于开发、部署和运行应用程序。

### 1.1 核心概念

- **镜像 (Image)**: 只读的模板，包含运行应用所需的一切
- **容器 (Container)**: 镜像的运行实例
- **仓库 (Registry)**: 存储和分发镜像的服务（如Docker Hub）
- **Dockerfile**: 构建镜像的脚本

### 1.2 Docker vs 虚拟机

| 特性 | Docker | 虚拟机 |
|------|--------|--------|
| 启动速度 | 秒级 | 分钟级 |
| 资源占用 | 少 | 多 |
| 性能 | 接近原生 | 有损耗 |
| 隔离性 | 进程级 | 系统级 |

## 2. 安装 Docker

### 2.1 Mac/Windows

```bash
# 下载并安装 Docker Desktop
# https://www.docker.com/products/docker-desktop
```

### 2.2 Linux (Ubuntu)

```bash
# 更新包索引
sudo apt-get update

# 安装依赖
sudo apt-get install ca-certificates curl gnupg

# 添加Docker官方GPG密钥
sudo install -m 0755 -d /etc/apt/keyrings
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo gpg --dearmor -o /etc/apt/keyrings/docker.gpg

# 设置仓库
echo \
  "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.gpg] https://download.docker.com/linux/ubuntu \
  $(lsb_release -cs) stable" | sudo tee /etc/apt/sources.list.d/docker.list > /dev/null

# 安装Docker
sudo apt-get update
sudo apt-get install docker-ce docker-ce-cli containerd.io

# 验证安装
docker --version
```

## 3. Docker 基础命令

### 3.1 镜像操作

```bash
# 搜索镜像
docker search python

# 拉取镜像
docker pull python:3.9
docker pull ubuntu:20.04

# 查看本地镜像
docker images

# 删除镜像
docker rmi python:3.9

# 构建镜像
docker build -t myapp:1.0 .

# 给镜像打标签
docker tag myapp:1.0 myuser/myapp:1.0

# 推送镜像到Docker Hub
docker push myuser/myapp:1.0
```

### 3.2 容器操作

```bash
# 运行容器
docker run python:3.9 python --version

# 交互式运行
docker run -it ubuntu:20.04 /bin/bash

# 后台运行
docker run -d nginx

# 查看运行中的容器
docker ps

# 查看所有容器（包括停止的）
docker ps -a

# 停止容器
docker stop container_id

# 启动已停止的容器
docker start container_id

# 重启容器
docker restart container_id

# 删除容器
docker rm container_id

# 删除所有停止的容器
docker container prune

# 查看容器日志
docker logs container_id
docker logs -f container_id  # 实时查看

# 进入运行中的容器
docker exec -it container_id /bin/bash

# 查看容器详细信息
docker inspect container_id
```

## 4. Dockerfile

### 4.1 基本语法

```dockerfile
# 基础镜像
FROM python:3.9-slim

# 维护者信息
LABEL maintainer="your.email@example.com"

# 设置工作目录
WORKDIR /app

# 复制文件
COPY requirements.txt .
COPY . .

# 执行命令
RUN pip install --no-cache-dir -r requirements.txt

# 暴露端口
EXPOSE 8000

# 设置环境变量
ENV PYTHONUNBUFFERED=1

# 容器启动命令
CMD ["python", "app.py"]
```

### 4.2 Python Web 应用示例

```dockerfile
FROM python:3.9-slim

WORKDIR /app

# 先复制依赖文件（利用缓存）
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 再复制应用代码
COPY . .

# 创建非root用户
RUN useradd -m appuser && chown -R appuser /app
USER appuser

EXPOSE 8000

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
```

### 4.3 多阶段构建

```dockerfile
# 构建阶段
FROM node:16 AS builder
WORKDIR /app
COPY package*.json ./
RUN npm install
COPY . .
RUN npm run build

# 运行阶段
FROM nginx:alpine
COPY --from=builder /app/dist /usr/share/nginx/html
EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]
```

## 5. Docker Compose

### 5.1 docker-compose.yml 示例

```yaml
version: '3.8'

services:
  # Web 应用
  web:
    build: .
    ports:
      - "8000:8000"
    volumes:
      - .:/app
    environment:
      - DATABASE_URL=postgresql://user:pass@db:5432/mydb
    depends_on:
      - db
      - redis

  # 数据库
  db:
    image: postgres:14
    volumes:
      - postgres_data:/var/lib/postgresql/data
    environment:
      - POSTGRES_USER=user
      - POSTGRES_PASSWORD=pass
      - POSTGRES_DB=mydb

  # Redis 缓存
  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"

volumes:
  postgres_data:
```

### 5.2 Compose 命令

```bash
# 启动所有服务
docker-compose up

# 后台启动
docker-compose up -d

# 停止所有服务
docker-compose down

# 停止并删除卷
docker-compose down -v

# 查看服务状态
docker-compose ps

# 查看服务日志
docker-compose logs
docker-compose logs -f web

# 执行命令
docker-compose exec web python manage.py migrate

# 重启服务
docker-compose restart web
```

## 6. 数据持久化

### 6.1 Volume (卷)

```bash
# 创建卷
docker volume create mydata

# 使用卷
docker run -v mydata:/data ubuntu

# 查看卷
docker volume ls

# 删除卷
docker volume rm mydata
```

### 6.2 Bind Mount (绑定挂载)

```bash
# 挂载主机目录到容器
docker run -v /host/path:/container/path ubuntu

# 只读挂载
docker run -v /host/path:/container/path:ro ubuntu
```

## 7. 网络

### 7.1 网络模式

```bash
# 创建网络
docker network create mynet

# 查看网络
docker network ls

# 容器连接到网络
docker run --network mynet nginx

# 查看网络详情
docker network inspect mynet
```

### 7.2 容器互联

```bash
# 启动数据库容器
docker run --name mydb --network mynet postgres

# 启动应用容器，可以通过mydb访问数据库
docker run --name myapp --network mynet myapp:1.0
```

## 8. 实战示例

### 8.1 FastAPI + PostgreSQL

**Dockerfile**:
```dockerfile
FROM python:3.9-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8000

CMD ["uvicorn", "main:app", "--host", "0.0.0.0"]
```

**docker-compose.yml**:
```yaml
version: '3.8'

services:
  api:
    build: .
    ports:
      - "8000:8000"
    environment:
      - DATABASE_URL=postgresql://postgres:password@db:5432/mydb
    depends_on:
      - db

  db:
    image: postgres:14
    environment:
      - POSTGRES_PASSWORD=password
      - POSTGRES_DB=mydb
    volumes:
      - db_data:/var/lib/postgresql/data

volumes:
  db_data:
```

**requirements.txt**:
```txt
fastapi
uvicorn[standard]
sqlalchemy
psycopg2-binary
```

### 8.2 部署流程

```bash
# 1. 构建并启动
docker-compose up -d

# 2. 查看日志
docker-compose logs -f

# 3. 运行数据库迁移
docker-compose exec api python migrate.py

# 4. 访问应用
curl http://localhost:8000

# 5. 停止
docker-compose down
```

## 9. 最佳实践

### 9.1 镜像优化

```dockerfile
# 使用小体积基础镜像
FROM python:3.9-slim  # 而不是 python:3.9

# 多阶段构建
FROM python:3.9 AS builder
# ... 构建步骤

FROM python:3.9-slim
COPY --from=builder /app /app

# 合并RUN命令减少层数
RUN apt-get update && \
    apt-get install -y git && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# 利用缓存，先复制依赖文件
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .  # 代码变化不会使上面的层失效
```

### 9.2 .dockerignore

```
# .dockerignore
__pycache__
*.pyc
*.pyo
*.pyd
.Python
env/
venv/
.git
.gitignore
README.md
.pytest_cache
.coverage
htmlcov/
dist/
build/
*.egg-info
```

### 9.3 安全性

```dockerfile
# 不要以root用户运行
RUN useradd -m appuser
USER appuser

# 不要在镜像中存储敏感信息
# 使用环境变量或secrets

# 使用特定版本的镜像
FROM python:3.9.17-slim  # 而不是 python:latest

# 扫描漏洞
# docker scan myapp:1.0
```

## 10. 常用命令速查

```bash
# 系统信息
docker info
docker version

# 清理
docker system prune              # 清理未使用的容器、网络、镜像
docker system prune -a           # 清理所有未使用的资源
docker volume prune              # 清理未使用的卷

# 资源监控
docker stats                     # 查看容器资源使用情况
docker top container_id          # 查看容器进程

# 导出/导入
docker save myapp:1.0 > myapp.tar        # 导出镜像
docker load < myapp.tar                  # 导入镜像
docker export container_id > backup.tar  # 导出容器
docker import backup.tar myapp:backup    # 导入为镜像
```

## 11. 故障排查

```bash
# 查看容器日志
docker logs container_id
docker logs --tail 100 container_id
docker logs --since 30m container_id

# 进入容器调试
docker exec -it container_id /bin/bash

# 查看容器进程
docker top container_id

# 查看容器资源使用
docker stats container_id

# 查看容器配置
docker inspect container_id

# 查看容器文件系统变化
docker diff container_id
```

## 总结

Docker 容器化技术的核心要点：
- **基础概念**: 镜像、容器、仓库
- **常用命令**: docker run, build, ps, logs
- **Dockerfile**: 构建自定义镜像
- **Docker Compose**: 多容器应用编排
- **数据持久化**: Volume 和 Bind Mount
- **网络**: 容器互联和网络管理
- **最佳实践**: 镜像优化、安全性、.dockerignore

掌握Docker可以大大简化应用的开发、测试和部署流程。
