#!/bin/bash

# 设置默认值
USE_GUNICORN=${USE_GUNICORN:-false}
MCP_MODE=${MCP_MODE:-false}

# 输出服务信息
echo "TTS文本转语音服务启动中..."
echo "MCP模式: $MCP_MODE"

if [ "$MCP_MODE" = "true" ]; then
    echo "以MCP服务模式运行，API端点: /api/tts 和 /api/voices"
    echo "MCP服务配置文件: /app/mcp.json"
fi

# 检查环境变量并设置API密钥
if [ ! -z "$SECRET_ID" ] && [ ! -z "$SECRET_KEY" ]; then
    echo "使用环境变量中的API密钥配置"
    # 这里可以添加替换配置文件中密钥的逻辑
    # 例如使用sed命令替换app.py中的密钥
fi

# 根据环境变量决定使用Flask开发服务器还是Gunicorn
if [ "$USE_GUNICORN" = "true" ]; then
    echo "使用Gunicorn作为WSGI服务器..."
    exec gunicorn --bind 0.0.0.0:5000 --workers 4 app:app
else
    echo "使用Flask开发服务器..."
    exec python app.py
fi