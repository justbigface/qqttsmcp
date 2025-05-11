from flask import Flask, render_template, request, send_file
import hashlib
import hmac
import json
import time
from datetime import datetime
from http.client import HTTPSConnection
import os
import base64
from io import BytesIO

app = Flask(__name__)

# 腾讯云API配置
SECRET_ID = os.environ.get("SECRET_ID", "XXXX")  # 可通过环境变量覆盖
SECRET_KEY = os.environ.get("SECRET_KEY", "XXXX")  # 可通过环境变量覆盖
HOST = os.environ.get("TTS_HOST", "tts.tencentcloudapi.com")
SERVICE = "tts"
VERSION = "2019-08-23"
ACTION = "TextToVoice"

def sign(key, msg):
    return hmac.new(key, msg.encode("utf-8"), hashlib.sha256).digest()

def get_tts_response(text, voice_type='1001', emotion='neutral'):
    try:
        print(f"[INFO] 准备调用腾讯云TTS API，文本长度: {len(text)}，音色类型: {voice_type}，情感类型: {emotion}")
        
        # 确保voice_type是整数
        try:
            voice_type_int = int(voice_type)
        except ValueError:
            print(f"[ERROR] 音色类型转换为整数失败: {voice_type}")
            return {"error": f"无效的音色类型: {voice_type}，必须是整数"}
        
        # 验证音色ID有效性
        valid_voice_ids = {
            10510000: '智逍遥',
            1001: '智瑜',
            1002: '智聆',
            1003: '智美',
            1004: '智云',
            1005: '智莉',
            1008: '智琪',
            1009: '智芸',
            1010: '智华',
            1017: '智蓉',
            1018: '智靖',
            1050: 'WeJack',
            1051: 'WeRose'
        }
        if voice_type_int not in valid_voice_ids:
            return {"error": f"无效的音色ID: {voice_type_int}，可用音色: {', '.join(map(str, valid_voice_ids))}"}
        
        # 检查是否为多情感音色
        is_emotion_voice = voice_type_int in [1018, 1017]
        
        # 更新情感验证逻辑
        valid_emotions = ["neutral", "sad", "happy", "angry", "fear", "news", "story", "radio", 
                         "poetry", "call", "sajiao", "disgusted", "amaze", "peaceful", 
                         "exciting", "aojiao", "jieshuo"]
        
        # 检查语言类型
        is_english_voice = voice_type_int in [1050, 1051]
        
        if is_emotion_voice and emotion not in valid_emotions:
            return {"error": f"情感音色必须指定有效情感参数，可用情感: {', '.join(valid_emotions)}"}
        
        # TTS参数设置 - 根据腾讯云API文档更新参数
        tts_params = {
            "Text": text,
            "SessionId": "session_" + str(int(time.time())),
            "Volume": 1,  # 音量大小，范围：[0，10]，默认值为0，表示正常音量
            "Speed": 1,   # 语速，范围：[-2，2]，默认为0，表示正常语速
            "ProjectId": 0,
            "ModelType": 1,
            "VoiceType": voice_type_int,  # 使用转换后的整数音色参数
            "PrimaryLanguage": 1,  # 1-中文（默认）2-英文 3-粤语
            "SampleRate": 16000,  # 音频采样率，支持16000Hz（默认）和8000Hz
            "Codec": "wav"  # 返回音频格式，可取值：wav（默认），mp3，pcm
        }
        
        # 强制设置情感参数（如果使用情感音色）
        if is_emotion_voice:
            print(f"[INFO] 使用多情感音色，设置情感类型: {emotion}")
            tts_params["EmotionCategory"] = emotion
            tts_params["EmotionIntensity"] = 100  # 情感强度，取值范围：[50，200]，默认值为100
        
        payload = json.dumps(tts_params, ensure_ascii=False)

        print(f"[INFO] TTS请求参数: {payload}")

        timestamp = int(time.time())
        date = datetime.utcfromtimestamp(timestamp).strftime("%Y-%m-%d")

        # 签名步骤1：拼接规范请求串
        http_request_method = "POST"
        canonical_uri = "/"
        canonical_querystring = ""
        ct = "application/json; charset=utf-8"
        canonical_headers = f"content-type:{ct}\nhost:{HOST}\nx-tc-action:{ACTION.lower()}\n"
        signed_headers = "content-type;host;x-tc-action"
        hashed_request_payload = hashlib.sha256(payload.encode("utf-8")).hexdigest()
        canonical_request = (
            http_request_method + "\n" +
            canonical_uri + "\n" +
            canonical_querystring + "\n" +
            canonical_headers + "\n" +
            signed_headers + "\n" +
            hashed_request_payload
        )

        # 签名步骤2：拼接待签名字符串
        algorithm = "TC3-HMAC-SHA256"
        credential_scope = date + "/" + SERVICE + "/" + "tc3_request"
        hashed_canonical_request = hashlib.sha256(canonical_request.encode("utf-8")).hexdigest()
        string_to_sign = (
            algorithm + "\n" +
            str(timestamp) + "\n" +
            credential_scope + "\n" +
            hashed_canonical_request
        )

        # 签名步骤3：计算签名
        secret_date = sign(("TC3" + SECRET_KEY).encode("utf-8"), date)
        secret_service = sign(secret_date, SERVICE)
        secret_signing = sign(secret_service, "tc3_request")
        signature = hmac.new(secret_signing, string_to_sign.encode("utf-8"), hashlib.sha256).hexdigest()

        # 签名步骤4：拼接 Authorization
        authorization = (
            algorithm + " " +
            "Credential=" + SECRET_ID + "/" + credential_scope + ", " +
            "SignedHeaders=" + signed_headers + ", " +
            "Signature=" + signature
        )

        # 构建请求头
        headers = {
            "Authorization": authorization,
            "Content-Type": ct,
            "Host": HOST,
            "X-TC-Action": ACTION,
            "X-TC-Timestamp": str(timestamp),
            "X-TC-Version": VERSION
        }
        
        # 如果有地域信息，添加地域头
        if SERVICE == "tts":
            headers["X-TC-Region"] = "ap-guangzhou"  # 腾讯云TTS服务默认使用广州地域

        print(f"[INFO] 准备发送HTTP请求到腾讯云TTS API")
        
        try:
            conn = HTTPSConnection(HOST)
            conn.request("POST", "/", payload.encode("utf-8"), headers)
            response = conn.getresponse()
            response_data = response.read().decode()
            print(f"[INFO] 收到API响应状态码: {response.status}")
            
            if response.status != 200:
                print(f"[ERROR] API响应非200状态码: {response.status}, 响应内容: {response_data}")
                return {"error": f"API返回错误状态码: {response.status}"}
                
            try:
                json_response = json.loads(response_data)
                if json_response.get('Response', {}).get('Error'):
                    error_msg = f"腾讯云API错误: {json_response['Response']['Error']['Code']} - {json_response['Response']['Error']['Message']}"
                    print(f"[ERROR] {error_msg}")
                    return {"error": error_msg}
                
                # 验证音频数据是否存在
                if not json_response['Response'].get('Audio'):
                    raise ValueError("API响应中缺少音频数据")
                
                return json_response
            except Exception as e:
                error_msg = f"处理API响应失败: {str(e)}"
                print(f"[ERROR] {error_msg}\n原始响应: {response_data}")
                return {"error": error_msg}
                
        except Exception as e:
            print(f"[ERROR] HTTP请求过程发生异常: {str(e)}")
            return {"error": f"HTTP请求异常: {str(e)}"}
        finally:
            conn.close()
            
    except Exception as e:
        import traceback
        error_detail = traceback.format_exc()
        print(f"[ERROR] TTS API调用准备过程发生异常: {str(e)}\n{error_detail}")
        return {"error": f"TTS API调用准备异常: {str(e)}"}

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/voices', methods=['GET'])
def get_voices():
    """获取可用的语音音色列表 - MCP服务接口"""
    try:
        voices = {
            10510000: '智逍遥',
            1001: '智瑜',
            1002: '智聆',
            1003: '智美',
            1004: '智云',
            1005: '智莉',
            1008: '智琪',
            1009: '智芸',
            1010: '智华',
            1017: '智蓉',
            1018: '智靖',
            1050: 'WeJack',
            1051: 'WeRose'
        }
        
        # 构建音色信息，包括是否支持情感
        voice_list = []
        for voice_id, voice_name in voices.items():
            voice_info = {
                "id": voice_id,
                "name": voice_name,
                "supports_emotion": voice_id in [1017, 1018]
            }
            voice_list.append(voice_info)
            
        return json.dumps({"voices": voice_list}, ensure_ascii=False), 200, {"Content-Type": "application/json; charset=utf-8"}
    except Exception as e:
        import traceback
        error_detail = traceback.format_exc()
        print(f"[ERROR] 获取音色列表异常: {str(e)}\n{error_detail}")
        return json.dumps({"error": f"服务器内部错误: {str(e)}"}), 500, {"Content-Type": "application/json; charset=utf-8"}

