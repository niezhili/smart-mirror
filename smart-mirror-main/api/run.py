import os
import sys
import uuid
from fastapi import FastAPI
from fastapi.responses import HTMLResponse
from starlette.staticfiles import StaticFiles
from features.asr.paraformer import ASR
from features.llm.qwen import LLM
from features.tts.tts_speech import tts_speech_sync
from features.tts.audio_process import AudioProcessor
from features.calligraphy.calli_process import Calli
import uvicorn
import json
from filelock import FileLock
from pathlib import Path
from features.calligraphy.pintu import compose_image_from_text
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

asr = ASR()
llm = LLM()
audio_processor=AudioProcessor()
cali=Calli()

STATIC_DIR = "static"
LOCK_FILE = Path(os.path.join(os.path.dirname(__file__), "status.json.lock"))
DATA_FILE = Path(os.path.join(os.path.dirname(__file__), "status.json"))


if not os.path.exists(STATIC_DIR):
    os.makedirs(STATIC_DIR)

app=FastAPI()
app.mount("/static",StaticFiles(directory=STATIC_DIR),name="static")

@app.get("/",response_class=HTMLResponse)
async def read_root():
    return HTMLResponse("""
    <!DOCTYPE html>
    <html>
    <head>
        <title>ASR-LLM-TTS Pipeline</title>
        <meta charset="utf-8">
        <style>
            body {
                font-family: Arial, sans-serif;
                max-width: 800px;
                margin: 0 auto;
                padding: 20px;
                background-color: #f5f5f5;
            }
            .container {
                background-color: white;
                padding: 30px;
                border-radius: 10px;
                box-shadow: 0 0 10px rgba(0,0,0,0.1);
            }
            h1 {
                color: #333;
                text-align: center;
            }
            .section {
                margin: 20px 0;
                padding: 20px;
                border: 1px solid #ddd;
                border-radius: 5px;
            }
            button {
                background-color: #4CAF50;
                color: white;
                padding: 10px 20px;
                border: none;
                border-radius: 4px;
                cursor: pointer;
                font-size: 16px;
            }
            button:hover {
                background-color: #45a049;
            }
            button:disabled {
                background-color: #cccccc;
            }
            input, textarea {
                width: 100%;
                padding: 10px;
                margin: 10px 0;
                border: 1px solid #ddd;
                border-radius: 4px;
                box-sizing: border-box;
            }
            .result {
                background-color: #e9f7ef;
                padding: 15px;
                border-radius: 4px;
                margin: 10px 0;
            }
            .error {
                background-color: #fce4e4;
                padding: 15px;
                border-radius: 4px;
                margin: 10px 0;
            }
            .processing {
                background-color: #fff3cd;
                padding: 15px;
                border-radius: 4px;
                margin: 10px 0;
                text-align: center;
                font-weight: bold;
            }
            audio {
                width: 100%;
                margin: 10px 0;
            }
            img {
                max-width: 100%;
                margin: 10px 0;
            }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>ASR-LLM-TTS Pipeline</h1>

            <!-- ASR Section -->
            <div class="section">
                <h2>1. 语音识别 (ASR)</h2>
                <button onclick="triggerASR()">开始语音识别</button>
                <div id="asrResult"></div>
            </div>

            <!-- LLM-TTS Section -->
            <div class="section">
                <h2>2. 语言模型+语音合成 (LLM-TTS)</h2>
                <textarea id="llmTtsInput" placeholder="输入要处理并转换为语音的文本..." rows="4"></textarea>
                <button onclick="triggerLLMTTS()">处理并播放</button>
                <div id="llmTtsResult"></div>
            </div>

            <!-- Calligraphy Section -->
            <div class="section">
                <h2>3. 书法生成</h2>
                <input type="text" id="calliTitle" placeholder="书法标题">
                <textarea id="calliText" placeholder="要生成书法的文本内容..." rows="4"></textarea>
                <input type="text" id="calliSignature" placeholder="签名">
                <button onclick="generateCalligraphy()">生成书法</button>
                <div id="calliResult"></div>
            </div>

            <!-- Full Pipeline Section -->
            <div class="section">
                <h2>4. 完整流程 (ASR->LLM->TTS)</h2>
                <button onclick="triggerFullPipeline()">开始完整流程</button>
                <div id="pipelineResult"></div>
            </div>
        </div>

        <script>
            // ASR功能
            async function triggerASR() {
                const resultDiv = document.getElementById('asrResult');

                resultDiv.innerHTML = '<div class="processing">正在录音并识别，请说话...</div>';

                try {
                    const response = await fetch('/asr', {
                        method: 'POST'
                    });

                    const data = await response.json();

                    if (response.ok) {
                        resultDiv.innerHTML = `
                            <div class="result">
                                <strong>识别结果:</strong>
                                <p>${data.text}</p>
                            </div>
                        `;
                        // 将结果填充到LLM-TTS输入框
                        document.getElementById('llmTtsInput').value = data.text;
                    } else {
                        resultDiv.innerHTML = `<div class="error">错误: ${data.detail}</div>`;
                    }
                } catch (error) {
                    resultDiv.innerHTML = `<div class="error">请求失败: ${error.message}</div>`;
                }
            }

            // LLM-TTS功能
            async function triggerLLMTTS() {
                const textInput = document.getElementById('llmTtsInput');
                const resultDiv = document.getElementById('llmTtsResult');

                if (!textInput.value.trim()) {
                    resultDiv.innerHTML = '<div class="error">请输入文本</div>';
                    return;
                }

                resultDiv.innerHTML = '<div class="processing">正在处理并合成语音...</div>';

                try {
                    const response = await fetch('/llm_tts', {
                        method: 'POST',
                        headers: {
                            'Content-Type': 'application/json'
                        },
                        body: JSON.stringify({text: textInput.value})
                    });

                    const data = await response.json();

                    if (response.ok) {
                        resultDiv.innerHTML = `
                            <div class="result">
                                <strong>处理结果:</strong>
                                <p>${data.response}</p>
                                <p>语音播放已完成</p>
                            </div>
                        `;
                    } else {
                        resultDiv.innerHTML = `<div class="error">错误: ${data.detail}</div>`;
                    }
                } catch (error) {
                    resultDiv.innerHTML = `<div class="error">请求失败: ${error.message}</div>`;
                }
            }

            // 书法生成功能
            async function generateCalligraphy() {
                const titleInput = document.getElementById('calliTitle');
                const textInput = document.getElementById('calliText');
                const signatureInput = document.getElementById('calliSignature');
                const resultDiv = document.getElementById('calliResult');

                if (!textInput.value.trim()) {
                    resultDiv.innerHTML = '<div class="error">请输入文本</div>';
                    return;
                }

                resultDiv.innerHTML = '<div class="processing">正在生成书法...</div>';

                try {
                    const response = await fetch('/calligraphy', {
                        method: 'POST',
                        headers: {
                            'Content-Type': 'application/json'
                        },
                        body: JSON.stringify({
                            title: titleInput.value || '书法作品',
                            text: textInput.value,
                            signature: signatureInput.value || '智能助手'
                        })
                    });

                    const data = await response.json();

                    if (response.ok && data.image_path) {
                        resultDiv.innerHTML = `
                            <div class="result">
                                <strong>书法生成成功:</strong>
                                <img src="${data.image_path}" alt="书法作品">
                                <p><a href="${data.image_path}" target="_blank">点击查看原图</a></p>
                            </div>
                        `;
                    } else {
                        resultDiv.innerHTML = `<div class="error">生成失败: ${data.detail || '未知错误'}</div>`;
                    }
                } catch (error) {
                    resultDiv.innerHTML = `<div class="error">请求失败: ${error.message}</div>`;
                }
            }

            // 完整流程
            async function triggerFullPipeline() {
                const resultDiv = document.getElementById('pipelineResult');

                resultDiv.innerHTML = '<div class="processing">正在录音并处理完整流程，请说话...</div>';

                try {
                    const response = await fetch('/asr_llm_tts', {
                        method: 'POST'
                    });

                    const data = await response.json();

                    if (response.ok) {
                        resultDiv.innerHTML = `
                            <div class="result">
                                <strong>ASR结果:</strong>
                                <p>${data.asr_text}</p>
                                <strong>LLM结果:</strong>
                                <p>${data.llm_response}</p>
                                <p>语音播放已完成</p>
                            </div>
                        `;
                    } else {
                        resultDiv.innerHTML = `<div class="error">错误: ${data.detail}</div>`;
                    }
                } catch (error) {
                    resultDiv.innerHTML = `<div class="error">请求失败: ${error.message}</div>`;
                }
            }
        </script>
    </body>
    </html>
    """)

