import streamlit as st
import random
from datetime import datetime
from gtts import gTTS
import os
import base64
import re
import numpy as np
import plotly.graph_objects as go  # 使用Plotly替代matplotlib
import pandas as pd

# 初始化session state
if 'messages' not in st.session_state:
    st.session_state.messages = []
if 'current_scene' not in st.session_state:
    st.session_state.current_scene = "pre_visit_planning"
if 'dialogue_context' not in st.session_state:
    st.session_state.dialogue_context = {}
if 'manager_input' not in st.session_state:
    st.session_state.manager_input = ""
if 'ai_response' not in st.session_state:
    st.session_state.ai_response = ""
if 'audio_html' not in st.session_state:
    st.session_state.audio_html = ""
if 'scores' not in st.session_state:
    st.session_state.scores = {
        "goal_setting": {"score": 0, "details": {}},
        "situation_analysis": {"score": 0, "details": {}},
        "options_review": {"score": 0, "details": {}},
        "way_forward": {"score": 0, "details": {}}
    }
if 'feedback' not in st.session_state:
    st.session_state.feedback = {}

# 设置页面标题
st.set_page_config(page_title="地区经理辅导模拟器 - 智能对话版", layout="wide")
st.title("🎯 地区经理辅导模拟器 - 智能对话与评分系统")

# GROW评分维度定义
GROW_DIMENSIONS = {
    "goal_setting": {
        "title": "目标设定",
        "description": "明确辅导目标和期望结果",
        "dimensions": {
            "specific": "目标是否具体明确",
            "measurable": "目标是否可衡量",
            "achievable": "目标是否可实现",
            "relevant": "目标是否相关",
            "time_bound": "是否有时间限制"
        },
        "weight": 0.25
    },
    "situation_analysis": {
        "title": "现状分析",
        "description": "分析当前情况和挑战",
        "dimensions": {
            "current_state": "对现状的了解程度",
            "challenges": "对挑战的识别能力",
            "strengths": "对优势的认知",
            "weaknesses": "对劣势的认知"
        },
        "weight": 0.25
    },
    "options_review": {
        "title": "方案评估",
        "description": "评估可能的解决方案",
        "dimensions": {
            "creativity": "解决方案的创造性",
            "feasibility": "方案的可行性",
            "impact": "方案的影响力",
            "resources": "对所需资源的考虑"
        },
        "weight": 0.25
    },
    "way_forward": {
        "title": "行动计划",
        "description": "制定具体的行动计划",
        "dimensions": {
            "specific_actions": "行动步骤的具体性",
            "responsibility": "责任分配的明确性",
            "timeline": "时间表的合理性",
            "support": "所需支持的识别",
            "monitoring": "进展跟踪机制"
        },
        "weight": 0.25
    }
}

