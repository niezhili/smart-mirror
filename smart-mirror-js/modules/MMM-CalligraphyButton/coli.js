// 等待DOM加载完成后执行（确保能获取到页面元素）
document.addEventListener('DOMContentLoaded', function() {
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
        btn.addEventListener('click', function() {
            fontBtns.forEach(b => b.classList.remove('active'));
            this.classList.add('active');
            console.log('当前选中字体：', this.dataset.font);
        });
    });

    // 语音输入逻辑（后续对接语音识别API）
    voiceBtn.addEventListener('click', function() {
        alert('语音输入功能待开发（需对接语音识别API）');
        // 模拟：假设识别结果填入输入框
        contentInput.value = '床前明月光，疑是地上霜。举头望明月，低头思故乡。';
    });

    // 生成书法逻辑（对接后端接口）
    generateBtn.addEventListener('click', async function() {
        const selectedFont = document.querySelector('.font-btn.active').dataset.font;
        const inputContent = contentInput.value.trim();

        if (!inputContent) {
            alert('请输入要生成书法的内容');
            return;
        }

        // 显示加载状态
        resultArea.innerHTML = '正在生成书法，请稍等...';

        try {
            // 调用后端接口
            const response = await fetch('http://localhost:8001/calligraphy', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    font: selectedFont, // 选中的字体
                    text: inputContent, // 输入的文本
                    title: '书法作品',   // 标题
                    signature: '智能助手'// 签名
                })
            });

            const data = await response.json();

            if (response.ok && data.image_path) {
                // 显示生成的书法图片（点击可查看大图）
                resultArea.innerHTML = `<img src="${data.image_path}" alt="书法作品" data-src="${data.image_path}">`;
                
                // 绑定“查看大图”事件
                resultArea.querySelector('img').addEventListener('click', function() {
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
    closeModal.addEventListener('click', function() {
        calligraphyModal.style.display = 'none';
    });
    calligraphyModal.addEventListener('click', function(event) {
        if (event.target === calligraphyModal) {
            calligraphyModal.style.display = 'none';
        }
    });
});