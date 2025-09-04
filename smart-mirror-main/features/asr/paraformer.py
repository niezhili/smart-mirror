import asyncio
import time
from config.load_config import config
from log.load_log import logger
from dashscope.audio.asr import Recognition
from http import HTTPStatus
import os
from features.vad.vad import VAD
import uuid
import dashscope
from concurrent.futures.thread import ThreadPoolExecutor
TAG=__name__

class ASR:
    def __init__(self):
        self.logger=logger.bind(tag=TAG)
        
        self.platform=config.get("choose",None).get("asr",None)
        self.api_key=None
        self.model=None
        self.language=None

        self._is_loaded=False
        self.vad=None
        self.loop = asyncio.new_event_loop()
        self.executor = ThreadPoolExecutor(max_workers=5, thread_name_prefix="llm_worker")

        self.recognition=None

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.vad:
            self.vad.close()
        if self.recognition:
            try:
                self.recognition.close()
            except Exception as e:
                self.logger.error(f"关闭asr失败: {str(e)}")
            self.recognition= None
    def audio_to_text(self,input_audio_path:str=""):
        # 用户接口,传入音频路径则读取音频文件，否则则录制
        record_mode=False
        if input_audio_path=="":
            record_mode=True

        if not self._is_loaded:
            if self.platform=="paraformer":
                self._load_paraformer()
            if not self._check():
                self.logger.error("请于config完整配置asr,本次返回空文本")
                return ""
            else:
                self._is_loaded=True
        if self._is_loaded:
            if record_mode:
                audio_path=self._record_audio()
            else:
                audio_path=input_audio_path

            if (audio_path == "")or (not os.path.exists(audio_path)):
                print(audio_path)
                self.logger.warning("无效音频路径，本次返回空文本")
                return ""
            else:
                if self.platform == "paraformer":
                    out_path=self.executor.submit(lambda: self.loop.run_until_complete(self._request_paraformer(audio_path))).result()
                    return out_path
                else:
                    self.logger.warning("未选择asr平台或asr平台不被支持，本次返回空文本")
                    return ""

        return ""

    @staticmethod
    def generate_filename():
        return str(uuid.uuid4().hex)

    def _record_audio(self)->str:
        # 录音人声片段，人声静默1秒结束并且写入音频wav
        # 注意这的filename是文件名，默认路径是【VAD】TEMP_PATH
        filename=f"record_audio_{self.generate_filename()}.wav"
        if not self.vad:
            self.vad=VAD()
        return self.vad.record_audio(filename)


    def _check(self)->bool:
        flag= True
        if self.platform is None or self.platform=="":
            self.logger.warning("未选择asr平台")
            flag=False
        if self.api_key is None or self.api_key=="":
            self.logger.warning("未填写api_key")
            flag=False
        if self.model is None or self.model=="" or self.model== []:
            self.logger.warning("未填写model")
            flag=False
        return flag

    def _load_paraformer(self):
        self.api_key=config.get("asr",None).get("paraformer",None).get("api_key",None)
        self.model=config.get("asr",None).get("paraformer",None).get("model",None)
        self.language=config.get("asr",None).get("paraformer",None).get("language",None)
        if self.api_key:
            dashscope.api_key = self.api_key
    async def _request_paraformer(self, audio_path):
        try:
            if self.recognition is None:
                self.recognition = Recognition(
                    model=self.model,
                    format="wav",
                    sample_rate=16000,
                    language_hints=self.language,
                    callback= None
                )


            loop=asyncio.get_event_loop()
            start_time=time.time()
            raw_result=await loop.run_in_executor(None,self.recognition.call,audio_path)
            end_time=time.time()
            self.logger.info(f"paraformer请求耗时:{end_time-start_time}")

            if raw_result.status_code == HTTPStatus.OK:
                result = raw_result.get_sentence()
                if not result:
                    return ""
                else:
                    # print(raw_result)
                    return result[0]['text']

            else:
                self.logger.warning(f"paraformer错误返回:{raw_result.status_code}")
                return ""
        except Exception as e:
            self.logger.warning(f"paraformer请求失败:{e}")
            return ""

    def _debug(self):
        self.logger.info(f"paraformer参数:{self.platform}")
        self.logger.info(f"api_key:{self.api_key}")
        self.logger.info(f"model:{self.model}")
        self.logger.info(f"language:{self.language}")
        self.logger.info(f"is_loaded:{self._is_loaded}")

