import asyncio
from features.common.log_loader import logger
import websockets
import uuid
import json
import gzip
import copy
from path_hub import temp_tts_path_abs

from features.common.config_loader import config
huoshan_config = config['tts']['tts_huoshan']
TAG =__name__
# ====== 配置参数=========
token = huoshan_config['token']
host = huoshan_config['host']
api_url = f"wss://{host}/api/v1/tts/ws_binary"

# ====== 请求头格式（固定）======
default_header = bytearray(b'\x11\x10\x11\x00')


def json_process(
    appid = huoshan_config['appid'],
    token = huoshan_config['token'],
    cluster = huoshan_config['cluster'],
    voice_type = huoshan_config['voice_type']['default'],
    motion_type = huoshan_config['motion_type']
):
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
            "pitch_ratio": 1.2,
        },
        "request": {
            "reqid": "",
            "text": "",
            "text_type": motion_type,
            "operation": "submit"
        }
    }
    return request_json


async def _synthesize(text: str, output_file: str,voice_typer=huoshan_config['voice_type']['default']):
    """内部异步函数：合成指定文本为语音并保存到 output_file"""
    request_json=json_process(voice_type=voice_typer)
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
        # print(f"[TTS Error] Code: {code}, Message: {error_msg.decode('utf-8')}")
        logger.bind(tag=TAG).error(f"[TTS Error] Code: {code}, Message: {error_msg.decode('utf-8')}")
        return True
    else:
        # print("未知消息类型:", message_type)
        logger.bind(tag=TAG).warning(f"未知消息类型: {message_type}")
        return True
async def text_to_speech_huoshan_async(text: str, output_file: str = "tts_huoshan_output.wav",voice_type=huoshan_config['voice_type']['default'],language='zh'):
    """
    异步版本
    :param text:
    :param output_file:
    :param voice_type:
    :return:
    """
    if language=='ja':
        voice_type=huoshan_config['voice_type']['ja']
    elif language=='de':
        voice_type=huoshan_config['voice_type']['de']
    elif language=='fr':
        voice_type=huoshan_config['voice_type']['fr']
    elif language=='en':
        voice_type=huoshan_config['voice_type']['en']
    else:
        voice_type=huoshan_config['voice_type']['default']

    await _synthesize(text, output_file,voice_typer=voice_type)


def text_to_speech_huoshan(text: str, output_file: str = "output.wav",voice_type=huoshan_config['voice_type']['default']):
    """
    同步函数：将指定文本合成语音并保存为 wav 文件
    :param text: 要合成的文本内容
    :param output_file: 输出的 wav 文件路径
    """
    asyncio.run(_synthesize(text, output_file,voice_typer=voice_type))
def text_to_speech(text: str, output_file: str = "output.wav",voice_type=huoshan_config['voice_type']['default']):
    """
    公共函数：将指定文本合成语音并保存为 wav 文件

    :param text: 要合成的文本内容
    :param output_file: 输出的 wav 文件路径
    """
    asyncio.run(_synthesize(text, output_file,voice_typer=voice_type))

