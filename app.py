import streamlit as st
import jieba
from gtts import gTTS
import os
import tempfile
import base64
from io import BytesIO
import time
import random
from datetime import datetime

# 初始化session state
if 'messages' not in st.session_state:
    st.session_state.messages = []
if 'current_scene' not in st.session_state:
    st.session_state.current_scene = "goal_setting"
if 'manager_speech' not in st.session_state:
    st.session_state.manager_speech = ""
if 'representative_speech' not in st.session_state:
    st.session_state.representative_speech = ""
if 'conversation_history' not in st.session_state:
    st.session_state.conversation_history = []
if 'ai_assistant' not in st.session_state:
    st.session_state.ai_assistant = False

# 设置页面标题和描述
st.set_page_config(page_title="地区经理辅导模拟器", page_icon="🎙️", layout="wide")
st.title("🎙️ 地区经理辅导模拟器 - 高级版")

# 辅导场景定义
SCENES = {
    "goal_setting": {
        "title": "目标设定",
        "description": "引导代表明确本次拜访目标",
        "manager_prompt": "作为地区经理，你需要帮助代表明确本次拜访的具体目标。请询问代表：'这次拜访的主要目标是什么？你希望达成什么结果？'",
        "representative_response": "我希望能了解医生对竞品的看法，并争取获得更多处方机会。"
    },
    "situation_analysis": {
        "title": "情况分析",
        "description": "分析当前市场情况和挑战",
        "manager_prompt": "作为地区经理，你需要帮助代表分析当前市场情况。请询问代表：'你了解医生目前处方竞品的情况吗？有什么具体的挑战？'",
        "representative_response": "医生目前主要处方竞品A，认为我们的产品效果不如竞品。"
    },
    "options_review": {
        "title": "方案评估",
        "description": "评估可能的解决方案",
        "manager_prompt": "作为地区经理，你需要帮助代表评估解决方案。请询问代表：'针对这个情况，你有什么解决方案？你考虑过哪些策略？'",
        "representative_response": "我考虑过提供更多的临床数据，但不确定是否有效。"
    },
    "way_forward": {
        "title": "行动计划",
        "description": "制定具体的行动计划",
        "manager_prompt": "作为地区经理，你需要帮助代表制定行动计划。请询问代表：'基于以上分析，你计划如何调整你的拜访策略？下一步具体怎么做？'",
        "representative_response": "我计划准备更多的临床证据，并在下次拜访时重点强调我们的优势。"
    }
}

# 语音合成函数
def text_to_speech(text, lang='zh'):
    if not text:
        return None
    
    try:
        tts = gTTS(text=text, lang=lang)
        fp = BytesIO()
        tts.write_to_fp(fp)
        fp.seek(0)
        
        # 将音频转换为base64
        audio_base64 = base64.b64encode(fp.read()).decode()
        audio_html = f'<audio src="data:audio/mp3;base64,{audio_base64}" controls></audio>'
        return audio_html
    except Exception as e:
        st.error(f"语音合成失败: {str(e)}")
        return None

# AI助手响应生成（简化版）
def generate_ai_response(context, role):
    if role == "representative":
        responses = [
            "我理解您的意思，但我需要更多时间思考...",
            "根据我的经验，我认为应该...",
            "我同意您的观点，同时我想补充...",
            "让我想想，可能的解决方案是...",
            "我需要收集更多信息才能给出准确回答..."
        ]
        return random.choice(responses)
    return ""

# 场景选择器
st.sidebar.title("🎯 辅导场景")
selected_scene = st.sidebar.selectbox(
    "选择辅导阶段",
    list(SCENES.keys()),
    format_func=lambda x: SCENES[x]["title"]
)

# 场景信息显示
current_scene = SCENES[selected_scene]
st.markdown(f"### 【{current_scene['title']}】")
st.markdown(f"**{current_scene['description']}**")

# AI助手开关
st.session_state.ai_assistant = st.sidebar.checkbox("启用AI助手（模拟代表）", value=st.session_state.ai_assistant)

# 辅导进度
progress_value = (list(SCENES.keys()).index(selected_scene) + 1) / len(SCENES)
st.progress(progress_value, text=f"整体辅导进度(当前: 第{list(SCENES.keys()).index(selected_scene)+1}轮 - {current_scene['title']}")