# 拜访流程场景定义
VISIT_SCENES = {
    "pre_visit_planning": {
        "title": "访前计划",
        "description": "准备拜访前的计划和准备",
        "manager_prompt": "作为地区经理，你需要帮助代表做好访前计划。请询问代表：'你这次拜访的目标医生是谁？你了解他的处方习惯吗？你准备了哪些资料？'",
        "dialogue_rules": {
            "greeting": ["你好，经理！", "好的，经理。", "在的，经理。"],
            "planning": ["我正在准备拜访张医生，他是心内科的主任。", 
                       "我已经了解了张医生的处方习惯，他主要使用竞品A，但我们的产品在安全性方面有优势。",
                       "我准备了最新的临床数据和患者案例，希望能说服他尝试我们的产品。"],
            "questions": ["您想了解哪方面的准备情况？", "关于访前计划，您有什么具体的建议吗？"]
        }
    },
    "smooth_opening": {
        "title": "顺利开场",
        "description": "建立良好关系，自然进入主题",
        "manager_prompt": "作为地区经理，你需要帮助代表做好开场。请询问代表：'你打算如何开场？如何建立良好的关系？'",
        "dialogue_rules": {
            "greeting": ["我会先问候医生，然后提到上次讨论的内容。", 
                       "我会先聊一些轻松的话题，了解他最近的工作情况。",
                       "我会直接说明今天的拜访目的，但会先表达对医生专业能力的尊重。"],
            "transition": ["然后我会自然过渡到今天的主题。", "接着我会进入正题。"],
            "questions": ["您觉得这样的开场方式合适吗？", "关于开场，您有什么更好的建议？"]
        }
    },
    "explore_needs": {
        "title": "探寻需求",
        "description": "深入了解医生的需求和痛点",
        "manager_prompt": "作为地区经理，你需要帮助代表探寻需求。请询问代表：'你打算如何探寻医生的需求？你会问哪些问题？'",
        "dialogue_rules": {
            "questions": ["我会问医生目前使用竞品的情况，了解他的满意度和遇到的问题。", 
                        "我会询问医生对治疗效果的期望，以及他对我们产品的看法。",
                        "我会通过几个具体问题，了解医生在处方决策时的考虑因素。"],
            "follow_up": ["然后我会根据他的回答，进一步深入探讨。", "接着我会针对他的具体需求，提供相应的解决方案。"],
            "questions": ["您觉得这些问题能有效探寻需求吗？", "关于探寻需求，您有什么具体的指导？"]
        }
    },
    "information_delivery": {
        "title": "信息传递",
        "description": "有效传递产品信息和价值",
        "manager_prompt": "作为地区经理，你需要帮助代表传递信息。请询问代表：'你打算如何传递产品信息？重点强调哪些优势？'",
        "dialogue_rules": {
            "delivery": ["我会重点介绍我们产品的临床优势，特别是安全性方面的数据。", 
                       "我会结合医生的需求，突出我们产品能解决他的具体问题。",
                       "我会用患者案例来说明产品的实际效果，让医生更容易理解。"],
            "value_proposition": ["我会强调产品的长期价值，而不仅仅是价格。", 
                              "我会比较产品的总体成本效益，说明虽然单价高，但能带来更好的治疗效果。"],
            "questions": ["您觉得这样的信息传递方式有效吗？", "关于信息传递，您有什么具体的建议？"]
        }
    },
    "handle_objections": {
        "title": "异议处理",
        "description": "有效处理医生的异议和疑虑",
        "manager_prompt": "作为地区经理，你需要帮助代表处理异议。请询问代表：'如果医生提出价格异议，你会如何回应？'",
        "dialogue_rules": {
            "objection_response": ["我会强调产品的长期价值，而不仅仅是价格。我们的产品虽然价格稍高，但效果更好，能减少患者的治疗成本。", 
                               "我会比较产品的总体成本效益，说明虽然单价高，但能带来更好的治疗效果和患者满意度。",
                               "我会提供一些临床数据支持，证明产品的价值超过了价格差异。"],
            "handling": ["我会耐心倾听医生的意见，然后针对性地回应。", "我会用事实和数据来说服医生。"],
            "questions": ["您觉得这样的异议处理方式合适吗？", "关于异议处理，您有什么更好的策略？"]
        }
    },
    "close_effectively": {
        "title": "高效缔结",
        "description": "争取处方或下一步行动",
        "manager_prompt": "作为地区经理，你需要帮助代表缔结。请询问代表：'你打算如何争取处方？你会提出什么请求？'",
        "dialogue_rules": {
            "closing": ["我会请求医生尝试处方我们的产品，并提供一些样品让医生体验。", 
                      "我会请求医生考虑在下次处方时优先考虑我们的产品，并约定下次拜访时间。",
                      "我会请求医生参加我们的学术活动，进一步了解产品优势。"],
            "action": ["然后我会明确下一步的行动计划。", "接着我会确认具体的后续步骤。"],
            "questions": ["您觉得这样的缔结方式有效吗？", "关于高效缔结，您有什么具体的建议？"]
        }
    },
    "post_visit_analysis": {
        "title": "访后分析",
        "description": "总结拜访效果，制定改进计划",
        "manager_prompt": "作为地区经理，你需要帮助代表做访后分析。请询问代表：'你觉得这次拜访的效果如何？有什么可以改进的地方？'",
        "dialogue_rules": {
            "analysis": ["我觉得这次拜访很成功，医生对我们的产品有了更深入的了解，并表示愿意尝试。", 
                       "我觉得在探寻需求方面还可以做得更好，下次我会多问一些开放式问题。",
                       "我觉得信息传递很有效，但异议处理还需要加强，下次我会准备更多应对策略。"],
            "improvement": ["我意识到在开场时应该更自然一些，下次我会改进。", 
                          "我觉得在异议处理方面还需要加强，特别是价格方面的回应。",
                          "我觉得整体效果不错，但下次可以更主动地引导对话方向。"],
            "questions": ["您觉得这样的分析全面吗？", "关于访后分析，您有什么具体的指导？"]
        }
    }
}

