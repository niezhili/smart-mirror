import asyncio
import websockets
import uuid
import json
import gzip
import copy
import yaml
import os
import glob
CONFIG_PATH = os.path.join(os.path.dirname(__file__), "../../config/config.yaml")
with open(CONFIG_PATH, 'r', encoding='utf-8') as f:
    config = yaml.safe_load(f)

huoshan_config = config['tts']['tts_huoshan']

# ====== 配置参数（请替换为你自己的）======
appid = huoshan_config['appid']
token = huoshan_config['token']
cluster = huoshan_config['cluster']
voice_type = huoshan_config['voice_type']
host = huoshan_config['host']
api_url = f"wss://{host}/api/v1/tts/ws_binary"

# ====== 请求头格式（固定）======
default_header = bytearray(b'\x11\x10\x11\x00')

# ====== 基础请求模板 ======
request_json = {
    "app": {
        "appid": appid,
        "token": token,
        "cluster": cluster
    },
    "user": {
        "uid": "388808087185088"
    },
    "audio": {
        "voice_type": voice_type,
        "encoding": "wav",
        "speed_ratio": 1.0,
        "volume_ratio": 1.0,
        "pitch_ratio": 1.0,
    },
    "request": {
        "reqid": "",
        "text": "",
        "text_type": "plain",
        "operation": "submit"
    }
}


async def _synthesize(text: str, output_file: str):
    """内部异步函数：合成指定文本为语音并保存到 output_file"""
    submit_request = copy.deepcopy(request_json)
    submit_request["request"]["reqid"] = str(uuid.uuid4())
    submit_request["request"]["text"] = text

    payload_bytes = json.dumps(submit_request).encode('utf-8')
    payload_bytes = gzip.compress(payload_bytes)

    full_client_request = bytearray(default_header)
    full_client_request.extend((len(payload_bytes)).to_bytes(4, 'big'))
    full_client_request.extend(payload_bytes)
    async with websockets.connect(
        api_url,
        extra_headers={"Authorization": f"Bearer; {token}"},
        ping_interval=None
    ) as ws:
        await ws.send(full_client_request)
        file = open(output_file, "wb")
        while True:
            res = await ws.recv()
            done = _parse_response(res, file)
            if done:
                file.close()
                break


def _parse_response(res, file):
    """解析服务器响应，写入音频数据"""
    header_size = res[0] & 0x0f
    message_type = res[1] >> 4
    payload = res[header_size * 4:]

    if message_type == 0xb:
        sequence_number = int.from_bytes(payload[:4], "big", signed=True)
        payload = payload[8:]
        file.write(payload)
        return sequence_number < 0
    elif message_type == 0xf:
        code = int.from_bytes(payload[:4], "big", signed=False)
        error_msg = payload[8:]
        error_msg = gzip.decompress(error_msg) if res[2] & 0x0f == 1 else error_msg
        print(f"[TTS Error] Code: {code}, Message: {error_msg.decode('utf-8')}")
        return True
    else:
        print("未知消息类型:", message_type)
        return True


def text_to_speech(text: str, output_file: str = "output.mp3"):
    """
    公共函数：将指定文本合成语音并保存为 MP3 文件

    :param text: 要合成的文本内容
    :param output_file: 输出的 MP3 文件路径
    """
    asyncio.run(_synthesize(text, output_file))

def manage_audio_files(directory: str, max_files: int = 15):
    """
    管理指定目录下的音频文件数量，保留最新的 max_files 个文件。

    :param directory: 存放音频的目录
    :param max_files: 最大保留文件数
    """
    files = glob.glob(os.path.join(directory, "*.mp3"))
    if len(files) > max_files:
        # 按修改时间排序（升序），删除最早的一批
        files.sort(key=os.path.getmtime)
        for file in files[:len(files) - max_files]:
            try:
                os.remove(file)
                print(f"已删除旧音频：{file}")
            except Exception as e:
                print(f"无法删除 {file}: {str(e)}")
