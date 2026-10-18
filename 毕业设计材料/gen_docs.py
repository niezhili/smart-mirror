# -*- coding: utf-8 -*-
"""生成毕业设计三份材料：任务书、文献综述、开题报告（docx）"""
import re
from docx import Document
from docx.shared import Pt, Cm, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH, WD_LINE_SPACING
from docx.enum.table import WD_ALIGN_VERTICAL
from docx.oxml.ns import qn
from docx.oxml import OxmlElement

import os
OUT = os.path.dirname(os.path.abspath(__file__))

# ---------- 基础工具 ----------

def set_run(run, cn="宋体", en="Times New Roman", size=12, bold=False):
    run.font.name = en
    run.font.size = Pt(size)
    run.font.bold = bold
    run.font.color.rgb = RGBColor(0, 0, 0)
    run._element.rPr.rFonts.set(qn("w:eastAsia"), cn)

def setup_doc(doc):
    for sec in doc.sections:
        sec.page_width, sec.page_height = Cm(21), Cm(29.7)
        sec.top_margin = sec.bottom_margin = Cm(2.54)
        sec.left_margin = sec.right_margin = Cm(3.17)
    st = doc.styles["Normal"]
    st.font.name = "Times New Roman"
    st.font.size = Pt(12)
    st.font.color.rgb = RGBColor(0, 0, 0)
    st.element.rPr.rFonts.set(qn("w:eastAsia"), "宋体")

def indent2(p):
    ind = p._p.get_or_add_pPr().get_or_add_ind()
    ind.set(qn("w:firstLineChars"), "200")
    ind.set(qn("w:firstLine"), "480")

def para(doc_or_cell, text, cn="宋体", size=12, bold=False, align=None,
         indent=True, spacing=1.5, before=0, after=6):
    p = doc_or_cell.add_paragraph()
    pf = p.paragraph_format
    pf.line_spacing = spacing
    pf.space_before = Pt(before)
    pf.space_after = Pt(after)
    if align is not None:
        pf.alignment = align
    if indent:
        indent2(p)
    r = p.add_run(text)
    set_run(r, cn=cn, size=size, bold=bold)
    return p

def heading(doc, text, size=14, before=12, after=8):
    p = para(doc, text, cn="黑体", size=size, bold=True,
             align=WD_ALIGN_PARAGRAPH.LEFT, indent=False,
             before=before, after=after)
    return p

def title(doc, text, size=22):
    return para(doc, text, cn="黑体", size=size, bold=True,
                align=WD_ALIGN_PARAGRAPH.CENTER, indent=False,
                before=6, after=12)

def add_page_number(doc):
    footer = doc.sections[0].footer
    p = footer.paragraphs[0]
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    fld = OxmlElement("w:fldSimple")
    fld.set(qn("w:instr"), "PAGE")
    r = OxmlElement("w:r")
    t = OxmlElement("w:t")
    t.text = "1"
    r.append(t)
    fld.append(r)
    p._p.append(fld)

def cell_text(cell, lines, align=WD_ALIGN_PARAGRAPH.LEFT, bold_first=False,
              indent=True, size=12):
    """在单元格写入多行文本；lines 为 str 或 list[str]"""
    if isinstance(lines, str):
        lines = [lines]
    first = True
    for ln in lines:
        if first:
            p = cell.paragraphs[0]
            first = False
        else:
            p = cell.add_paragraph()
        p.paragraph_format.line_spacing = 1.5
        p.paragraph_format.space_after = Pt(4)
        p.alignment = align
        if indent and not ln.startswith(("1.", "2.", "3.", "4.", "5.", "6.", "7.", "①", "②", "③", "④", "（")):
            indent2(p)
        r = p.add_run(ln)
        set_run(r, size=size, bold=bold_first and p is cell.paragraphs[0])

def label_cell(cell, text, size=12):
    cell.vertical_alignment = WD_ALIGN_VERTICAL.CENTER
    p = cell.paragraphs[0]
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p.paragraph_format.line_spacing = 1.5
    r = p.add_run(text)
    set_run(r, size=size, bold=True)

def value_cell(cell, text, align=WD_ALIGN_PARAGRAPH.LEFT):
    cell.vertical_alignment = WD_ALIGN_VERTICAL.CENTER
    p = cell.paragraphs[0]
    p.alignment = align
    p.paragraph_format.line_spacing = 1.5
    r = p.add_run(text)
    set_run(r, size=12)

# ---------- 参考文献 ----------