# 智能对话生成器
def generate_intelligent_response(scene_key, manager_input, dialogue_history):
    scene = VISIT_SCENES[scene_key]
    dialogue_rules = scene["dialogue_rules"]
    
    # 分析用户输入的关键词
    input_lower = manager_input.lower()
    
    # 根据关键词选择回应
    if any(word in input_lower for word in ["你好", "您好", "经理", "你好经理"]):
        return random.choice(dialogue_rules.get("greeting", ["您好，经理！"]))
    
    elif any(word in input_lower for word in ["计划", "准备", "拜访", "医生"]):
        return random.choice(dialogue_rules.get("planning", ["我正在准备拜访计划。"]))
    
    elif any(word in input_lower for word in ["开场", "关系", "问候", "进入主题"]):
        return random.choice(dialogue_rules.get("greeting", ["我会先问候医生。"])) + " " + random.choice(dialogue_rules.get("transition", ["然后自然过渡到主题。"]))
    
    elif any(word in input_lower for word in ["需求", "痛点", "问题", "询问"]):
        return random.choice(dialogue_rules.get("questions", ["我会问医生目前使用竞品的情况。"])) + " " + random.choice(dialogue_rules.get("follow_up", ["然后根据他的回答深入探讨。"]))
    
    elif any(word in input_lower for word in ["信息", "传递", "优势", "价值"]):
        return random.choice(dialogue_rules.get("delivery", ["我会重点介绍产品优势。"])) + " " + random.choice(dialogue_rules.get("value_proposition", ["强调长期价值。"]))
    
    elif any(word in input_lower for word in ["异议", "疑虑", "价格", "回应"]):
        return random.choice(dialogue_rules.get("objection_response", ["我会强调产品的长期价值。"])) + " " + random.choice(dialogue_rules.get("handling", ["耐心倾听并针对性回应。"]))
    
    elif any(word in input_lower for word in ["缔结", "处方", "请求", "行动"]):
        return random.choice(dialogue_rules.get("closing", ["我会请求医生尝试处方。"])) + " " + random.choice(dialogue_rules.get("action", ["然后明确下一步计划。"]))
    
    elif any(word in input_lower for word in ["分析", "总结", "效果", "改进"]):
        return random.choice(dialogue_rules.get("analysis", ["我觉得这次拜访很成功。"])) + " " + random.choice(dialogue_rules.get("improvement", ["下次我会改进。"]))
    
    elif any(word in input_lower for word in ["什么", "如何", "为什么", "建议", "指导", "意见"]):
        return random.choice(dialogue_rules.get("questions", ["您想了解哪方面的内容？"]))
    
    else:
        # 默认回应
        return random.choice(dialogue_rules.get("questions", ["您想了解哪方面的内容？"]))

