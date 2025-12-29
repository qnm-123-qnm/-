import streamlit as st
import random
from datetime import datetime
from langchain.chat_models import ChatOpenAI
from langchain.prompts import ChatPromptTemplate
from langchain.schema.output_parser import StrOutputParser

# -------------------------- 页面基础配置（小红书风格） --------------------------
st.set_page_config(
    page_title="小红书文案助手✨",
    page_icon="🍠",
    layout="wide",
    initial_sidebar_state="expanded"
)

# -------------------------- 小红书风格自定义样式 --------------------------
st.markdown("""
<style>
    /* 整体风格 */
    .stApp {
        background-color: #fdf2f8;
    }
    /* 卡片样式 */
    .note-card {
        background-color: #ffffff;
        border-radius: 16px;
        padding: 20px;
        margin: 10px 0;
        box-shadow: 0 2px 10px rgba(0,0,0,0.05);
        border: 1px solid #fef7fb;
    }
    /* 标题样式 */
    .title-style {
        color: #e53e3e;
        font-weight: 700;
        font-size: 1.2em;
        margin-bottom: 8px;
    }
    /* 正文样式 */
    .content-style {
        color: #2d3748;
        line-height: 1.6;
        font-size: 1em;
    }
    /* 标签样式 */
    .tag-style {
        color: #9f7aea;
        font-size: 0.9em;
        display: inline-block;
        background-color: #fcf1f7;
        padding: 4px 10px;
        border-radius: 20px;
        margin: 4px 4px;
    }
    /* 按钮样式 */
    .stButton>button {
        background-color: #ed8936;
        color: white;
        border-radius: 10px;
        border: none;
        padding: 8px 20px;
    }
    .stButton>button:hover {
        background-color: #dd6b20;
    }
    /* 输入框样式 */
    .stTextInput, .stSelectbox, .stTextArea {
        border-radius: 10px;
        border: 1px solid #f0e6eb;
        padding: 10px;
    }
</style>
""", unsafe_allow_html=True)


# -------------------------- LangChain 配置月之暗面API --------------------------
def init_moonshot_llm(api_key):
    """初始化LangChain封装的月之暗面LLM"""
    if not api_key:
        st.warning("⚠️ 未填写API密钥，将使用模拟文案生成内容")
        return None

    try:
        llm = ChatOpenAI(
            model_name="moonshot-v1-8k",
            temperature=0.8,  # 更高随机性，适配小红书文案风格
            openai_api_key=api_key,
            openai_api_base="https://api.moonshot.cn/v1"
        )
        # 验证LLM可用性
        test_prompt = ChatPromptTemplate.from_messages([("user", "测试")])
        test_chain = test_prompt | llm | StrOutputParser()
        test_chain.invoke({})
        st.success("✅ 小红书文案引擎已激活！")
        return llm
    except Exception as e:
        st.error(f"❌ API初始化失败：{str(e)}")
        return None


# -------------------------- 模拟文案数据（兜底用） --------------------------
# 标题模板（按场景分类）
TITLE_TEMPLATES = {
    "好物分享": [
        "挖到宝了✨{topic}真的太好用了！",
        "无限回购的{topic}，谁用谁知道👍",
        "均价XX的{topic}，学生党闭眼冲💸"
    ],
    "美妆教程": [
        "新手必学✨{topic}化妆技巧，手残党也会！",
        "超简单的{topic}教程，5分钟搞定出门妆💄",
        "踩雷无数总结的{topic}干货，快码住📝"
    ],
    "旅行攻略": [
        "人均500玩转{topic}✨，避坑指南收好！",
        "{topic}小众玩法，本地人都不知道🤫",
        "3天2晚{topic}攻略，不绕路不踩雷🚗"
    ],
    "职场干货": [
        "打工人必看✨{topic}高效工作法，效率翻倍！",
        "月薪3k到1w，{topic}帮我少走2年弯路💼",
        "超实用的{topic}技巧，老板都夸会做事👍"
    ],
    "情感文案": [
        "治愈系✨{topic}，放过自己才是最好的和解",
        "关于{topic}，我终于想通了💛",
        "写给所有女生：{topic}才是人生的必修课🌷"
    ]
}

