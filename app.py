import streamlit as st
import random
from datetime import datetime

# 初始化session state
if 'messages' not in st.session_state:
    st.session_state.messages = []
if 'current_scene' not in st.session_state:
    st.session_state.current_scene = "pre_visit_planning"
if 'manager_input' not in st.session_state:
    st.session_state.manager_input = ""
if 'ai_response' not in st.session_state:
    st.session_state.ai_response = ""

# 设置页面标题
st.set_page_config(page_title="地区经理辅导模拟器", layout="wide")
st.title("🎯 地区经理辅导模拟器 - AI对话版")

# 拜访流程场景定义
VISIT_SCENES = {
    "pre_visit_planning": {
        "title": "访前计划",
        "description": "准备拜访前的计划和准备",
        "manager_prompt": "作为地区经理，你需要帮助代表做好访前计划。请询问代表：'你这次拜访的目标医生是谁？你了解他的处方习惯吗？你准备了哪些资料？'",
        "ai_responses": [
            "我要拜访的是张医生，他是心内科的主任。我知道他主要处方竞品A，但我们的产品在安全性方面有优势。",
            "我准备了一些最新的临床数据，还有几个患者案例，希望能说服他尝试我们的产品。",
            "我已经了解了医生的需求，他最近对竞品的效果有些疑虑，这正是我们的机会。"
        ]
    },
    "smooth_opening": {
        "title": "顺利开场",
        "description": "建立良好关系，自然进入主题",
        "manager_prompt": "作为地区经理，你需要帮助代表做好开场。请询问代表：'你打算如何开场？如何建立良好的关系？'",
        "ai_responses": [
            "我会先问候医生，然后提到上次讨论的内容，自然过渡到今天的拜访目的。",
            "我会先聊一些轻松的话题，了解他最近的工作情况，然后再进入正题。",
            "我会直接说明今天的拜访目的，但会先表达对医生专业能力的尊重。"
        ]
    },
    "explore_needs": {
        "title": "探寻需求",
        "description": "深入了解医生的需求和痛点",
        "manager_prompt": "作为地区经理，你需要帮助代表探寻需求。请询问代表：'你打算如何探寻医生的需求？你会问哪些问题？'",
        "ai_responses": [
            "我会问医生目前使用竞品的情况，了解他的满意度和遇到的问题。",
            "我会询问医生对治疗效果的期望，以及他对我们产品的看法。",
            "我会通过几个具体问题，了解医生在处方决策时的考虑因素。"
        ]
    },
    "information_delivery": {
        "title": "信息传递",
        "description": "有效传递产品信息和价值",
        "manager_prompt": "作为地区经理，你需要帮助代表传递信息。请询问代表：'你打算如何传递产品信息？重点强调哪些优势？'",
        "ai_responses": [
            "我会重点介绍我们产品的临床优势，特别是安全性方面的数据。",
            "我会结合医生的需求，突出我们产品能解决他的具体问题。",
            "我会用患者案例来说明产品的实际效果，让医生更容易理解。"
        ]
    },
    "handle_objections": {
        "title": "异议处理",
        "description": "有效处理医生的异议和疑虑",
        "manager_prompt": "作为地区经理，你需要帮助代表处理异议。请询问代表：'如果医生提出价格异议，你会如何回应？'",
        "ai_responses": [
            "我会强调产品的长期价值，而不仅仅是价格。我们的产品虽然价格稍高，但效果更好，能减少患者的治疗成本。",
            "我会比较产品的总体成本效益，说明虽然单价高，但能带来更好的治疗效果和患者满意度。",
            "我会提供一些临床数据支持，证明产品的价值超过了价格差异。"
        ]
    },
    "close_effectively": {
        "title": "高效缔结",
        "description": "争取处方或下一步行动",
        "manager_prompt": "作为地区经理，你需要帮助代表缔结。请询问代表：'你打算如何争取处方？你会提出什么请求？'",
        "ai_responses": [
            "我会请求医生尝试处方我们的产品，并提供一些样品让医生体验。",
            "我会请求医生考虑在下次处方时优先考虑我们的产品，并约定下次拜访时间。",
            "我会请求医生参加我们的学术活动，进一步了解产品优势。"
        ]
    },
    "post_visit_analysis": {
        "title": "访后分析",
        "description": "总结拜访效果，制定改进计划",
        "manager_prompt": "作为地区经理，你需要帮助代表做访后分析。请询问代表：'你觉得这次拜访的效果如何？有什么可以改进的地方？'",
        "ai_responses": [
            "我觉得这次拜访很成功，医生对我们的产品有了更深入的了解，并表示愿意尝试。",
            "我觉得在探寻需求方面还可以做得更好，下次我会多问一些开放式问题。",
            "我觉得信息传递很有效，但异议处理还需要加强，下次我会准备更多应对策略。"
        ]
    }
}