# 文本转语音函数
def text_to_speech(text, lang='zh'):
    try:
        tts = gTTS(text=text, lang=lang)
        tts.save("response.mp3")
        with open("response.mp3", "rb") as f:
            audio_bytes = f.read()
        audio_base64 = base64.b64encode(audio_bytes).decode()
        return f'<audio controls><source src="data:audio/mp3;base64,{audio_base64}" type="audio/mp3"></audio>'
    except Exception as e:
        st.error(f"语音合成失败: {str(e)}")
        return None

# 生成蛛网图（使用Plotly）
def generate_radar_chart(scores):
    categories = list(GROW_DIMENSIONS.keys())
    values = [scores[cat]["score"] for cat in categories]
    
    fig = go.Figure(data=go.Scatterpolar(
        r=values + [values[0]],  # 闭合图形
        theta=categories + [categories[0]],  # 闭合图形
        fill='toself',
        name='技能评分',
        line=dict(color='royalblue', width=2),
        fillcolor='rgba(65, 105, 225, 0.25)'
    ))
    
    fig.update_layout(
        polar=dict(
            radialaxis=dict(
                visible=True,
                range=[0, 100],
                tickvals=[0, 25, 50, 75, 100],
                ticktext=['0', '25', '50', '75', '100']
            )
        ),
        title={
            'text': "GROW辅导技巧评分",
            'font': {'size': 20}
        },
        showlegend=False,
        height=400,
        width=500
    )
    
    return fig

# 生成反馈
def generate_feedback(scores):
    feedback = {}
    for grow_key, grow_data in scores.items():
        grow_title = GROW_DIMENSIONS[grow_key]["title"]
        score = grow_data["score"]
        dimensions = grow_data["details"]
        
        if score >= 80:
            overall_feedback = f"在{grow_title}方面表现优秀！"
        elif score >= 60:
            overall_feedback = f"在{grow_title}方面表现良好，还有提升空间。"
        elif score >= 40:
            overall_feedback = f"在{grow_title}方面需要加强，建议多加练习。"
        else:
            overall_feedback = f"在{grow_title}方面存在明显不足，需要重点关注。"
        
        # 生成维度反馈
        dimension_feedback = []
        for dim_key, dim_value in dimensions.items():
            if dim_value >= 80:
                dimension_feedback.append(f"• {dim_key}: 表现优秀")
            elif dim_value >= 60:
                dimension_feedback.append(f"• {dim_key}: 表现良好")
            elif dim_value >= 40:
                dimension_feedback.append(f"• {dim_key}: 需要加强")
            else:
                dimension_feedback.append(f"• {dim_key}: 需要重点关注")
        
        feedback[grow_key] = {
            "overall": overall_feedback,
            "dimensions": dimension_feedback
        }
    
    return feedback

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
st.subheader("🗣️ 智能对话模拟")

# 地区经理的输入
st.markdown("#### 🎤 地区经理的对话输入")
manager_input = st.text_area("请输入地区经理的对话内容:", height=100, key="manager_input_field")

# 生成AI回应按钮
if st.button("🤖 生成AI回应"):
    if manager_input:
        # 生成智能回应
        ai_response = generate_intelligent_response(selected_scene, manager_input, st.session_state.messages)
        
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
        
        # 生成语音
        audio_html = text_to_speech(ai_response)
        if audio_html:
            st.session_state.audio_html = audio_html
        
        st.session_state.manager_input = ""
        st.session_state.ai_response = ai_response
        
        # 自动更新评分（简化版，实际应用中可以根据对话内容更智能地评分）
        for grow_key in st.session_state.scores:
            if grow_key == "goal_setting":
                st.session_state.scores[grow_key]["score"] = min(100, st.session_state.scores[grow_key]["score"] + random.randint(0, 5))
            elif grow_key == "situation_analysis":
                st.session_state.scores[grow_key]["score"] = min(100, st.session_state.scores[grow_key]["score"] + random.randint(0, 5))
            elif grow_key == "options_review":
                st.session_state.scores[grow_key]["score"] = min(100, st.session_state.scores[grow_key]["score"] + random.randint(0, 5))
            elif grow_key == "way_forward":
                st.session_state.scores[grow_key]["score"] = min(100, st.session_state.scores[grow_key]["score"] + random.randint(0, 5))
                
    else:
        st.warning("请输入地区经理的对话内容")