@app.route('/api/tts', methods=['POST'])
def tts_api():
    """文本转语音API - MCP服务接口"""
    try:
        # 获取JSON请求数据
        request_data = request.get_json()
        if not request_data:
            # 如果不是JSON，尝试获取表单数据
            text = request.form.get('text', '')
            voice_type = request.form.get('voice_type', '1001')
            emotion = request.form.get('emotion', 'neutral')
        else:
            text = request_data.get('text', '')
            voice_type = request_data.get('voice_type', '1001')
            emotion = request_data.get('emotion', 'neutral')
            
        if not text:
            return json.dumps({"error": "文本不能为空"}), 400, {"Content-Type": "application/json; charset=utf-8"}

        print(f"[INFO] 接收到API合成请求，文本长度: {len(text)}，音色类型: {voice_type}，情感类型: {emotion}")
        
        response = get_tts_response(text, voice_type, emotion)
        
        if "Response" in response and "Audio" in response["Response"]:
            # 将Base64音频数据转换为二进制
            audio_data = base64.b64decode(response["Response"]["Audio"])
            print(f"[INFO] 音频数据解码成功，长度: {len(audio_data)} 字节")
            return send_file(
                BytesIO(audio_data),
                mimetype="audio/mp3",
                as_attachment=True,
                download_name="speech.mp3"
            )
        elif "error" in response:
            print(f"[ERROR] TTS API调用出错: {response['error']}")
            return json.dumps({"error": f"语音合成失败: {response['error']}"}), 500, {"Content-Type": "application/json; charset=utf-8"}
        else:
            error_msg = "未知错误，API返回数据格式异常"
            if "Response" in response and "Error" in response["Response"]:
                error_msg = f"API错误: {response['Response']['Error']['Code']} - {response['Response']['Error']['Message']}"
            print(f"[ERROR] {error_msg}")
            return json.dumps({"error": f"语音合成失败: {error_msg}"}), 500, {"Content-Type": "application/json; charset=utf-8"}
    except Exception as e:
        import traceback
        error_detail = traceback.format_exc()
        print(f"[ERROR] 语音合成过程发生异常: {str(e)}\n{error_detail}")
        return json.dumps({"error": f"服务器内部错误: {str(e)}"}), 500, {"Content-Type": "application/json; charset=utf-8"}