REFS = [
    "[1] Vaswani A, Shazeer N, Parmar N, et al. Attention is all you need[C]//Advances in Neural Information Processing Systems (NIPS). 2017: 5998-6008.",
    "[2] Bai J, Bai S, Chu Y, et al. Qwen technical report[EB/OL]. arXiv preprint arXiv:2309.16609, 2023.",
    "[3] Zhang J, Zhang Y, Shi J, et al. Paraformer: Fast and accurate parallel transformer for non-autoregressive end-to-end ASR[C]//Proceedings of Interspeech. 2022: 2063-2067.",
    "[4] Radford A, Kim J W, Xu T, et al. Robust speech recognition via large-scale weak supervision[C]//Proceedings of the 40th International Conference on Machine Learning (ICML). 2023: 28492-28518.",
    "[5] Zhao W X, Zhou K, Li J, et al. A survey of large language models[EB/OL]. arXiv preprint arXiv:2303.18223, 2023.",
    "[6] LeCun Y, Bengio Y, Hinton G. Deep learning[J]. Nature, 2015, 521(7553): 436-444.",
    "[7] Schmidhuber J. Deep learning in neural networks: An overview[J]. Neural Networks, 2015, 61: 85-117.",
    "[8] King D E. Dlib-ml: A machine learning toolkit[J]. Journal of Machine Learning Research, 2009, 10: 1755-1758.",
    "[9] Silero Team. Silero VAD: Pre-trained enterprise-grade voice activity detector[EB/OL]. https://github.com/snakers4/silero-vad, 2024.",
    "[10] Teeuw M. MagicMirror²: The open source modular smart mirror platform[EB/OL]. https://magicmirror.builders, 2024.",
    "[11] 俞栋, 邓力. 解析深度学习：语音识别实践[M]. 俞凯, 钱彦旻, 等译. 北京: 电子工业出版社, 2016.",
    "[12] 宗成庆. 统计自然语言处理（第2版）[M]. 北京: 清华大学出版社, 2013.",
    "[13] Yao S, Zhao J, Yu D, et al. ReAct: Synergizing reasoning and acting in language models[C]//Proceedings of the 11th International Conference on Learning Representations (ICLR). 2023.",
    "[14] Schick T, Dwivedi-Yu J, Dessì R, et al. Toolformer: Language models can teach themselves to use tools[C]//Advances in Neural Information Processing Systems (NeurIPS). 2023.",
    "[15] Xi Z, Chen W, Guo X, et al. The rise and potential of large language model based agents: A survey[EB/OL]. arXiv preprint arXiv:2309.07864, 2023.",
    "[16] Carletta J, Ashby S, Bourban S, et al. The AMI meeting corpus: A pre-announcement[C]//International Workshop on Machine Learning for Multimodal Interaction (MLMI). 2005: 28-39.",
    "[17] Zhong M, Yin D, Yu T, et al. QMSum: A query-based multi-domain meeting summarization dataset[C]//Proceedings of the 2021 Conference of the North American Chapter of the Association for Computational Linguistics (NAACL). 2021: 5590-5600.",
]

TOPIC = "基于树莓派的Agent智能镜子助手设计与实现"
STUDENT = "聂志理"
STUDENT_ID = "1230205081"
KLASS = "通信工程232"
COLLEGE = "人工智能与信息工程学院"
ADVISOR = "吴茗蔚"

# ================= 1. 任务书 =================

