import asyncio
import websockets
import json
import uuid
import wave

# 替换为你的火山引擎凭证
APP_KEY = "6082784057"
ACCESS_KEY = "bF4nRpNiCcP8HDLfDJYvFupObvZxy0gq"
RESOURCE_ID = "volc.service_type.10029"  # 大模型语音合成资源ID

# WebSocket 地址
URI = "wss://openspeech.bytedance.com/api/v3/tts/bidirection"

# 音色配置
SPEAKER = "zh_female_shuangkuaisisi_moon_bigtts"

# 音频参数（支持WAV）
AUDIO_PARAMS = {
    "format": "wav",
    "sample_rate": 24000,
}

# 构建 StartSession 请求
def build_start_session(session_id):
    return {
        "user": {"uid": "12345"},
        "event": 100,
        "req_params": {
            "text": "你好，这是测试文本",
            "speaker": SPEAKER,
            "audio_params": AUDIO_PARAMS
        }
    }

# 构建 TaskRequest 请求
def build_task_request(session_id, text):
    return {
        "user": {"uid": "12345"},
        "event": 200,
        "req_params": {
            "text": text,
            "speaker": SPEAKER,
            "audio_params": AUDIO_PARAMS
        }
    }

# 构建 FinishSession 请求
def build_finish_session(session_id):
    return {
        "event": 102,
        "session_id": session_id
    }

# 主函数：封装为 run_tts()
async def run_tts():
    session_id = str(uuid.uuid4())
    headers = {
        "X-Api-App-Key": APP_KEY,
        "X-Api-Access-Key": ACCESS_KEY,
        "X-Api-Resource-Id": RESOURCE_ID,
        "X-Api-Connect-Id": str(uuid.uuid4())
    }

    async with websockets.connect(URI, extra_headers=headers) as websocket:
        print("WebSocket 连接建立成功")

        # 1. 发送 StartConnection
        await websocket.send(json.dumps({"event": 1, "payload": {}}))
        print("已发送 StartConnection")

        # 2. 接收 ConnectionStarted
        response = await websocket.recv()
        print("ConnectionStarted 响应:", response)

        # 3. 发送 StartSession
        await websocket.send(json.dumps(build_start_session(session_id)))
        print("已发送 StartSession")

        # 4. 接收 SessionStarted
        response = await websocket.recv()
        print("SessionStarted 响应:", response)

        # 5. 发送文本（可多次）
        texts = [
            "你好，这是第一段文本。",
            "第二段文本用于测试流式合成。",
            "最后一段文本，结束会话。"
        ]
        for text in texts:
            await websocket.send(json.dumps(build_task_request(session_id, text)))

        # 6. 发送 FinishSession
        await websocket.send(json.dumps(build_finish_session(session_id)))
        print("已发送 FinishSession")

        # 7. 接收音频数据并保存为 WAV 文件
        output_wav = wave.open("output.wav", "wb")
        output_wav.setnchannels(1)  # 单声道
        output_wav.setsampwidth(2)  # 16位
        output_wav.setframerate(24000)  # 采样率

        while True:
            try:
                data = await websocket.recv()
                if isinstance(data, str):
                    print("收到文本消息:", data)
                else:
                    print("收到二进制音频数据，长度:", len(data))
                    output_wav.writeframes(data)
            except websockets.exceptions.ConnectionClosed:
                print("连接已关闭")
                break

        output_wav.close()
        print("音频已保存为 output.wav")

# 程序入口
if __name__ == "__main__":
    print("开始运行 TTS 测试程序...")
    asyncio.run(run_tts())
    print("程序结束")