@app.post("/calligraphy")
async def calligraphy_endpoint(request: dict):
    try:
        title = request.get("title", "书法作品")
        text = request.get("text", "请输入文本")
        signature = request.get("signature", "佚名")
        choose=request.get("choose", "楷书")
        # 这个choose就是选择字体，支持“楷书”“鹤体”“行书”“金文”，由于字库限制，部分字显示不出来
        style=request.get("style","1")
        # 这个style可选择1（经典），2（书本），3（拼图）

        if not text:
            return {"detail": "没有提供文本内容"}

        async def generate_cali(title, text, signature, choose):
            if style=="1":
                image = cali.create(text, title=f"{title}", signature=f"--{signature}", font_size=60,choose=choose)
            elif style=="2":
                image=cali.create_zitie(text,font_size=88)
            elif style=='3':
                image=compose_image_from_text(text,font_size=250)
            else:
                image = cali.create(text, title=f"{title}", signature=f"--{signature}", font_size=60, choose=choose)
            if image:
                filename = f"{uuid.uuid4()}.png"
                file_path = os.path.join(STATIC_DIR, filename)
                image.save(file_path)
                return f"/{STATIC_DIR}/{filename}"
            return None

        image_path = await generate_cali(title, text, signature,choose)

        if image_path:
            # 提取文件名用于URL访问
            return {"image_path": image_path}
        else:
            return {"detail": "书法生成失败"}
    except Exception as e:
        return {"detail": str(e)}