def gen_task_book():
    doc = Document()
    setup_doc(doc)
    add_page_number(doc)

    title(doc, "浙江科技大学")
    title(doc, "毕业设计（论文）任务书", size=22)

    tb = doc.add_table(rows=0, cols=4)
    tb.style = "Table Grid"

    def new_row():
        return tb.add_row()

    # 课题名称
    r = new_row()
    label_cell(r.cells[0], "课题名称")
    m = r.cells[1].merge(r.cells[2]).merge(r.cells[3])
    value_cell(m, TOPIC)

    # 类型/来源
    r = new_row()
    label_cell(r.cells[0], "课题类型")
    value_cell(r.cells[1], "工程设计（应用开发）类")
    label_cell(r.cells[2], "课题来源")
    value_cell(r.cells[3], "大学生创新创业训练计划项目")

    # 学生信息
    r = new_row()
    label_cell(r.cells[0], "学生姓名")
    value_cell(r.cells[1], STUDENT)
    label_cell(r.cells[2], "学　　号")
    value_cell(r.cells[3], STUDENT_ID)

    r = new_row()
    label_cell(r.cells[0], "专　　业")
    value_cell(r.cells[1], "通信工程")
    label_cell(r.cells[2], "班　　级")
    value_cell(r.cells[3], KLASS)

    r = new_row()
    label_cell(r.cells[0], "学　　院")
    value_cell(r.cells[1], COLLEGE)
    label_cell(r.cells[2], "指导教师")
    value_cell(r.cells[3], ADVISOR)

    # 一、主要任务与目标
    r = new_row()
    m = r.cells[0].merge(r.cells[1]).merge(r.cells[2]).merge(r.cells[3])
    label_cell(m, "一、主要任务与目标")
    r2 = new_row()
    m2 = r2.cells[0].merge(r2.cells[1]).merge(r2.cells[2]).merge(r2.cells[3])
    cell_text(m2, [
        "本课题要求学生在树莓派嵌入式平台上，设计并实现一款集镜面信息显示、语音交互、身份识别于一体的Agent 智能镜子助手。主要任务包括：",
        "（1）完成系统总体方案设计，划分前端镜面信息显示子系统与后端语音交互子系统，制定软硬件接口与数据流方案；",
        "（2）实现“唤醒—识别—理解—回复”的语音交互闭环，包括基于 Silero VAD 的语音活动检测、语音识别（ASR）、基于大语言模型的多轮对话（LLM）与流式语音合成（TTS），支持中文、英语等多语言交互；",
        "（3）实现基于 PIR 传感器的人体感应与基于 dlib 的人脸识别联动，做到用户靠近自动唤醒、识别身份后个性化问候；",
        "（4）基于 MagicMirror² 框架定制前端展示模块，实现时钟、日历、实时天气、新闻滚动等信息显示；",
        "（5）构建端侧轻量智能体：在树莓派本地部署量化小语言模型，实现查询任务、打卡、报时、查天气等工具调用与长期记忆，采用本地优先、云端兜底的路由策略，保障离线场景核心功能可用；",
        "（6）实现个人任务管理集成：从飞书妙记拉取录音及其转写内容（增量轮询、去重），文本交由云端大语言模型处理，自动整理为待办、日程、提醒、记事等条目并进入待确认队列，用户确认后生效；识别人脸后展示个性化今日任务，支持到点语音与横幅提醒、语音查询与语音打卡；",
        "（7）完成系统集成、功能与性能测试及优化，撰写符合学校规范的毕业论文。",
        "预期目标：在正常网络条件下，语音交互端到端响应时间不超过 5 秒；人脸识别满足日常使用要求；录音结束后 25 分钟内待办进入待确认队列；断网情况下任务查询、打卡、报时、查天气等核心功能可离线使用；系统可连续稳定运行，具备模块化、可配置、可扩展的软件结构。",
    ])

    # 二、基本要求
    r = new_row()
    m = r.cells[0].merge(r.cells[1]).merge(r.cells[2]).merge(r.cells[3])
    label_cell(m, "二、基本要求")
    r2 = new_row()
    m2 = r2.cells[0].merge(r2.cells[1]).merge(r2.cells[2]).merge(r2.cells[3])
    cell_text(m2, [
        "1. 独立完成文献调研，文献综述与开题报告各不少于 2000 字，符合学校规范并通过开题审查；",
        "2. 毕业论文正文不少于 8000 字，结构完整、条理清晰、图表规范；参考文献不少于 10 篇，其中外文文献不少于 2 篇；",
        "3. 完成外文文献翻译，不少于 1 万印刷字符（或译文不少于 2000 汉字），内容与课题相关；",
        "4. 系统功能完整、可现场演示，代码结构规范、注释清晰，关键模块具备测试记录；",
        "5. 论文查重复制比低于 30%，AIGC 智能生成比例低于 40%，符合学校学术诚信要求。",
    ])

    # 三、进度安排
    r = new_row()
    m = r.cells[0].merge(r.cells[1]).merge(r.cells[2]).merge(r.cells[3])
    label_cell(m, "三、进度安排")
    r2 = new_row()
    m2 = r2.cells[0].merge(r2.cells[1]).merge(r2.cells[2]).merge(r2.cells[3])
    cell_text(m2, [
        "1. 2026.10.13—11.2：完成课题申报与选题，明确研究内容与技术路线；",
        "2. 2026.11—2026.12：文献调研与需求分析，完成文献综述与开题报告；",
        "3. 2027.1—2027.2：系统设计与各功能模块开发（语音交互、人脸识别、信息展示、端侧智能体、任务管理集成）；",
        "4. 2027.3：系统集成与测试，完成外文文献翻译，完善开题材料并通过审查；",
        "5. 2027.4：参加中期检查，撰写论文初稿；",
        "6. 2027.5：论文修改定稿，完成查重与 AIGC 检测，制作答辩材料；",
        "7. 2027.5.7—5.20：参加毕业答辩，按答辩意见修改论文并完成材料归档。",
    ])

    # 四、主要参考文献
    r = new_row()
    m = r.cells[0].merge(r.cells[1]).merge(r.cells[2]).merge(r.cells[3])
    label_cell(m, "四、主要参考文献")
    r2 = new_row()
    m2 = r2.cells[0].merge(r2.cells[1]).merge(r2.cells[2]).merge(r2.cells[3])
    cell_text(m2, REFS, indent=False)

    doc.add_paragraph()
    para(doc, "学生（签字）：　　　　　　　　　　日期：　　　年　　月　　日", indent=False, after=12)
    para(doc, "指导教师（签字）：　　　　　　　　　日期：　　　年　　月　　日", indent=False, after=12)
    para(doc, "教研室主任（签字）：　　　　　　　　日期：　　　年　　月　　日", indent=False)

    path = f"{OUT}/毕业设计任务书-基于树莓派的Agent智能镜子助手.docx"
    doc.save(path)
    return path