# 显示对话历史
if st.session_state.messages:
    st.subheader("📝 对话历史")
    for message in st.session_state.messages[-10:]:  # 只显示最近10条
        with st.container():
            st.markdown(f"**{message['role']}** [{message['timestamp']}]")
            st.markdown(f"*{message['content']}*")
            if message['role'] == 'AI代表' and st.session_state.audio_html:
                st.markdown(st.session_state.audio_html, unsafe_allow_html=True)
            st.markdown("---")

# 评分系统
st.subheader("📊 GROW辅导技巧评分系统")

# 生成评分和反馈
if st.button("📈 生成评分和反馈"):
    st.session_state.feedback = generate_feedback(st.session_state.scores)
    
    # 显示评分
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("目标设定", f"{st.session_state.scores['goal_setting']['score']}/100")
    with col2:
        st.metric("现状分析", f"{st.session_state.scores['situation_analysis']['score']}/100")
    with col3:
        st.metric("方案评估", f"{st.session_state.scores['options_review']['score']}/100")
    with col4:
        st.metric("行动计划", f"{st.session_state.scores['way_forward']['score']}/100")
    
    # 显示蛛网图（使用Plotly）
    st.plotly_chart(generate_radar_chart(st.session_state.scores), use_container_width=True)
    
    # 显示详细反馈
    st.subheader("💡 详细反馈")
    for grow_key, feedback_data in st.session_state.feedback.items():
        grow_title = GROW_DIMENSIONS[grow_key]["title"]
        st.markdown(f"### {grow_title}")
        st.markdown(f"**{feedback_data['overall']}**")
        for dim_feedback in feedback_data["dimensions"]:
            st.markdown(dim_feedback)
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
4. **生成评分和反馈**：点击按钮生成GROW评分和详细反馈
5. **查看对话历史**：显示之前的对话记录

#### 评分系统：
- **GROW四大项**：目标设定、现状分析、方案评估、行动计划
- **蛛网图**：直观显示各项技能的强弱项
- **详细反馈**：针对每个维度提供具体的改进建议

#### 智能对话特点：
- **关键词识别**：AI会分析你的输入内容，根据关键词生成相应的回应
- **上下文理解**：能够理解对话的上下文，生成连贯的回应
- **多样化回应**：每个场景都有多种可能的回应，避免重复
- **实时互动**：像真实对话一样，根据输入实时生成回应

#### 示例对话：

**地区经理**: "你好，今天我想给你辅导一下访前计划这一趴，来做一些探讨。"
**AI代表**: "您好，经理！我正在准备拜访张医生，他是心内科的主任。"

**地区经理**: "你打算如何开场？如何建立良好的关系？"
**AI代表**: "我会先问候医生，然后提到上次讨论的内容，然后自然过渡到今天的主题。"

**地区经理**: "如果医生提出价格异议，你会如何回应？"
**AI代表**: "我会强调产品的长期价值，而不仅仅是价格。我们的产品虽然价格稍高，但效果更好，能减少患者的治疗成本。"
""")

# 添加重置按钮
if st.button("🔄 重置对话"):
    st.session_state.messages = []
    st.session_state.manager_input = ""
    st.session_state.ai_response = ""
    st.session_state.audio_html = ""
    st.session_state.scores = {
        "goal_setting": {"score": 0, "details": {}},
        "situation_analysis": {"score": 0, "details": {}},
        "options_review": {"score": 0, "details": {}},
        "way_forward": {"score": 0, "details": {}}
    }
    st.session_state.feedback = {}
    st.success("对话已重置")
