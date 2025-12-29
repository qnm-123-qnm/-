import streamlit as st
import random
import requests
from datetime import datetime

# -------------------------- 页面基础配置 --------------------------
st.set_page_config(
    page_title="ScholarMind - 学术灵感引擎",
    page_icon="📚",
    layout="wide",
    initial_sidebar_state="expanded"
)

# -------------------------- 自定义样式 --------------------------
st.markdown("""
<style>
    .stTextInput, .stSelectbox, .stTextArea {
        border-radius: 8px;
        border: 1px solid #e0e0e0;
    }
    .result-card {
        background-color: #f8f9fa;
        border-radius: 10px;
        padding: 20px;
        margin: 10px 0;
        border-left: 4px solid #2196f3;
    }
    .citation {
        font-family: monospace;
        font-size: 0.9em;
        color: #333;
        background-color: #f0f0f0;
        padding: 8px;
        border-radius: 4px;
    }
    .api-tip {
        font-size: 0.9em;
        color: #666;
        margin-top: 5px;
    }
</style>
""", unsafe_allow_html=True)

# -------------------------- 月之暗面API配置（HTTP调用） --------------------------
def call_moonshot_api(api_key, prompt, model="moonshot-v1-8k", temperature=0.7, max_tokens=500):
    """直接调用月之暗面API（兼容OpenAI接口格式）"""
    url = "https://api.moonshot.cn/v1/chat/completions"
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {api_key}"
    }
    data = {
        "model": model,
        "messages": [{"role": "user", "content": prompt}],
        "temperature": temperature,
        "max_tokens": max_tokens
    }
    try:
        response = requests.post(url, headers=headers, json=data, timeout=30)
        response.raise_for_status()  # 抛出HTTP错误
        return response.json()["choices"][0]["message"]["content"].strip()
    except Exception as e:
        st.warning(f"API调用失败，使用模拟数据：{str(e)}")
        return None

def verify_moonshot_key(api_key):
    """验证月之暗面API密钥有效性"""
    if not api_key:
        return False
    url = "https://api.moonshot.cn/v1/models"
    headers = {"Authorization": f"Bearer {api_key}"}
    try:
        response = requests.get(url, headers=headers, timeout=10)
        return response.status_code == 200
    except:
        return False

# -------------------------- 模拟学术数据（兜底用） --------------------------
CORE_LITERATURE = {
    "计算机科学/机器学习/大模型幻觉抑制": [
        ("Li et al., 2024", "《Hallucination Suppression in LLMs via Knowledge Grounding》",
         "IEEE Transactions on Pattern Analysis and Machine Intelligence"),
        ("Zhang et al., 2023", "《A Survey on Hallucination Detection in Large Language Models》",
         "ACM Computing Surveys"),
        ("Wang et al., 2022", "《Contrastive Learning for Reducing LLM Hallucinations》", "NeurIPS")
    ],
    "计算机科学/机器学习/小样本学习": [
        ("Chen et al., 2024", "《Few-Shot Learning with Prompt Enhancement》", "ICML"),
        ("Liu et al., 2023", "《Meta-Learning for Low-Resource Few-Shot Tasks》", "ICLR"),
        ("Zhao et al., 2022", "《Few-Shot Classification via Feature Alignment》", "CVPR")
    ],
    "默认": [
        ("Author et al., 2024", "《Research on Core Issues in This Field》", "Top Journal in the Field"),
        ("Author et al., 2023", "《A Comprehensive Review of Recent Advances》", "Key Conference Proceedings"),
        ("Author et al., 2022", "《Challenges and Future Directions》", "International Journal")
    ]
}

CITATION_FORMATS = {
    "APA 7th": "{authors} ({year}). {title}. {journal}.",
    "GB/T 7714": "{authors}. {title}[J]. {journal}, {year}.",
    "MLA 9th": "{authors}. \"{title}\". {journal}, vol. XX, no. XX, {year}, pp. XX-XX."
}

# -------------------------- 核心功能函数 --------------------------
def get_literature(field_key):
    return CORE_LITERATURE.get(field_key, CORE_LITERATURE["默认"])

