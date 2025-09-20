// 等待DOM加载完成后执行（确保能获取到页面元素）
const server = "http://c2.zmal.top:7444"
async function setStatus(status) {
    try {
        const response = await fetch(`${server}/set_status?mode=${status}`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            }
        });

        // 检查响应是否成功
        if (response.ok) {
            console.log("状态设置成功"+status);
            if(status==="talking"){
                window.location.href = "/";
            }
        } else {
            console.error("服务器返回错误", response.status);
        }
    } catch (error) {
        console.error("请求失败", error);
    }
}
window.onload = function () {
    setStatus("cali");
};


document.addEventListener('DOMContentLoaded', function () {
    // 获取页面元素
    const fontBtns = document.querySelectorAll('.font-btn');
    const voiceBtn = document.querySelector('.voice-btn');
    const generateBtn = document.querySelector('.generate-btn');
    const contentInput = document.querySelector('.content-input');
    const resultArea = document.getElementById('calligraphyResult');
    const calligraphyModal = document.getElementById('calligraphyModal');
    const modalImage = document.getElementById('modalImage');
    const closeModal = document.getElementById('closeModal');

    // 字体选择逻辑：切换选中状态
    fontBtns.forEach(btn => {
        btn.addEventListener('click', function () {
            fontBtns.forEach(b => b.classList.remove('active'));
            this.classList.add('active');
            // console.log('当前选中字体：', this.dataset.font);
        });
    });

    // 语音输入逻辑（对接后端ASR接口）
    voiceBtn.addEventListener('click', async function () {
        // 显示加载状态
        const originalText = this.innerHTML;
        this.innerHTML = '正在录音...';
        this.disabled = true; // 防止重复点击

        try {
            // 调用后端语音识别接口（对应run.py中的/asr端点）
            const response = await fetch(`${server}/asr`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                }
            });

            const data = await response.json();

            if (response.ok) {
                // 识别成功：将结果填入输入框
                contentInput.value = data.text || '识别结果为空';
                alert('语音识别成功！');
            } else {
                // 识别失败：显示错误信息
                alert(`语音识别失败：${data.detail || '未知错误'}`);
            }
        } catch (error) {
            // 网络错误等异常
            alert(`请求失败：${error.message}，请检查后端是否启动`);
        } finally {
            // 恢复按钮状态
            this.innerHTML = originalText;
            this.disabled = false;
        }
    });

    // 生成书法逻辑（对接后端接口）
    generateBtn.addEventListener('click', async function () {
        const inputContent = contentInput.value.trim();

        if (!inputContent) {
            alert('请输入要生成书法的内容');
            return;
        }

        // 显示加载状态
        resultArea.innerHTML = '正在生成书法，请稍等...';
        const choosefont = document.getElementById('fontchoose').value.trim();
        const fontstyle = document.getElementById("fontstyle").value
        // console.log("choose: "+choosefont);
        try {
            // 调用后端接口
            const response = await fetch(`${server}/calligraphy`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    text: inputContent, // 输入的文本
                    title: '书法作品',   // 标题
                    signature: '智能助手',
                    choose: choosefont,
                    style: fontstyle
                })
            });

            const data = await response.json();

            if (response.ok && data.image_path) {
                // 显示生成的书法图片（点击可查看大图）
                resultArea.innerHTML = `<img src="${server}${data.image_path}">`;

                // 绑定“查看大图”事件
                resultArea.querySelector('img').addEventListener('click', function () {
                    modalImage.src = this.dataset.src;
                    calligraphyModal.style.display = 'flex';
                });
            } else {
                resultArea.innerHTML = `生成失败：${data.detail || '未知错误'}`;
            }
        } catch (error) {
            resultArea.innerHTML = `请求失败：${error.message}`;
        }
    });

    // 模态框关闭逻辑
    closeModal.addEventListener('click', function () {
        calligraphyModal.style.display = 'none';
    });
    calligraphyModal.addEventListener('click', function (event) {
        if (event.target === calligraphyModal) {
            calligraphyModal.style.display = 'none';
        }
    });
});