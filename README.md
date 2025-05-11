# TTS文本转语音服务

## 项目简介

这是一个基于腾讯云TTS API的文本转语音服务，支持多种音色和情感参数，可以将文本内容转换为自然流畅的语音。

## 功能特点

- 支持多种音色选择（智瑜、智聆、智美等）
- 支持情感音色（智蓉、智靖）
- 提供Web界面和API接口
- 支持作为MCP服务部署和调用

## 部署方式

### 标准部署

请参考 [docker-deploy.md](docker-deploy.md) 文件了解如何使用Docker部署本服务。

### MCP服务部署

本服务已支持作为MCP（Microservice Cloud Platform）服务进行部署和调用。详细部署和使用指南请参考 [mcp-deploy.md](mcp-deploy.md) 文件。

## API接口

### 标准接口

- `/synthesize` - 文本转语音接口（POST方法）

### MCP服务接口

- `/api/tts` - 文本转语音接口（POST方法）
- `/api/voices` - 获取可用音色列表（GET方法）

## 使用示例

### Web界面

访问服务根路径（如：http://localhost:5000/）即可使用Web界面。

### API调用

```bash
# 获取音色列表
curl -X GET http://localhost:5000/api/voices

# 文本转语音
curl -X POST http://localhost:5000/api/tts \
  -H "Content-Type: application/json" \
  -d '{"text":"欢迎使用文本转语音服务","voice_type":"1001","emotion":"neutral"}' \
  --output speech.mp3
```

## 配置说明

服务支持通过环境变量进行配置：

- `SECRET_ID`: 腾讯云API密钥ID
- `SECRET_KEY`: 腾讯云API密钥
- `TTS_HOST`: 腾讯云TTS API主机地址

## 许可证

MIT