# 正文模板
CONTENT_TEMPLATES = {
    "元气少女": "宝子们！今天一定要给你们安利{topic}😭！我真的用了好久，亲测巨好用！\n\n先说优点👉\n1. 颜值超在线，拍照巨出片📸\n2. 性价比绝了，学生党也能冲💸\n3. 效果超预期，用一次就爱上✨\n\n真的闭眼入不亏，信我！",
    "高冷拽姐": "{topic}，没必要讨好所有人。\n\n好用就留，不好用就换，人生嘛，开心最重要😎\n\n试过很多同款，还是这个最合心意，懂的都懂。\n\n不废话，值得入。",
    "温柔治愈": "慢慢发现，{topic}教会我的，是和生活和解💛。\n\n不用急着求结果，不用逼自己完美，一点点进步就很好。\n\n愿我们都能在{topic}里，找到属于自己的小美好✨。",
    "搞笑沙雕": "家人们谁懂啊🤣！{topic}真的笑不活了！\n\n本来以为踩雷，结果真香现场！\n\n我宣布，{topic}就是我的年度快乐源泉，笑到邻居来敲门😂！",
    "专业干货": "深度测评{topic}，纯干货无广📝！\n\n核心优势：\n1. 核心逻辑：XXX\n2. 实操步骤：XXX\n3. 避坑要点：XXX\n\n总结：适合XX人群，性价比⭐⭐⭐⭐。"
}

# 标签模板
TAG_TEMPLATES = {
    "好物分享": ["好物分享", "平价好物", "学生党必备", "无限回购", "开箱", "性价比", "生活好物", "宝藏单品", "购物分享",
                 "自用推荐"],
    "美妆教程": ["美妆教程", "新手化妆", "化妆技巧", "平价彩妆", "美妆干货", "手残党化妆", "妆容教程", "底妆教程",
                 "眼妆教程", "美妆分享"],
    "旅行攻略": ["旅行攻略", "小众旅行地", "自由行", "旅游攻略", "避坑指南", "性价比旅行", "周末去哪儿", "国内旅行",
                 "旅行日记", "拍照攻略"],
    "职场干货": ["职场干货", "高效工作", "打工人", "职场技巧", "升职加薪", "办公技巧", "职场生存法则", "副业赚钱",
                 "自我提升", "职场经验"],
    "情感文案": ["情感文案", "治愈系", "女性成长", "自我和解", "生活感悟", "正能量", "情绪价值", "内心强大",
                 "成长型思维", "温柔文案"]
}


# -------------------------- 核心功能函数（小红书文案生成） --------------------------
def generate_xhs_title(llm, scene, topic, style):
    """生成小红书标题（3个）"""
    if llm:
        prompt_template = ChatPromptTemplate.from_messages([
            ("system", f"你是小红书爆款文案专家，擅长生成{style}风格的吸睛标题，带emoji，每句话不超过20字，每行1个。"),
            ("user", f"""生成3个{scene}类别的小红书标题，主题是{topic}，风格{style}：
示例：挖到宝了✨平价粉底液真的太好用了！""")
        ])
        chain = prompt_template | llm | StrOutputParser()
        try:
            result = chain.invoke({"scene": scene, "topic": topic, "style": style})
            titles = [t.strip() for t in result.split("\n") if t.strip() and len(t) <= 20]
            return titles[:3] if titles else []
        except Exception as e:
            st.warning(f"标题生成失败，使用模拟数据：{str(e)}")

    # 兜底逻辑
    base_templates = TITLE_TEMPLATES.get(scene, TITLE_TEMPLATES["好物分享"])
    return [template.format(topic=topic) for template in base_templates]


def generate_xhs_content(llm, scene, topic, style):
    """生成小红书正文"""
    if llm:
        prompt_template = ChatPromptTemplate.from_messages([
            ("system",
             f"你是小红书爆款文案专家，擅长写{style}风格的正文，带emoji，分段清晰，字数300-500字，符合小红书阅读习惯。"),
            ("user", f"""写一篇{scene}类别的小红书正文，主题是{topic}，风格{style}，要求：
1. 开头吸睛，有代入感
2. 中间分点/分段讲核心内容
3. 结尾有互动（比如提问/呼吁）
4. 带合适的emoji，不要堆砌""")
        ])
        chain = prompt_template | llm | StrOutputParser()
        try:
            return chain.invoke({"scene": scene, "topic": topic, "style": style})
        except Exception as e:
            st.warning(f"正文生成失败，使用模拟数据：{str(e)}")

    # 兜底逻辑
    return CONTENT_TEMPLATES.get(style, CONTENT_TEMPLATES["元气少女"]).format(topic=topic)


