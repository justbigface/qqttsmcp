# TTS文本转语音服务 - MCP服务部署指南

## 概述

本文档提供了将TTS文本转语音服务作为MCP服务进行部署和使用的详细指南。MCP（Microservice Cloud Platform）是一个微服务云平台，通过将服务包装为MCP服务，可以更方便地进行服务注册、发现和调用。

## 服务说明

本TTS服务基于腾讯云语音合成API，提供文本到语音的转换功能，支持多种音色和情感参数。作为MCP服务，它提供了标准化的API接口，便于其他服务或应用进行集成。

## MCP服务接口

服务提供以下API接口：

### 1. 文本转语音接口

- **路径**: `/api/tts`
- **方法**: POST
- **功能**: 将文本转换为语音
- **参数**:
  - `text`: 需要转换为语音的文本内容（必填）
  - `voice_type`: 语音音色ID，默认为1001(智瑜)（可选）
  - `emotion`: 情感类型，仅适用于情感音色(1017,1018)（可选）
- **返回**: 音频文件(MP3格式)或错误信息(JSON格式)

### 2. 获取音色列表接口

- **路径**: `/api/voices`
- **方法**: GET
- **功能**: 获取可用的语音音色列表
- **参数**: 无
- **返回**: 音色列表(JSON格式)

## 部署步骤

### 1. 准备工作

- 确保已安装Docker和Docker Compose
- 获取腾讯云API密钥（如需修改默认密钥）

### 2. 部署为MCP服务

#### 方法一：使用Docker Compose（推荐）

1. 克隆或下载项目代码到服务器

2. 进入项目目录
   ```bash
   cd tts文本转语音服务
   ```

3. 构建并启动容器
   ```bash
   docker-compose up -d
   ```

4. 服务将在 http://服务器IP:5000 上运行

#### 方法二：使用Docker命令

1. 构建Docker镜像
   ```bash
   docker build -t tts-mcp-service .
   ```

2. 运行Docker容器
   ```bash
   docker run -d --name tts-mcp-service -p 5000:5000 \
     -e SECRET_ID=您的SecretId \
     -e SECRET_KEY=您的SecretKey \
     tts-mcp-service
   ```

### 3. 注册到MCP平台

1. 登录MCP管理控制台

2. 进入「服务管理」-「服务注册」

3. 填写服务信息：
   - 服务名称：tts-service
   - 服务版本：1.0.0
   - 服务描述：腾讯云TTS文本转语音服务
   - 服务地址：http://服务器IP:5000

4. 上传服务配置文件：选择项目中的`mcp.json`文件

5. 完成注册

## 调用示例

### 1. 获取音色列表

```bash
curl -X GET http://服务器IP:5000/api/voices
```

响应示例：
```json
{
  "voices": [
    {
      "id": 1001,
      "name": "智瑜",
      "supports_emotion": false
    },
    {
      "id": 1017,
      "name": "智蓉",
      "supports_emotion": true
    },
    // 更多音色...
  ]
}
```

### 2. 文本转语音

```bash
curl -X POST http://服务器IP:5000/api/tts \
  -H "Content-Type: application/json" \
  -d '{"text":"欢迎使用文本转语音服务","voice_type":"1001","emotion":"neutral"}' \
  --output speech.mp3
```

## 环境变量配置

服务支持通过环境变量进行配置：

- `SECRET_ID`: 腾讯云API密钥ID
- `SECRET_KEY`: 腾讯云API密钥
- `TTS_HOST`: 腾讯云TTS API主机地址，默认为`tts.tencentcloudapi.com`

## 故障排除

1. **服务无法启动**
   - 检查Docker和Docker Compose是否正确安装
   - 检查端口5000是否被占用

2. **API调用失败**
   - 检查API密钥是否正确
   - 检查网络连接是否正常
   - 查看容器日志：`docker logs tts-mcp-service`

## 安全注意事项

- 生产环境中，请务必使用环境变量设置API密钥，避免在代码中硬编码
- 考虑为API添加适当的访问控制和认证机制
- 定期更新依赖包以修复潜在的安全漏洞

## 更多资源

- [腾讯云TTS API文档](https://cloud.tencent.com/document/product/1073)
- [MCP平台使用指南](https://your-mcp-platform-docs-url)