def generate_topics(api_key, field, core_problem):
    """生成选题（月之暗面API优先，无则兜底）"""
    prompt = f"""
    你是资深学术研究员，基于以下信息生成3个创新、可行的学术选题：
    1. 学科领域：{field}
    2. 核心研究问题：{core_problem}
    3. 格式要求：选题需简洁专业，贴合当前研究热点，每行1个选题，示例：「基于知识锚定的大模型幻觉抑制方法研究」
    """
    # 调用月之暗面API
    api_result = call_moonshot_api(api_key, prompt, max_tokens=500)
    if api_result:
        topics = [t.strip() for t in api_result.split("\n") if t.strip()]
        return topics[:3] if topics else []
    
    # 兜底逻辑
    methods = ["知识锚定", "对比学习", "元学习", "提示增强", "特征对齐"]
    innovations = ["因果推理", "多模态融合", "轻量化模型", "人机协同"]
    cross_fields = ["认知心理学", "统计学", "博弈论"]
    templates = [
        "基于{method}的{field}低资源场景{problem}问题研究",
        "{field}中{problem}的可解释性增强方法：{innovation}视角",
        "融合{cross_field}思想的{field} {problem}解决方案与实证分析"
    ]
    return [
        template.format(
            method=random.choice(methods),
            field=field,
            problem=core_problem,
            innovation=random.choice(innovations),
            cross_field=random.choice(cross_fields)
        ) for template in templates
    ]

def generate_literature_review(api_key, field, core_problem, literature_list):
    """生成综述（月之暗面API优先，无则兜底）"""
    literature_str = "\n".join([f"{auth}: {title} ({journal})" for auth, title, journal in literature_list])
    prompt = f"""
    基于以下信息生成结构化的文献综述框架（约800字）：
    1. 学科领域：{field}
    2. 核心研究问题：{core_problem}
    3. 核心文献：{literature_str}
    4. 框架要求：包含「研究背景与意义」「国内外研究现状」「现有研究不足」「本文研究切入点」4部分，语言专业、逻辑清晰。
    """
    # 调用API
    api_result = call_moonshot_api(api_key, prompt, temperature=0.6, max_tokens=1000)
    if api_result:
        return api_result
    
    # 兜底逻辑
    return f"""
### 文献综述框架：{field} - {core_problem}
#### 1. 研究背景与意义
{field}作为人工智能领域的核心方向，近年来取得了快速发展，但{core_problem}问题仍制约着该领域的实际应用价值，亟待提出有效的解决方案。

#### 2. 国内外研究现状
##### 2.1 核心方法分类
- 基于数据增强的方法：代表文献{literature_list[0][0]}提出了{literature_list[0][1].split("《")[1].split("》")[0]}，通过{random.choice(["知识 grounding", "对比学习"])}缓解{core_problem}；
- 基于模型结构优化的方法：{literature_list[1][0]}的研究聚焦于{core_problem}的可解释性，提出了{random.choice(["元学习框架", "特征对齐策略"])}；
- 基于提示工程的方法：{literature_list[2][0]}探索了低资源场景下的{core_problem}解决思路，为后续研究提供了参考。

#### 3. 现有研究不足
- 现有方法在{random.choice(["低资源场景", "复杂任务"])}下性能显著下降；
- 缺乏对{core_problem}产生机制的深入分析与可解释性验证；
- 跨领域融合的解决方案尚未形成体系化研究。

#### 4. 本文研究切入点
针对上述不足，本研究拟从{random.choice(["多模态融合", "轻量化模型"])}视角出发，提出适用于{field}的{core_problem}解决方法。
    """

def generate_abstract(api_key, field, core_problem, topic):
    """生成摘要（月之暗面API优先，无则兜底）"""
    prompt = f"""
    基于以下信息生成规范的学术论文摘要（约300字）：
    1. 学科领域：{field}
    2. 核心研究问题：{core_problem}
    3. 研究选题：{topic}
    4. 要求：包含「研究背景」「研究方法」「实验结果」「研究结论」4部分，数据合理虚构，符合学术规范。
    """
    # 调用API
    api_result = call_moonshot_api(api_key, prompt, temperature=0.6, max_tokens=600)
    if api_result:
        return api_result
    
    # 兜底逻辑
    return f"""
### 论文摘要
**研究背景**：{field}是当前人工智能领域的研究热点，{core_problem}问题已成为制约该领域技术落地的关键瓶颈。现有方法在处理{random.choice(["低资源", "复杂场景"])}下的{core_problem}时，存在{random.choice(["性能不足", "可解释性差"])}等问题。
**研究方法**：本文提出了{topic.split("：")[-1] if "：" in topic else "一种基于新型框架的"}方法，通过{random.choice(["知识锚定", "特征对齐", "元学习"])}策略优化模型输出，增强对{core_problem}的抑制/解决能力。
**实验结果**：在{random.choice(["公开基准数据集", "自建数据集"])}上的实验表明，所提方法相较于{random.choice(["Li et al., 2024", "Zhang et al., 2023"])}的基线模型，{random.choice(["准确率提升12.5%", "幻觉率降低18.3%", "F1值提高9.7%"])}，验证了方法的有效性。
**研究结论**：该方法为解决{field}中的{core_problem}问题提供了新的思路，可进一步拓展至{random.choice(["多模态任务", "工业级应用场景"])}。
    """