# ================= 2. 文献综述 =================

LIT_BODY = [
    ("h", "一、引言"),
    ("p", "随着人工智能与物联网技术的快速发展，人机交互方式正从键盘、鼠标、触摸屏等传统手段，向语音、视觉等更自然的方式演进。镜面是人们在盥洗、更衣、出门前高频接触的界面，将其与显示屏、传感器和智能算法结合，就形成了智能镜面（Smart Mirror）这一新型交互终端。智能镜面能够在用户照镜的同时展示时间、天气、新闻等信息，并通过语音和视觉感知与用户交流，是智能家居场景中极具代表性的嵌入式人工智能应用。本文围绕智能镜面系统、语音交互关键技术与嵌入式实现平台三个方向，对国内外研究现状进行综述，为本课题的研究提供依据。"),
    ("h", "二、智能镜面系统的研究与应用现状"),
    ("p", "国外方面，智能镜面较早以创客项目和概念产品的形式出现。开源框架 MagicMirror²[10] 由 Michael Teeuw 发起，采用模块化架构，开发者可以像安装插件一样组合时钟、天气、日历、新闻等显示模块，目前已形成活跃的国际社区，是绝大多数智能镜面研究与二次开发的原型基础。在产业界，三星、松下等公司先后在国际消费电子展（CES）上展出智能镜子概念产品，将增强现实、健康检测等功能引入镜面形态；相关研究还探索了智能镜在皮肤分析、体重管理等健康监测场景中的应用。"),
    ("p", "国内方面，随着智能家居生态的成熟，智能镜产品逐步进入浴室、美妆与服装零售等场景，各类“智能魔镜”“智能化妆镜”商用产品不断涌现。在高校与研究层面，多数工作基于树莓派等单板计算机与 MagicMirror² 框架进行二次开发，重点集中在信息展示定制与简单语音控制上。总体来看，现有智能镜面系统大多停留在“信息展示+简单指令控制”阶段，将大语言模型、人脸识别、多模态感知深度融合进镜面终端的研究仍较少，交互的自然度与智能化水平有较大提升空间。"),
    ("h", "三、语音交互关键技术研究现状"),
    ("h", "3.1 语音活动检测与唤醒"),
    ("p", "语音交互的第一环是判断“用户是否在说话”。传统的语音活动检测（VAD）依赖能量阈值与过零率等手工特征，在噪声环境下性能明显下降。近年来，基于深度学习的 VAD 成为主流，其中 Silero VAD[9] 是典型的轻量级预训练模型，单模型体积小、推理快，可以直接在树莓派等嵌入式设备上本地运行，为资源受限终端提供了可靠的人声检测能力。"),
    ("p", "唤醒词检测（Keyword Spotting）通常在本地持续监听特定关键词，其挑战在于误唤醒率与功耗的平衡：唤醒模型需要全天候运行，过灵敏会造成误唤醒和隐私顾虑，过迟钝则影响首次交互体验。目前常用的做法是将轻量唤醒模型与 VAD 级联，先由 VAD 过滤静音段再进行关键词判决，并引入连续多帧确认与冷却时间等防抖策略，在保证唤醒率的同时降低无效识别带来的资源消耗。此外，唤醒与 VAD 环节尽量在端侧本地完成，也有助于减少音频数据上云带来的隐私风险。"),
    ("h", "3.2 语音识别"),
    ("p", "语音识别（ASR）经历了从 GMM-HMM 到 DNN-HMM 混合系统，再到端到端深度模型的演进[6][7][11]。端到端模型免去了人工设计的发音词典与决策树，主流路线包括 CTC、注意力机制与 Transducer 等。在效率方面，Paraformer[3] 提出非自回归的并行预测结构，在保持识别精度的同时显著降低推理时延，适合对实时性要求高的交互场景；在鲁棒性方面，Whisper[4] 利用大规模弱监督数据训练，在中英文等多语种、多口音场景下表现出很强的泛化能力。对嵌入式终端而言，直接本地部署高精度 ASR 仍然困难，因此通过云端 API（如阿里云 DashScope、百度智能云）调用大规模识别模型，成为当前智能硬件产品的普遍做法。"),
    ("h", "3.3 大语言模型对话"),
    ("p", "Transformer 结构[1]的提出奠定了大语言模型（LLM）的基础。以 GPT 为代表的自回归语言模型证明了规模化的价值，此后 Qwen[2]、DeepSeek 等模型在中文理解、多语言能力与推理水平上不断进步，并通过开放 API 的方式降低了应用接入门槛。综述研究[5]指出，大语言模型已具备多轮上下文对话、指令遵循与角色扮演能力，可以承担智能设备的“对话大脑”。在智能镜面场景中，将用户语音经 ASR 转写后交给 LLM 理解与生成，再由 TTS 播报，即可获得远超固定模板问答的自然对话体验；结合人设配置与多轮上下文管理，还能实现个性化、多语种的助手形象。"),
    ("h", "3.4 语音合成"),
    ("p", "语音合成（TTS）从早期的拼接合成与参数合成，发展到基于深度神经网络的波形生成，自然度已接近真人水平。当前的云端 TTS 服务（如火山引擎、百度智能云）普遍支持多语种、多音色与情感风格控制，并采用 WebSocket 流式接口，可以边生成边播放。对于智能镜面这类交互终端，将长句按标点分段流式合成与播放，能有效压缩用户感知延迟，是提升对话体验的关键工程手段。"),
    ("h", "3.5 大语言模型智能体与工具调用"),
    ("p", "单纯对话之外，研究者进一步提出了大语言模型智能体（LLM Agent）的概念：以模型为“大脑”，通过工具调用感知环境、执行动作。ReAct[13] 将推理轨迹与行动交织，让模型边思考边调用外部工具，显著提升复杂任务的完成率；Toolformer[14] 证明模型可以在自监督条件下学会在合适位置插入 API 调用。综述研究[15]将智能体的基本结构归纳为“规划—记忆—工具使用”三个模块，成为当前端侧与云端 Agent 应用的通用设计范式。在工程实现上，函数调用（Function Calling）通过让模型输出结构化的调用参数而非自然语言，保证了工具执行的确定性；配合单次请求工具调用轮数上限与解析失败回退策略，可以约束小模型误调用带来的风险。在部署侧，模型量化技术与 llama.cpp 等推理框架的成熟，使 0.5B—2B 级模型可以在树莓派等资源受限设备上本地常驻运行，为离线场景下的工具调用与简单对话提供了可行路径。"),
    ("h", "3.6 会议内容理解与任务抽取"),
    ("p", "从会议或谈话录音中自动提取待办事项，学术上属于会议内容理解的研究范畴。AMI 会议语料库[16]提供了多通道录音、转写与标注数据，是该方向的经典评测基础；QMSum[17] 进一步提出基于查询的多域会议摘要任务，推动了对长转写文本要点抽取的研究。相关工作表明，将长转写按语义分段后交由大语言模型进行结构化抽取（待办、日程、提醒、纪要等类别），比传统规则方法具有明显更高的准确率与泛化能力。工程实践中，录音采集与转写通常由成熟的商业平台完成（如飞书妙记等会议转写服务，提供开放 API 供增量拉取转写结果），研究重点集中在转写文本的下游处理——即如何可靠地将非结构化谈话内容映射为可执行的任务条目，并交由用户确认后落地，以控制自动抽取的误判风险。"),
    ("h", "四、嵌入式平台与系统集成研究现状"),
    ("p", "树莓派（Raspberry Pi）是目前应用最广泛的单板计算机之一，具备 GPIO 通用接口、多媒体处理与网络通信能力，且拥有完善的操作系统与软件生态，非常适合智能硬件原型验证。在感知层面，dlib[8] 提供了基于深度度量学习的人脸特征编码方法，将人脸映射为 128 维特征向量进行比对，在常规硬件上即可获得较高的识别精度，广泛用于嵌入式身份识别。"),
    ("p", "系统架构方面，受算力约束，嵌入式 AI 终端普遍采用“端云协同”模式：本地负责传感器采集、VAD、人脸识别等轻量计算，云端负责 ASR、LLM、TTS 等重计算任务，两者通过网络衔接。这种架构兼顾了响应速度、识别质量与设备成本，是当前智能语音硬件的主流方案。其代价是系统对网络质量高度敏感，且需要妥善管理多后端服务的密钥与配置；因此工程上普遍强调配置驱动与模块可插拔设计，使同类能力（如不同厂商的 ASR）可以按需切换，核心逻辑不与具体云服务耦合，从而提高系统的可维护性与可扩展性。"),
    ("h", "五、总结"),
    ("p", "综上所述，智能镜面系统的展示框架、语音交互各环节的关键技术、大语言模型智能体与工具调用方法、会议内容理解技术以及嵌入式平台均已较为成熟，为构建 Agent 智能镜子助手提供了坚实的技术基础。但现有研究仍存在以下不足：一是多数智能镜面仅实现简单语音指令，缺少基于大语言模型的多轮自然对话与工具调用能力；二是语音交互链路的端到端延迟优化研究不足，影响实际体验；三是身份识别与对话系统往往相互独立，个性化服务难以落地；四是从谈话录音到可执行任务的自动化处理链路，在面向个人场景的智能终端上仍缺少完整实践。本课题拟在已有大学生创新创业训练项目的基础上，融合 Silero VAD、Qwen3-ASR 语音识别、Qwen3.6 大语言模型、流式 TTS、dlib 人脸识别与 MagicMirror² 展示框架，并构建端侧轻量智能体、集成基于飞书妙记的个人任务管理，在树莓派平台上实现一个交互自然、响应及时、支持多语种与个性化的 Agent 智能镜子助手，并对其中的端云协同与延迟优化问题进行重点研究，具有较高的研究价值与应用前景。"),
]