# 对话区域
st.subheader("🗣️ 语音对话模拟")

# 地区经理的语音输入
st.markdown("#### 🎤 地区经理的语音输入")
manager_speech = st.text_area("请输入地区经理的对话内容:", height=120, key="manager_input")

# 代表的语音输入
st.markdown("#### 🎤 代表的语音输入")
if st.session_state.ai_assistant:
    st.info("AI助手已启用，代表将自动生成响应")
    representative_speech = generate_ai_response(manager_speech, "representative")
else:
    representative_speech = st.text_area("请输入代表的对话内容:", height=120, key="representative_input")

# 生成语音按钮
if st.button("🎵 生成语音对话"):
    if manager_speech:
        # 添加地区经理的对话
        manager_message = {
            "role": "地区经理",
            "content": manager_speech,
            "speech": text_to_speech(manager_speech),
            "timestamp": datetime.now().strftime("%H:%M:%S")
        }
        
        # 添加代表的对话
        if st.session_state.ai_assistant and not representative_speech:
            representative_speech = generate_ai_response(manager_speech, "representative")
        
        representative_message = {
            "role": "代表",
            "content": representative_speech,
            "speech": text_to_speech(representative_speech),
            "timestamp": datetime.now().strftime("%H:%M:%S")
        }
        
        # 添加到对话历史
        st.session_state.conversation_history.append(manager_message)
        st.session_state.conversation_history.append(representative_message)
        
        st.success("语音对话已生成！")
    else:
        st.warning("请输入地区经理的对话内容")

# 显示对话历史
if st.session_state.conversation_history:
    st.subheader("📝 对话历史")
    for message in st.session_state.conversation_history[-10:]:  # 只显示最近10条
        with st.container():
            st.markdown(f"**{message['role']}** [{message['timestamp']}]")
            st.markdown(f"*{message['content']}*")
            if message['speech']:
                st.markdown(message['speech'], unsafe_allow_html=True)
            st.markdown("---")

# 场景提示
st.markdown(f"### 💡 场景提示")
st.markdown(f"**地区经理提示**: {current_scene['manager_prompt']}")
if st.session_state.ai_assistant:
    st.markdown(f"**AI代表响应**: {current_scene['representative_response']}")

# 对话分析
st.subheader("📊 对话分析")
if st.session_state.conversation_history:
    manager_count = sum(1 for msg in st.session_state.conversation_history if msg['role'] == '地区经理')
    representative_count = sum(1 for msg in st.session_state.conversation_history if msg['role'] == '代表')
    
    col1, col2 = st.columns(2)
    with col1:
        st.metric("地区经理发言次数", manager_count)
    with col2:
        st.metric("代表发言次数", representative_count)
    
    # 对话质量评分（简化版）
    if manager_count > 0 and representative_count > 0:
        quality_score = min(100, (representative_count / manager_count) * 80 + 20)
        st.progress(quality_score/100, text=f"对话质量评分: {quality_score:.1f}%")

# 使用说明
st.markdown("""
---
### 📖 使用说明

#### 基本功能：
1. **选择辅导场景**：在左侧选择不同的辅导阶段
2. **输入对话内容**：在文本框中输入地区经理和代表的对话
3. **生成语音**：点击按钮将文本转换为语音并播放
4. **AI助手**：启用后代表会自动生成响应

#### 高级功能：
- **对话历史**：显示最近的对话记录
- **场景提示**：提供辅导建议和示例
- **对话分析**：分析对话质量和参与度

#### 技术特性：
- 支持中英文语音合成
- 实时对话记录
- 多场景辅导模拟
- AI辅助对话生成
- 对话质量分析

---

### 💡 辅导技巧建议

**地区经理应该：**
- 提出开放式问题
- 积极倾听代表观点
- 提供具体建议
- 鼓励代表思考

**代表应该：**
- 清晰表达观点
- 积极参与讨论
- 接受反馈
- 制定行动计划
""")

# 添加重置按钮
if st.button("🔄 重置对话"):
    st.session_state.conversation_history = []
    st.session_state.messages = []
    st.session_state.manager_speech = ""
    st.session_state.representative_speech = ""
    st.success("对话已重置")
