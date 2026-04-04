## 语音转文本
### 用户接口
#### 1.paraformer.py
audio_to_text(self,input_audio_path:str) 两个模式：1.传入音频路径，返回识别结果 2.不传入音频路径，则录制后返回识别结果
generate_filename() 生成随机文件名
!!! 测试示例在test/asr/test_paraformer.py 由于api请求异步，需要使用asyncio库和await关键字
#### 2.vad.py(服务于paraformer.py)
record_audio(self,filename:str)  录制人声音频，保存到文件(服务于paraformer.py)
close 清理资源
!!! 测试示例在test/asr/test_vad.py
