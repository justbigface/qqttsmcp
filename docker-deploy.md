# TTS文本转语音服务 Docker部署指南

## 项目简介

这是一个基于Flask和腾讯云TTS API的文本转语音服务，可以将输入的文本转换为语音文件。本文档提供了使用Docker进行部署的详细步骤。

## 前置条件

- 安装Docker（[Docker官方安装指南](https://docs.docker.com/get-docker/)）
- 安装Docker Compose（[Docker Compose安装指南](https://docs.docker.com/compose/install/)）
- 获取腾讯云API密钥（如需修改）

## 部署步骤

### 方法一：使用Docker Compose（推荐）

1. 克隆或下载项目代码到服务器

2. 进入项目目录
   ```bash
   cd tts文本转语音服务
   ```

3. 构建并启动容器
   ```bash
   docker-compose up -d
   ```

4. 访问服务
   服务将在 http://服务器IP:5000 上运行

### 方法二：使用Docker命令

1. 构建Docker镜像
   ```bash
   docker build -t tts-service .
   ```

2. 运行Docker容器
   ```bash
   docker run -d -p 5000:5000 --name tts-service tts-service
   ```

3. 访问服务
   服务将在 http://服务器IP:5000 上运行

## 配置说明

### 修改API密钥

如需修改腾讯云API密钥，可以通过以下两种方式：

1. 直接修改app.py文件中的配置（需要重新构建镜像）
   ```python
   SECRET_ID = "您的SecretId"  
   SECRET_KEY = "您的SecretKey"  
   ```

2. 使用环境变量（推荐，无需重新构建镜像）
   
   修改docker-compose.yml文件，添加环境变量：
   ```yaml
   environment:
     - TZ=Asia/Shanghai
     - SECRET_ID=您的SecretId
     - SECRET_KEY=您的SecretKey
   ```

   然后在app.py中使用环境变量（需要修改代码）：
   ```python
   SECRET_ID = os.environ.get("SECRET_ID", "默认SecretId")
   SECRET_KEY = os.environ.get("SECRET_KEY", "默认SecretKey")
   ```

## 常见问题

### 1. 容器无法启动

检查日志：
```bash
docker logs tts-service
```

### 2. 无法访问服务

- 确认容器是否正常运行：`docker ps`
- 检查端口映射是否正确：`docker port tts-service`
- 检查防火墙是否开放5000端口

### 3. 更新服务

```bash
# 使用Docker Compose
docker-compose down
docker-compose up -d --build

# 使用Docker命令
docker stop tts-service
docker rm tts-service
docker build -t tts-service .
docker run -d -p 5000:5000 --name tts-service tts-service
```

## 性能优化

- 如需处理大量请求，可以考虑使用Gunicorn作为WSGI服务器
- 修改Dockerfile中的启动命令：
  ```
  CMD ["gunicorn", "--bind", "0.0.0.0:5000", "app:app"]
  ```

## 数据持久化

如果需要保存生成的语音文件，可以添加数据卷：

```yaml
volumes:
  - ./:/app
  - ./data:/app/data
```

然后修改代码，将生成的语音文件保存到/app/data目录。