def gen_lit_review():
    doc = Document()
    setup_doc(doc)
    add_page_number(doc)

    title(doc, "毕业设计（论文）文献综述", size=22)
    para(doc, f"课题名称：{TOPIC}", indent=False, align=WD_ALIGN_PARAGRAPH.CENTER, after=2)
    para(doc, f"学生姓名：{STUDENT}　　专业：通信工程　　学院：{COLLEGE}",
         indent=False, align=WD_ALIGN_PARAGRAPH.CENTER, after=12)

    for kind, text in LIT_BODY:
        if kind == "h":
            heading(doc, text, size=14)
        else:
            para(doc, text)

    heading(doc, "参考文献", size=14)
    for ref in REFS:
        para(doc, ref, indent=False, size=10.5, after=3)

    path = f"{OUT}/文献综述-基于树莓派的Agent智能镜子助手.docx"
    doc.save(path)
    cjk = sum(len(re.findall(r"[\u4e00-\u9fff]", t)) for k, t in LIT_BODY)
    return path, cjk

# ================= 3. 开题报告 =================

PROP_BODY = [
    ("h", "一、课题背景与意义"),
    ("p", "在智能家居快速普及的背景下，家庭终端正从“人找信息”向“信息找人、自然交互”演进。镜面是家庭中使用频率极高的界面，传统镜面功能单一，却占据着盥洗间、玄关、卧室等黄金位置。将镜面升级为集信息显示、语音对话、身份识别于一体的智能终端，既能充分利用现有空间，又能为用户提供“零学习成本”的自然交互方式。"),
    ("p", "本课题的意义体现在三个方面：其一，应用价值——Agent 智能镜子助手可作为家庭信息中枢，用户无需触碰屏幕即可通过语音获取天气、新闻、日程等信息，并让镜面主动提醒待办事项；其二，技术价值——课题涉及语音活动检测、语音识别、大语言模型、语音合成、人脸识别、嵌入式开发等多项技术的系统集成，对研究资源受限设备上的端云协同架构具有参考意义；其三，工程训练价值——课题覆盖需求分析、方案设计、编码实现、测试优化的完整流程，能够全面锻炼嵌入式人工智能系统的工程实践能力。"),
    ("p", "从需求侧看，智能家居设备保有量持续增长，用户对“免触控、免学习”交互方式的接受度不断提高，语音已成为智能音箱、智能电视等产品的标配交互入口；镜面作为家庭中天然的信息展示界面，与语音交互结合后可以在照镜、洗漱等“双手被占用”的场景中发挥独特优势。从技术侧看，大语言模型的出现使设备从“命令式应答”升级为“对话式服务”成为可能，而云端 AI 服务按量计费的模式也大幅降低了个人开发者构建智能终端的门槛。本课题正是在上述背景下，依托本人主持参与的大学生创新创业训练计划项目，已完成核心功能的初步验证，具备良好的工作基础。"),
    ("h", "二、国内外研究现状"),
    ("p", "国外方面，MagicMirror² 开源框架[10]以模块化方式构建智能镜面应用，是当前最主流的原型平台；产业界的三星、松下等公司展出了融合健康检测与增强显示的智能镜概念产品。语音技术方面，端到端语音识别（如 Paraformer[3]、Whisper[4]）与大语言模型（如 Qwen[2]）显著提升了识别精度与对话质量；深度学习理论的发展[1][6][7]为上述技术提供了支撑。国内方面，智能镜产品逐步进入家庭与商用场景，但多数系统仍以信息展示为主，语音交互停留在固定指令层面，将大语言模型与多模态感知深度集成到镜面终端的研究与实践仍较少（详见文献综述）。"),
    ("h", "三、主要研究内容"),
    ("p", "本课题在树莓派平台上设计并实现Agent 智能镜子助手，主要研究内容如下："),
    ("p", "（1）系统总体设计。构建“硬件层—后端服务层—前端展示层”三层架构：硬件层包括树莓派、摄像头、麦克风阵列、扬声器、镜面显示屏及 PIR 传感器等外设；后端基于 Python 与 Flask 提供语音交互与感知识别服务；前端基于 MagicMirror² 与 Electron 实现镜面信息展示。"),
    ("p", "（2）语音交互闭环实现。包括：基于 Silero VAD 的本地语音活动检测与自定义唤醒词；语音识别采用云端 Qwen3-ASR 为主（Paraformer/百度备选），并以 SenseVoice-Small 端侧模型作为离线兜底，支持中文、英语等多语言转写；接入 Qwen3.6-Flash 大语言模型实现多轮上下文对话与助手人设管理（DeepSeek V4 备选）；接入火山引擎流式 TTS，支持情感音色与分段流式播放。"),
    ("p", "（3）感知与个性化。基于 PIR 传感器实现人体靠近自动唤醒；基于 dlib 实现人脸注册与实时识别，识别用户身份后进行个性化问候，并结合用户维护独立的对话上下文。"),
    ("p", "（4）镜面信息展示。基于 MagicMirror² 定制开发时钟、月历、和风天气实时展示、新闻滚动、节气与节日背景等模块。"),
    ("p", "（5）端侧轻量智能体。在树莓派本地部署 Qwen3.5-0.8B 量化模型（llama.cpp 常驻服务，--jinja 原生工具调用解析），构建含调度循环（单次请求工具调用上限 3 轮）、工具集（查今日任务/语音打卡/报时/查天气）与 SQLite 记忆（最近 6 轮上下文 + 长期事实库）的极简智能体；路由采用本地优先、云端兜底的三层容错策略（本地模型→关键词规则→云端大模型），保障断网时核心功能可用。"),
    ("p", "（6）个人任务管理集成。从飞书妙记拉取录音及其转写内容（增量轮询、游标去重，仅处理转写完成的记录），将文本交由云端大语言模型处理，自动整理为待办、日程、提醒、记事等条目并进入待确认队列，由用户在手机端确认后落地。处理位置的选择依据：转写内容提取对语义理解与结构化输出要求较高，量化小模型可靠性不足，且该环节无实时性要求、每日调用量小，故采用云端大模型处理（成本可忽略），树莓派侧仅承担同步调度、到点提醒与打卡等轻量逻辑，形成“云端重提取、端侧轻调度”的端云协同分工。在交互层，复用人脸识别实现个性化今日任务展示，任务到点且检测到有人时进行语音播报与镜面横幅提醒，无人时仅屏幕常驻显示；支持语音查询今日任务与语音打卡。"),
    ("p", "（7）系统测试与优化。开展功能测试、语音交互端到端延迟测量、长时间稳定性运行与断网离线场景验证，针对延迟与资源占用进行优化。"),
    ("h", "四、拟解决的关键问题"),
    ("p", "（1）资源受限设备上的多线程并发与调度：人体检测、人脸识别、语音交互等任务相互独立，需设计合理的线程模型，避免资源竞争导致的卡顿；"),
    ("p", "（2）端云协同下的响应延迟优化：ASR、LLM、TTS 均依赖云端服务，需通过流式分段合成播放、并行请求与合理的超时策略，将端到端延迟控制在 5 秒以内；"),
    ("p", "（3）唤醒可靠性：唤醒词采用关键词匹配存在误唤醒风险，需结合 VAD 置信度阈值与防抖策略降低误触发；"),
    ("p", "（4）模块化与可配置设计：多个 ASR/LLM/TTS 后端需要支持配置切换，需设计统一的配置管理与模块接口，使核心逻辑不与具体实现耦合。"),
    ("p", "（5）本地小模型的工具调用可靠性：量化小模型输出 JSON/工具格式错误率较高，需通过 llama.cpp 原生 tool_calls 解析与语法约束、失败重试及多层兜底路由保证智能体可用性。"),
    ("h", "五、研究方案与技术路线"),
    ("p", "硬件平台：树莓派 4（或 3B+）、单向透视镜与 HDMI 显示屏、USB 摄像头、麦克风阵列、扬声器、HC-SR501 PIR 传感器。"),
    ("p", "软件环境：后端采用 Python 3.8，基于 Flask 提供 Web 服务，使用 PyAudio 采集音频，配置统一由 config.yaml 管理，日志采用 loguru；前端采用 Node.js 与 MagicMirror² 框架并通过 Electron 封装为桌面应用；版本管理采用 Git。"),
    ("p", "技术路线：首先完成需求分析与总体方案设计；随后按“语音交互闭环→感知模块→信息展示→端侧智能体→个人任务管理集成”的顺序进行模块开发与单元测试；再将各模块集成到树莓派平台进行系统联调，测量端到端延迟、识别准确率与稳定性指标；最后针对测试暴露的问题进行优化，完成论文撰写。"),
    ("p", "测试方案：功能层面逐项验证语音交互、人脸识别、信息展示、端侧智能体工具调用、任务同步与提醒；性能层面统计从唤醒结束到 TTS 开始播报的端到端延迟（目标 ≤5 秒）；稳定性层面进行连续 72 小时运行观察与断网离线场景验证，记录异常与资源占用。"),
    ("p", "研究方法上，本课题综合采用四种方法：（1）文献研究法，通过检索国内外文献梳理智能镜面与语音交互技术的最新进展，为方案选型提供依据；（2）原型开发法，采用敏捷迭代方式，先构建最小可用原型，再逐步扩展与优化；（3）对比实验法，对不同的 ASR、LLM、TTS 后端在识别准确率、响应延迟与多语种支持等方面进行对比测试，选取性价比最优的配置组合；（4）指标量化法，以端到端延迟、唤醒成功率、人脸识别准确率、连续运行稳定性等量化指标评价系统，保证结论客观可复现。"),
    ("h", "六、可行性分析"),
    ("p", "（1）技术可行性：系统所依赖的 Silero VAD、dlib、MagicMirror² 均为成熟开源方案，ASR、LLM、TTS 均有稳定可用的云端 API，技术风险可控；本人已具备 Python 与前端开发基础。"),
    ("p", "（2）硬件可行性：所需硬件均为常见树莓派外设，价格适中，已具备开发套件。"),
    ("p", "（3）工作基础：课题依托大学生创新创业训练计划项目，系统主体功能已完成初步开发，具备完整的代码基础、产品需求文档与软件说明书，端侧智能体与任务管理集成已完成方案设计，研究工作可在既有基础上深化与完善。"),
    ("p", "（4）时间可行性：按进度安排，设计与开发集中在 2026 年 11 月至 2027 年 3 月完成，中期检查后有一个月以上时间用于论文撰写与完善，时间充裕。"),
    ("h", "七、进度安排"),
    ("p", "1. 2026.10.13—11.2：完成课题申报与选题，明确研究内容与技术路线；"),
    ("p", "2. 2026.11—2026.12：文献调研与需求分析，完成文献综述与开题报告；"),
    ("p", "3. 2027.1—2027.2：完成各功能模块的设计与开发（含端侧智能体与任务管理集成）；"),
    ("p", "4. 2027.3：系统集成与测试，完成外文文献翻译，完善开题材料并通过审查；"),
    ("p", "5. 2027.4：参加中期检查，撰写论文初稿；"),
    ("p", "6. 2027.5：论文修改定稿，完成查重与 AIGC 检测，制作答辩材料；"),
    ("p", "7. 2027.5.7—5.20：参加毕业答辩，按意见修改并归档。"),
    ("h", "八、预期成果"),
    ("p", "（1）可在树莓派样机上现场演示的Agent 智能镜子助手系统一套（含离线智能体、个性化任务展示、到点提醒与语音打卡）；（2）毕业论文一篇（正文不少于 8000 字）；（3）符合要求的外文文献翻译一篇；（4）文献综述与开题报告各一份。"),
]