def generate_xhs_tags(llm, scene, topic):
    """生成小红书标签（10个）"""
    if llm:
        prompt_template = ChatPromptTemplate.from_messages([
            ("system", "你是小红书运营专家，擅长生成高匹配度的标签，带#，10个左右，包含核心词+长尾词。"),
            ("user", f"""生成{scene}类别的小红书标签，主题是{topic}，格式：#标签1 #标签2 #标签3...""")
        ])
        chain = prompt_template | llm | StrOutputParser()
        try:
            result = chain.invoke({"scene": scene, "topic": topic})
            tags = [t.replace("#", "").strip() for t in result.split() if t.strip()]
            return tags[:10] if tags else []
        except Exception as e:
            st.warning(f"标签生成失败，使用模拟数据：{str(e)}")

    # 兜底逻辑
    return TAG_TEMPLATES.get(scene, TAG_TEMPLATES["好物分享"])


# -------------------------- 页面布局（小红书风格） --------------------------
# 侧边栏：文案参数配置
st.sidebar.header("🍠 文案参数配置")
scene = st.sidebar.selectbox(
    "文案场景",
    ["好物分享", "美妆教程", "旅行攻略", "职场干货", "情感文案"],
    index=0
)
topic = st.sidebar.text_input("核心主题", placeholder="如：平价粉底液/厦门旅行/职场沟通技巧")
style = st.sidebar.selectbox(
    "文案风格",
    ["元气少女", "高冷拽姐", "温柔治愈", "搞笑沙雕", "专业干货"],
    index=0
)

# 月之暗面API配置
st.sidebar.divider()
st.sidebar.header("🔑 AI引擎配置")
api_key = st.sidebar.text_input(
    "月之暗面API Key",
    type="password",
    placeholder="sk-sk-xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx",
    help="获取地址：https://platform.moonshot.cn"
)
if st.sidebar.button("🔍 验证密钥"):
    init_moonshot_llm(api_key)

st.sidebar.markdown("💡 填写密钥可生成定制化爆款文案，不填则用模拟数据", unsafe_allow_html=True)

# 生成按钮
generate_btn = st.sidebar.button("✨ 生成小红书文案", type="primary")

# 主页面标题
st.title("🍠 小红书文案助手")
st.caption("一键生成爆款标题+正文+标签，适配小红书流量逻辑～")
st.divider()

# 文案生成结果展示
if generate_btn:
    if not topic:
        st.error("⚠️ 请先填写「核心主题」！")
    else:
        # 初始化LLM
        llm = init_moonshot_llm(api_key)
        with st.spinner("正在生成爆款文案..."):
            # 生成文案组件
            titles = generate_xhs_title(llm, scene, topic, style)
            content = generate_xhs_content(llm, scene, topic, style)
            tags = generate_xhs_tags(llm, scene, topic)

            # 布局：标题区 + 正文区 + 标签区
            col1, col2 = st.columns([1, 2])

            with col1:
                st.subheader("🔥 吸睛标题（选1个）")
                for i, title in enumerate(titles, 1):
                    st.markdown(f"""
                    <div class="note-card">
                        <div class="title-style">标题{i}：{title}</div>
                    </div>
                    """, unsafe_allow_html=True)

            with col2:
                st.subheader("✍️ 正文文案")
                st.markdown(f"""
                <div class="note-card">
                    <div class="content-style">{content}</div>
                </div>
                """, unsafe_allow_html=True)

                st.subheader("🏷️ 推荐标签")
                tags_html = "".join([f'<span class="tag-style">#{tag}</span>' for tag in tags])
                st.markdown(f"""
                <div class="note-card">
                    {tags_html}
                </div>
                """, unsafe_allow_html=True)

                # 一键复制功能
                full_copy = f"""【小红书文案】\n标题：{titles[0]}\n\n正文：\n{content}\n\n标签：{" ".join([f"#{t}" for t in tags])}"""
                st.button("📋 一键复制全部文案", on_click=lambda: st.code(full_copy, language="text"))

                # 导出功能
                export_content = full_copy
                st.download_button(
                    label="💾 导出文案（TXT）",
                    data=export_content,
                    file_name=f"小红书文案_{topic}_{datetime.now().strftime('%Y%m%d')}.txt",
                    mime="text/plain"
                )

# 底部提示
st.divider()
st.caption("💡 提示：生成文案可根据需求微调，标签建议保留3-5个核心词，流量效果更佳～")