@app.route('/synthesize', methods=['POST'])
def synthesize():
    try:
        text = request.form.get('text', '')
        voice_type = request.form.get('voice_type', '1001')  # 默认使用1001音色
        emotion = request.form.get('emotion', 'neutral')  # 获取情感参数
        if not text:
            return json.dumps({"error": "文本不能为空"}), 400

        print(f"[INFO] 接收到合成请求，文本长度: {len(text)}，音色类型: {voice_type}，情感类型: {emotion}")
        
        # 将情感参数传递给get_tts_response函数
        response = get_tts_response(text, voice_type, emotion)
        print(f"[INFO] TTS API响应: {json.dumps(response, ensure_ascii=False)}")
        
        if "Response" in response and "Audio" in response["Response"]:
            # 将Base64音频数据转换为二进制
            audio_data = base64.b64decode(response["Response"]["Audio"])
            print(f"[INFO] 音频数据解码成功，长度: {len(audio_data)} 字节")
            return send_file(
                BytesIO(audio_data),
                mimetype="audio/mp3",
                as_attachment=True,
                download_name="speech.mp3"
            )
        elif "error" in response:
            print(f"[ERROR] TTS API调用出错: {response['error']}")
            return json.dumps({"error": f"语音合成失败: {response['error']}"}), 500
        else:
            error_msg = "未知错误，API返回数据格式异常"
            if "Response" in response and "Error" in response["Response"]:
                error_msg = f"API错误: {response['Response']['Error']['Code']} - {response['Response']['Error']['Message']}"
            print(f"[ERROR] {error_msg}")
            return json.dumps({"error": f"语音合成失败: {error_msg}"}), 500
    except Exception as e:
        import traceback
        error_detail = traceback.format_exc()
        print(f"[ERROR] 语音合成过程发生异常: {str(e)}\n{error_detail}")
        return json.dumps({"error": f"服务器内部错误: {str(e)}"}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)