def gen_proposal():
    doc = Document()
    setup_doc(doc)
    add_page_number(doc)

    title(doc, "毕业设计（论文）开题报告", size=22)
    para(doc, f"课题名称：{TOPIC}", indent=False, align=WD_ALIGN_PARAGRAPH.CENTER, after=2)
    para(doc, f"学生姓名：{STUDENT}　　学号：{STUDENT_ID}　　专业：通信工程　　指导教师：{ADVISOR}",
         size=10.5, indent=False, align=WD_ALIGN_PARAGRAPH.CENTER, after=12)  # 10.5pt 保证一行放下

    for kind, text in PROP_BODY:
        if kind == "h":
            heading(doc, text, size=14)
        else:
            para(doc, text)

    heading(doc, "九、主要参考文献", size=14)
    for ref in REFS:
        para(doc, ref, indent=False, size=10.5, after=3)

    doc.add_paragraph()
    para(doc, "学生（签字）：　　　　　　　　　　日期：　　　年　　月　　日", indent=False, after=12)
    para(doc, "指导教师意见：", indent=False, after=12)
    para(doc, "指导教师（签字）：　　　　　　　　日期：　　　年　　月　　日", indent=False)

    path = f"{OUT}/开题报告-基于树莓派的Agent智能镜子助手.docx"
    doc.save(path)
    cjk = sum(len(re.findall(r"[\u4e00-\u9fff]", t)) for k, t in PROP_BODY)
    return path, cjk

if __name__ == "__main__":
    p1 = gen_task_book()
    p2, n2 = gen_lit_review()
    p3, n3 = gen_proposal()
    print("OK")
    print("任务书:", p1)
    print(f"文献综述: {p2}  正文汉字数≈{n2}")
    print(f"开题报告: {p3}  正文汉字数≈{n3}")
