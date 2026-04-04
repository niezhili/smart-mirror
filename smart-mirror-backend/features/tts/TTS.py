from features.common.config_loader import config
from features.common.text_cutter import text_cutter
from features.common.globals import set_tts_state, is_tts_working
from features.common.utils import tts_huoshan, play_audio_file, manage_audio_files
from features.common.text_clean import text_clean
from loguru import logger
import os
import re
import glob
import queue
import threading
import platform
from concurrent.futures import ThreadPoolExecutor
from loguru import logger
from typing import List, Dict, Any, Optional, Callable, Generator
# 从common模块导入依赖
from features.common.config_loader import config
from features.common.text_cutter import text_cutter
from features.common.globals import set_tts_state, is_tts_working
from features.common.utils import tts_huoshan, play_audio_file, manage_audio_files
from features.common.text_clean import text_clean

# 使用模块级TAG
TAG = __name__

class TtsManager():
    def __init__(self):
        # 初始化状态变量
        self._tts_working = False
        self._tts_lock = threading.Lock()
        
        # 检测设备类型
        self.device_type = 'pc'
        machine_info = platform.uname().machine.lower()
        if 'raspberry' in machine_info or 'arm' in machine_info:
            self.device_type = 'raspberry_pi'
        
        # 根据设备类型选择线程池大小
        if self.device_type == 'raspberry_pi':
            self.max_workers = 2
        else:
            self.max_workers = 4
            
        # 创建线程池
        self.executor = ThreadPoolExecutor(max_workers=self.max_workers)
        
        # 音频播放队列
        self.play_queue = queue.Queue()
        self.playback_active = True
        
        # 音频流队列
        self.audio_queue = queue.Queue()
        
        # 启动队列监控线程
        self.queue_monitor_thread = threading.Thread(target=self._monitor_play_queue)
        self.queue_monitor_thread.daemon = True
        self.queue_monitor_thread.start()
        
        # 设置最大文本长度
        self.max_text_length = 48

    def _detect_char_language(self, char: str) -> str:
        """简单判断字符所属语言"""
        if re.match(r'[\u4e00-\u9fff]', char):  # 中文
            return 'zh'
        elif re.match(r'[ぁ-ゔァ-ヴー]', char):  # 日文
            return 'ja'
        elif re.match(r'[a-zA-Z]', char):  # 英文
            return 'en'
        else:
            return 'other'  # 标点、空格等统一归为其他

    def _split_by_language(self, text: str) -> List[str]:
        """根据语言变化将文本分段"""
        if not text:
            return []

        segments = []
        current_lang = self._detect_char_language(text[0])
        current_segment = text[0]

        for char in text[1:]:
            lang = self._detect_char_language(char)
            if lang == current_lang or lang == 'other' or current_lang == 'other':
                # 如果是相同语言，或当前字符是标点等，继续拼接
                current_segment += char
                if lang != 'other':
                    current_lang = lang  # 更新语言（忽略标点）
            else:
                # 语言变化，保存当前段并开始新段
                segments.append(current_segment)
                current_segment = char
                current_lang = lang

        if current_segment:
            segments.append(current_segment)

        return segments

    def words_cut_new(self, text: str) -> List[str]:
        if not text or text.strip() == "":
            return []

        # 1. 先按语言进行分段
        language_segments = self._split_by_language(text)

        # 2. 对每个语言段落进行长度控制
        processed_segments = []
        for seg in language_segments:
            if len(seg) <= self.max_text_length:
                processed_segments.append(seg)
            else:
                processed_segments.extend(self._split_sentence_new(seg))

        # 3. 合并处理后的段落，确保不超过 max_text_length
        result = []
        temp = ""
        for seg in processed_segments:
            if not seg.strip():
                continue
            if len(temp) + len(seg) <= self.max_text_length:
                temp += seg
            else:
                if temp:
                    result.append(temp)
                if len(seg) <= self.max_text_length:
                    temp = seg
                else:
                    result.extend(self._split_sentence_new(seg))
                    temp = ""
        if temp:
            result.append(temp)

        return result

    def words_cut(self, text: str) -> List[str]:
        if not text or text.strip() == "":
            return []

        cleaned_text = text_clean(text)
        # language = self._detect_language(cleaned_text)
        sentences = text_cutter(cleaned_text)

        # 先确保所有句子都不超过 max_text_length
        # 使用 _split_sentence 处理超长句
        processed_sentences = []
        for sent in sentences:
            if len(sent) > self.max_text_length:
                processed_sentences.extend(self._split_sentence(sent))
            else:
                processed_sentences.append(sent)

        # 现在将句子合并成不超过 max_text_length 的片段
        result = []
        temp = ""

        for sent in processed_sentences:
            # 如果当前句子本身就不为空
            if not sent.strip():
                continue

            if len(temp) + len(sent) <= self.max_text_length:
                temp += sent
            else:
                if temp:  # 先把之前的 temp 推出
                    result.append(temp)
                # 如果当前句子单独也不超，就作为新起点
                if len(sent) <= self.max_text_length:
                    temp = sent
                else:
                    # 理论上不会发生，因为前面已 split
                    # 但以防万一，还是处理一下
                    result.extend(self._split_sentence(sent))
                    temp = ""

        # 最后剩余的 temp
        if temp:
            result.append(temp)

        return result

    def split_by_language_v2(self,text):
        # 匹配两类：
        # 1. 汉字 + 日语字符（平假名、片假名）的组合块
        # 2. 拉丁字母块（含德语变音）
        pattern = r'[\u4e00-\u9fff\u3040-\u309f\u30a0-\u30ff]+|[a-zA-ZäöüßÄÖÜ][a-zA-ZäöüßÄÖÜ\'\-_]*[a-zA-ZäöüßÄÖÜ]?'

        matches = re.findall(pattern, text)

        # 过滤空格，保留有意义的部分
        return [m.strip() for m in matches if m.strip()]
    def words_cut_v2(self, text: str) -> List[str]:
        if not text or text.strip() == "":
            return []

        cleaned_text = text_clean(text)
        # language = self._detect_language(cleaned_text)
        sentences = text_cutter(cleaned_text)

        # 先确保所有句子都不超过 max_text_length
        # 使用 _split_sentence 处理超长句
        processed_sentences = []
        for sent in sentences:
            if len(sent) > self.max_text_length:
                processed_sentences.extend(self._split_sentence(sent))
            else:
                if self._detect_language(sent)!='zh':
                    temp_texts=self.split_by_language_v2(sent)
                    for t in temp_texts:
                        processed_sentences.append(t)
                processed_sentences.append(sent)

        # 现在将句子合并成不超过 max_text_length 的片段
        result = []
        temp = ""

        for sent in processed_sentences:
            # 如果当前句子本身就不为空
            if not sent.strip():
                continue

            if len(temp) + len(sent) <= self.max_text_length:
                temp += sent
            else:
                if temp:  # 先把之前的 temp 推出
                    result.append(temp)
                # 如果当前句子单独也不超，就作为新起点
                if len(sent) <= self.max_text_length:
                    temp = sent
                else:
                    # 理论上不会发生，因为前面已 split
                    # 但以防万一，还是处理一下
                    result.extend(self._split_sentence(sent))
                    temp = ""

        # 最后剩余的 temp
        if temp:
            result.append(temp)

        return result

    def _split_sentence_new(self, sentence: str) -> List[str]:
        result = []
        max_len = self.max_text_length
        if not sentence.strip():
            return []
        while len(sentence) > max_len:
            search_range = sentence[:max_len + 1]
            matches = list(re.finditer(r'[，。！？；,…!?;]', search_range))
            if matches:
                split_pos = matches[-1].end()
            else:
                split_pos = max_len
            result.append(sentence[:split_pos])
            sentence = sentence[split_pos:]
        if sentence:
            result.append(sentence)
        return result

    def _split_sentence(self, sentence: str) -> List[str]:
        """
        辅助方法：将过长的句子按标点分割，避免超过最大长度。
        """
        result = []
        max_len = self.max_text_length
        if sentence is None or sentence.strip() == "":
            return []
        while len(sentence) > max_len:
            # 尝试在 max_len 范围内找最后一个标点进行分割
            # 更合理的策略：在 max_len 内找最后一个标点，而不是第一个
            search_range = sentence[:max_len + 1]  # 多看一个字符
            matches = list(re.finditer(r'[，。！？；,…!?;]', search_range))

            if matches:
                # 取最后一个标点（更合理，避免过早分割）
                split_pos = matches[-1].end()  # end() 包含标点符号
            else:
                # 没有标点，直接按长度截断
                split_pos = max_len

            # 添加分割段
            result.append(sentence[:split_pos])
            sentence = sentence[split_pos:]

        # 添加最后一段（非空才加）
        if sentence:
            result.append(sentence)

        return result
        
    def _detect_language(self, text: str) -> str:
        """
        自动检测文本语言。
        """
        # 检测中文字符
        if re.search(r'[ぁ-ゔァ-ヴー]', text):
            return 'ja'
        # 检测德文字符
        elif re.search(r'[ÄÖÜäöüß]', text):
            return 'de'
        # 检测法文字符
        elif re.search(r'[À-ÿ]', text):
            return 'fr'
        # 检测英文字符
        elif re.search(r'[a-zA-Z]', text):
            return 'en'
        # 默认返回中文
        return 'zh'
        
    def generate(self, text: str) -> List[str]:
        """
        同步生成音频文件。
        """
        try:
            # 设置TTS状态
            self.set_tts_state(True)
            
            result=self.words_cut(text)
            
            # 音频文件路径列表
            audio_files = []
            
            # 合成每个文本片段的音频
            for fragment in result:
                if fragment.strip():  # 跳过空文本
                    try:
                        audio_file = tts_huoshan(fragment, output_dir="temp_tts")
                        if audio_file:
                            audio_files.append(audio_file)
                    except Exception as e:
                        logger.bind(tag=TAG).error(f"合成音频片段失败: {str(e)}")
            
        except Exception as e:
            logger.bind(tag=TAG).error(f"生成音频时出错: {str(e)}", exc_info=True)
            return []
            
        finally:
            # 释放TTS状态
            self.set_tts_state(False)
            
    def play_audio(self, audio_files: List[str]) -> None:
        """
        使用pygame将合成的音频顺序播放。
        
        参数:
            audio_files (List[str]): 需要播放的音频文件路径列表
        """
        try:
            # 设置TTS状态
            self.set_tts_state(True)
            
            # 播放音频
            for i, audio_file in enumerate(audio_files):
                logger.bind(tag=TAG).info(f"播放音频文件 {i+1}/{len(audio_files)}: {audio_file}")
                play_audio_file(audio_file)
                
        finally:
            # 播放完成后清理音频文件
            for audio_file in audio_files:
                try:
                    os.remove(audio_file)
                    logger.bind(tag=TAG).debug(f"已删除音频文件: {audio_file}")
                except Exception as e:
                    logger.bind(tag=TAG).warning(f"删除音频文件失败: {str(e)}")
            
            # 管理音频文件数量
            manage_audio_files("temp_tts")
            
            # 释放TTS状态
            self.set_tts_state(False)
            
    def play_audio_async(self, audio_files: List[str]) -> None:
        """
        异步播放音频文件。
        
        参数:
            audio_files (List[str]): 需要播放的音频文件路径列表
        """
        self.executor.submit(self._playback_worker, audio_files)
        
    def _playback_worker(self, audio_files: List[str]) -> None:
        """播放工作线程，处理音频播放和文件清理"""
        self.play_audio(audio_files)
        
    def add_to_queue(self, audio_files: List[str]) -> bool:
        """
        将音频文件添加到播放队列。
        
        参数:
            audio_files (List[str]): 需要添加到队列的音频文件路径列表
            
        返回:
            bool: 添加是否成功
        """
        if self.playback_active:
            self.play_queue.put(audio_files)
            return True
        return False
        
    def _monitor_play_queue(self) -> None:
        """监控播放队列，自动播放队列中的音频"""
        while self.playback_active:
            try:
                # 获取队列中的音频文件
                audio_files = self.play_queue.get(timeout=1)
                if not audio_files:
                    continue
                print(f"准备播放：{audio_files}")
                # 播放音频
                for audio_file in audio_files:
                    if os.path.exists(audio_file):  # 增加文件存在检查
                        play_audio_file(audio_file)
                    else:
                        logger.error(f"音频文件不存在：{audio_file}")

                # 清理播放完成的音频文件
                for audio_file in audio_files:
                    try:
                        os.remove(audio_file)
                    except Exception as e:
                        logger.bind(tag=TAG).warning(f"删除音频文件失败: {str(e)}")
                
            except queue.Empty:
                continue
            except Exception as e:
                logger.bind(tag=TAG).error(f"播放队列处理异常: {str(e)}")


    def stop_playback(self) -> None:
        """停止所有播放并清空队列"""
        self.playback_active = False
        with self.play_queue.mutex:
            self.play_queue.queue.clear()
        
    def restart_playback(self) -> None:
        """重新启动播放器"""
        self.playback_active = True
        self.queue_monitor_thread = threading.Thread(target=self._monitor_play_queue)
        self.queue_monitor_thread.daemon = True
        self.queue_monitor_thread.start()
        
    def text_to_speech(self, text: str, play_immediately: bool = True) -> List[str]:
        """
        文本转语音主流程。
        
        参数:
            text (str): 需要转换的文本
            play_immediately (bool): 是否立即播放生成的音频
            
        返回:
            List[str]: 生成的音频文件路径列表
        """
        # 同步生成音频
        audio_files = self.generate(text)
        
        # 如果需要立即播放，同步播放音频
        if play_immediately and audio_files:
            self.play_audio(audio_files)
        
        return audio_files
        
    def generate_async(self, text: str, callback: Optional[Callable[[List[str]], None]] = None) -> None:
        """
        异步生成音频文件。
        
        参数:
            text (str): 需要转换的文本
            callback (Callable): 音频生成完成后的回调函数
        """
        self.executor.submit(self._generation_worker, text, callback)
        
    def _generation_worker(self, text: str, callback: Optional[Callable[[List[str]], None]]) -> None:
        """音频生成工作线程，处理文本切割和音频合成"""
        audio_files = self.generate(text)
        
        # 如果提供了回调函数，使用回调返回结果
        if callback:
            callback(audio_files)
            
        return audio_files
        
    def __enter__(self):
        """支持with语句的进入方法"""
        self.set_tts_state(True)
        return self
        
    def __exit__(self, exc_type, exc_val, exc_tb) -> bool:
        """支持with语句的退出方法"""
        self.set_tts_state(False)
        return False
        
    def set_tts_state(self, state: bool) -> None:
        """设置TTS状态，线程安全"""
        with self._tts_lock:
            self._tts_working = state
            logger.bind(tag=TAG).debug(f"TTS状态已更新: {state}")
            
    def is_tts_working(self) -> bool:
        """获取TTS状态，线程安全"""
        with self._tts_lock:
            return self._tts_working
            
    def get_status(self) -> Dict[str, Any]:
        """
        获取当前TTS状态信息。
        
        返回:
            Dict[str, Any]: 包含以下键的状态字典:
                - tts_working (bool): TTS是否正在工作
                - device_type (str): 设备类型（pc/raspberry_pi）
                - queue_size (int): 播放队列大小
                - audio_files_in_temp (int): 临时音频文件数量
                - max_workers (int): 线程池大小
        """
        return {
            'tts_working': self.is_tts_working(),
            'device_type': self.device_type,
            'queue_size': self.play_queue.qsize(),
            'audio_files_in_temp': len(glob.glob("temp_tts/*.wav")),
            'max_workers': self.max_workers
        }
        
    def cleanup(self) -> None:
        """清理资源"""
        # 停止播放
        self.stop_playback()
        
        # 关闭线程池
        self.executor.shutdown(wait=False)
        
        # 清理临时音频文件
        manage_audio_files("temp_tts")
        
    def __del__(self) -> None:
        """析构方法，确保资源被正确释放"""
        try:
            self.cleanup()
        except:
            pass
        
    def __enter__(self):
        """支持with语句的进入方法"""
        self.set_tts_state(True)
        return self
        
    def __exit__(self, exc_type, exc_val, exc_tb) -> bool:
        """支持with语句的退出方法"""
        self.set_tts_state(False)
        return False