def format_citation(literature, format_type):
    formatted_citations = []
    year = literature[0].split(", ")[1] if ", " in literature[0] else "2024"
    for auth, title, journal in literature:
        citation = CITATION_FORMATS[format_type].format(
            authors=auth,
            year=year,
            title=title,
            journal=journal
        )
        formatted_citations.append(citation)
    return formatted_citations

# -------------------------- 页面布局 --------------------------
st.sidebar.header("📋 研究参数配置")
field = st.sidebar.text_input("学科领域", placeholder="如：计算机科学/机器学习/大模型幻觉抑制")
research_basis = st.sidebar.selectbox("已有基础", ["已完成文献调研", "正在进行实验", "需确定选题"])
core_problem = st.sidebar.text_input("核心研究问题", placeholder="如：现有方法在低资源场景下性能下降")
citation_format = st.sidebar.selectbox("引用格式", ["APA 7th", "GB/T 7714", "MLA 9th"])
output_choice = st.sidebar.multiselect(
    "输出内容",
    ["创新选题建议", "文献综述框架", "论文摘要初稿"],
    default=["创新选题建议", "文献综述框架", "论文摘要初稿"]
)

# 月之暗面API密钥输入
st.sidebar.divider()
st.sidebar.header("🔑 月之暗面 API 配置")
api_key = st.sidebar.text_input(
    "API Key",
    type="password",
    placeholder="sk-sk-xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx",
    help="获取地址：https://platform.moonshot.cn"
)
# 密钥验证按钮
if st.sidebar.button("🔍 验证密钥"):
    if verify_moonshot_key(api_key):
        st.sidebar.success("✅ 密钥有效！")
    else:
        st.sidebar.error("❌ 密钥无效/过期！")
st.sidebar.markdown('<div class="api-tip">✅ 填写有效密钥可生成高质量学术内容，不填则用模拟数据</div>',
                    unsafe_allow_html=True)

generate_btn = st.sidebar.button("🚀 生成学术灵感", type="primary")

# 主页面
st.title("📚 ScholarMind 学术灵感引擎")
st.divider()

if generate_btn:
    if not field or not core_problem:
        st.error("⚠️ 请先填写「学科领域」和「核心研究问题」！")
    else:
        with st.spinner("正在生成学术内容，请稍候..."):
            literature = get_literature(field.strip())
            col1, col2 = st.columns([2, 1])
            with col1:
                st.subheader("🎯 创新选题建议")
                topics = generate_topics(api_key, field, core_problem)
                for i, topic in enumerate(topics, 1):
                    st.markdown(f"""
                    <div class="result-card">
                        <strong>选题{i}：</strong> {topic}
                    </div>
                    """, unsafe_allow_html=True)

                if "文献综述框架" in output_choice:
                    st.subheader("📖 文献综述框架")
                    review = generate_literature_review(api_key, field, core_problem, literature)
                    st.markdown(f'<div class="result-card">{review}</div>', unsafe_allow_html=True)

                if "论文摘要初稿" in output_choice:
                    st.subheader("📝 论文摘要初稿")
                    abstract = generate_abstract(api_key, field, core_problem, topics[0])
                    st.markdown(f'<div class="result-card">{abstract}</div>', unsafe_allow_html=True)

            with col2:
                st.subheader("📜 核心文献引用")
                formatted_cites = format_citation(literature, citation_format)
                for i, cite in enumerate(formatted_cites, 1):
                    st.markdown(f'<div class="citation">{i}. {cite}</div>', unsafe_allow_html=True)

                st.subheader("💾 导出内容")
                export_all = "\n\n".join([
                    "=== 创新选题建议 ===",
                    "\n".join(topics),
                    "=== 文献综述框架 ===",
                    review if "文献综述框架" in output_choice else "",
                    "=== 论文摘要初稿 ===",
                    abstract if "论文摘要初稿" in output_choice else "",
                    "=== 核心文献引用 ===",
                    "\n".join(formatted_cites)
                ])
                st.download_button(
                    label="下载全部内容（TXT）",
                    data=export_all,
                    file_name=f"ScholarMind_成果_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt",
                    mime="text/plain"
                )

st.divider()
st.caption("💡 提示：生成内容仅为学术灵感参考，需结合实际研究验证；API密钥仅在本次会话有效，不会存储。")