@app.post("/asr")
async def asr_endpoint():
    async def asr_text():
        # 识别文本
        return asr.audio_to_text()
    try:
        # 直接调用asr_text函数进行录音和识别
        recognized_text = await asr_text()
        return {"text": recognized_text}
    except Exception as e:
        return {"detail": str(e)}

@app.post("/llm_tts")
async def llm_tts_endpoint(request: dict):
    async def llm_tts(text):
        # 文本到播放，返回llm到文本
        texts = llm.chat(text)
        await tts_speech_sync(texts)
        return texts
    try:
        text = request.get("text", "")
        if not text:
            return {"detail": "No text provided"}

        # 直接调用llm_tts函数处理文本并播放语音
        o=await llm_tts(text)
        return {"response": f"处理完成，语音已播放\nllm输出{o}"}
    except Exception as e:
        return {"detail": str(e)}

@app.post("/asr_llm_tts")
async def asr_llm_tts_endpoint():
    async def asr_text():
        # 识别文本
        return asr.audio_to_text()

    async def llm_tts(text):
        # 文本到播放，返回llm到文本
        texts = llm.chat(text)
        await tts_speech_sync(texts)
        return texts

    async def asr_llm_tts():
        # 从识别到播放
        out_asr_text = await asr_text()
        llm_text = await llm_tts(
            out_asr_text
        )
        return out_asr_text, llm_text
    try:
        # 直接调用asr_llm_tts函数执行完整流程
        asr_o,llm_o=await asr_llm_tts()
        return {
            "asr_text": f"ASR处理:{asr_o}",
            "llm_response": f"LLM-TTS处理:{llm_o}"
        }
    except Exception as e:
        return {"detail": str(e)}

@app.get("/get_status")
async def get_status():
    with FileLock(LOCK_FILE, timeout=10):
        try:
            with open(DATA_FILE, 'r', encoding='utf-8') as f:
                data = json.load(f)
                status = data.get('main_py').get('status')
                mode = data.get('main_py').get('mode')
        except Exception as e:
            print(e)
    return {"status":status,"mode":mode}

@app.post("/set_status")
async def in_cali(mode: str):
    try:
        with FileLock(LOCK_FILE, timeout=10):
            with open(DATA_FILE, 'r', encoding='utf-8') as f:
                data = json.load(f)
                data['main_py']['mode'] = mode
            with open(DATA_FILE, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
        return {"detail": "状态更新成功cali"}
    except Exception as e:
        return {"detail": str(e)}



if __name__ == "__main__":
    print("正在启动 ASR-LLM-TTS 服务...")
    print("请在浏览器中打开以下地址访问前端界面:")
    print("  http://localhost:8001")
    print("  http://127.0.0.1:8001")
    print("http://127.0.0.1:8081/docs 访问测试文档")
    print("按 Ctrl+C 停止服务")
    print("-" * 50)

    # 运行 FastAPI 应用
    uvicorn.run(
        "api.run:app",
        host="0.0.0.0",
        port=8001,
        reload=False
    )