# AI代表响应生成
def generate_ai_response(scene_key, manager_input):
    scene = VISIT_SCENES[scene_key]
    # 根据经理的输入选择合适的AI回应
    if "计划" in manager_input or "准备" in manager_input:
        return random.choice(scene["ai_responses"][:1])
    elif "开场" in manager_input or "关系" in manager_input:
        return random.choice(scene["ai_responses"][1:2])
    elif "需求" in manager_input or "痛点" in manager_input:
        return random.choice(scene["ai_responses"][2:3])
    elif "信息" in manager_input or "传递" in manager_input:
        return random.choice(scene["ai_responses"][3:4])
    elif "异议" in manager_input or "疑虑" in manager_input:
        return random.choice(scene["ai_responses"][4:5])
    elif "缔结" in manager_input or "处方" in manager_input:
        return random.choice(scene["ai_responses"][5:6])
    elif "分析" in manager_input or "总结" in manager_input:
        return random.choice(scene["ai_responses"][6:7])
    else:
        return random.choice(scene["ai_responses"])

# 场景选择器
st.sidebar.title("🎯 拜访流程场景")
selected_scene = st.sidebar.selectbox(
    "选择拜访阶段",
    list(VISIT_SCENES.keys()),
    format_func=lambda x: VISIT_SCENES[x]["title"]
)

# 场景信息显示
current_scene = VISIT_SCENES[selected_scene]
st.markdown(f"### 【{current_scene['title']}】")
st.markdown(f"**{current_scene['description']}**")

# 辅导进度
progress_value = (list(VISIT_SCENES.keys()).index(selected_scene) + 1) / len(VISIT_SCENES)
st.progress(progress_value, text=f"整体辅导进度(当前: 第{list(VISIT_SCENES.keys()).index(selected_scene)+1}轮 - {current_scene['title']}")

# 对话区域
st.subheader("🗣️ AI对话模拟")

# 地区经理的输入
st.markdown("#### 🎤 地区经理的对话输入")
manager_input = st.text_area("请输入地区经理的对话内容:", height=100, key="manager_input")

# 生成AI回应按钮
if st.button("🤖 生成AI回应"):
    if manager_input:
        # 生成AI回应
        ai_response = generate_ai_response(selected_scene, manager_input)
        
        # 添加到对话历史
        timestamp = datetime.now().strftime("%H:%M:%S")
        st.session_state.messages.append({
            "role": "地区经理",
            "content": manager_input,
            "timestamp": timestamp
        })
        st.session_state.messages.append({
            "role": "AI代表",
            "content": ai_response,
            "timestamp": timestamp
        })
        
        st.session_state.manager_input = ""
        st.session_state.ai_response = ai_response
    else:
        st.warning("请输入地区经理的对话内容")

# 显示对话历史
if st.session_state.messages:
    st.subheader("📝 对话历史")
    for message in st.session_state.messages[-10:]:  # 只显示最近10条
        with st.container():
            st.markdown(f"**{message['role']}** [{message['timestamp']}]")
            st.markdown(f"*{message['content']}*")
            st.markdown("---")

# 场景提示
st.markdown(f"### 💡 场景提示")
st.markdown(f"**地区经理提示**: {current_scene['manager_prompt']}")

# 对话分析
st.subheader("📊 对话分析")
if st.session_state.messages:
    manager_count = sum(1 for msg in st.session_state.messages if msg['role'] == '地区经理')
    ai_count = sum(1 for msg in st.session_state.messages if msg['role'] == 'AI代表')
    
    col1, col2 = st.columns(2)
    with col1:
        st.metric("地区经理发言次数", manager_count)
    with col2:
        st.metric("AI代表发言次数", ai_count)
    
    # 对话质量评分（简化版）
    if manager_count > 0 and ai_count > 0:
        quality_score = min(100, (ai_count / manager_count) * 80 + 20)
        st.progress(quality_score/100, text=f"对话质量评分: {quality_score:.1f}%")

# 使用说明
st.markdown("""
---
### 📖 使用说明

#### 基本功能：
1. **选择拜访阶段**：在左侧选择不同的拜访流程阶段
2. **输入对话内容**：在文本框中输入地区经理的对话
3. **生成AI回应**：点击按钮获取AI代表的回应
4. **查看对话历史**：显示之前的对话记录

#### 拜访流程：

**1. 访前计划** - 准备拜访前的计划和准备
**2. 顺利开场** - 建立良好关系，自然进入主题  
**3. 探寻需求** - 深入了解医生的需求和痛点
**4. 信息传递** - 有效传递产品信息和价值
**5. 异议处理** - 有效处理医生的异议和疑虑
**6. 高效缔结** - 争取处方或下一步行动
**7. 访后分析** - 总结拜访效果，制定改进计划

#### 辅导技巧建议：

**地区经理应该：**
- 针对每个阶段提供具体指导
- 提出开放式问题
- 提供具体的建议和策略
- 鼓励代表思考和反思

**AI代表特点：**
- 模拟真实临床医生的反应
- 根据场景生成合理的回应
- 提供多样化的回答选项

---

### 💡 示例对话：

**地区经理**: "你好，今天我想给你辅导一下访前计划这一趴，来做一些探讨。"
**AI代表**: "我要拜访的是张医生，他是心内科的主任。我知道他主要处方竞品A，但我们的产品在安全性方面有优势。"

**地区经理**: "你打算如何开场？如何建立良好的关系？"
**AI代表**: "我会先问候医生，然后提到上次讨论的内容，自然过渡到今天的拜访目的。"
""")

# 添加重置按钮
if st.button("🔄 重置对话"):
    st.session_state.messages = []
    st.session_state.manager_input = ""
    st.session_state.ai_response = ""
    st.success("对话已重置")
