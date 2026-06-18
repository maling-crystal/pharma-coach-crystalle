import streamlit as st
import random
from datetime import datetime
import base64
import numpy as np
import plotly.graph_objects as go
import pandas as pd

# 初始化session state
if 'analysis_complete' not in st.session_state:
    st.session_state.analysis_complete = False
if 'scores' not in st.session_state:
    st.session_state.scores = {
        "goal_setting": {"score": 0, "details": {}},
        "situation_analysis": {"score": 0, "details": {}},
        "options_review": {"score": 0, "details": {}},
        "way_forward": {"score": 0, "details": {}}
    }
if 'feedback' not in st.session_state:
    st.session_state.feedback = {}
if 'audio_file' not in st.session_state:
    st.session_state.audio_file = None

# 设置页面标题
st.set_page_config(page_title="地区经理辅导反馈工具", layout="wide")
st.title("🎯 地区经理辅导反馈工具")

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

# 模拟音频分析（实际应用中这里会有真实的语音分析）
def analyze_audio(audio_file):
    # 模拟分析过程 - 实际应用中这里会有语音识别和内容分析
    st.info("正在分析音频内容...")
    
    # 模拟分析结果
    analysis_results = {
        "goal_setting": {
            "score": random.randint(60, 90),
            "details": {
                "specific": random.randint(60, 90),
                "measurable": random.randint(60, 90),
                "achievable": random.randint(60, 90),
                "relevant": random.randint(60, 90),
                "time_bound": random.randint(60, 90)
            }
        },
        "situation_analysis": {
            "score": random.randint(60, 90),
            "details": {
                "current_state": random.randint(60, 90),
                "challenges": random.randint(60, 90),
                "strengths": random.randint(60, 90),
                "weaknesses": random.randint(60, 90)
            }
        },
        "options_review": {
            "score": random.randint(60, 90),
            "details": {
                "creativity": random.randint(60, 90),
                "feasibility": random.randint(60, 90),
                "impact": random.randint(60, 90),
                "resources": random.randint(60, 90)
            }
        },
        "way_forward": {
            "score": random.randint(60, 90),
            "details": {
                "specific_actions": random.randint(60, 90),
                "responsibility": random.randint(60, 90),
                "timeline": random.randint(60, 90),
                "support": random.randint(60, 90),
                "monitoring": random.randint(60, 90)
            }
        }
    }
    
    return analysis_results

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

# 生成柱状图
def generate_bar_chart(scores):
    categories = list(GROW_DIMENSIONS.keys())
    values = [scores[cat]["score"] for cat in categories]
    
    fig = go.Figure(data=[go.Bar(
        x=categories,
        y=values,
        marker_color='royalblue'
    )])
    
    fig.update_layout(
        title={
            'text': "GROW各维度评分对比",
            'font': {'size': 20}
        },
        yaxis=dict(
            range=[0, 100],
            tickvals=[0, 25, 50, 75, 100],
            ticktext=['0', '25', '50', '75', '100']
        ),
        height=400,
        width=500
    )
    
    return fig

# 音频文件上传区域
st.subheader("🎤 音频文件上传")
uploaded_file = st.file_uploader("请上传地区经理的辅导录音文件", type=["wav", "mp3", "m4a"])

if uploaded_file:
    st.audio(uploaded_file, format="audio/wav")
    
    if st.button("📊 分析音频并评分"):
        # 模拟分析过程
        with st.spinner("正在分析音频内容..."):
            # 这里可以添加实际的语音分析代码
            # 由于Streamlit Cloud限制，我们使用模拟数据
            analysis_results = analyze_audio(uploaded_file)
            
            # 更新session state
            st.session_state.scores = analysis_results
            st.session_state.feedback = generate_feedback(analysis_results)
            st.session_state.audio_file = uploaded_file
            st.session_state.analysis_complete = True
        
        st.rerun()

# 显示分析结果
if st.session_state.analysis_complete:
    st.subheader("📊 分析结果")
    
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
    
    # 显示蛛网图
    st.plotly_chart(generate_radar_chart(st.session_state.scores), use_container_width=True)
    
    # 显示柱状图
    st.plotly_chart(generate_bar_chart(st.session_state.scores), use_container_width=True)
    
    # 显示详细反馈
    st.subheader("💡 详细反馈")
    for grow_key, feedback_data in st.session_state.feedback.items():
        grow_title = GROW_DIMENSIONS[grow_key]["title"]
        st.markdown(f"### {grow_title}")
        st.markdown(f"**{feedback_data['overall']}**")
        for dim_feedback in feedback_data["dimensions"]:
            st.markdown(dim_feedback)
        st.markdown("---")

# 使用说明
st.markdown("""
---
### 📖 使用说明

#### 基本功能：
1. **上传音频文件**：选择地区经理的辅导录音文件
2. **分析评分**：点击按钮进行分析和评分
3. **查看结果**：查看GROW评分、蛛网图和详细反馈

#### 评分系统：
- **GROW四大项**：目标设定、现状分析、方案评估、行动计划
- **蛛网图**：直观显示各项技能的强弱项
- **柱状图**：显示各维度评分对比
- **详细反馈**：针对每个维度提供具体的改进建议

#### 注意事项：
- 支持的音频格式：WAV, MP3, M4A
- 分析过程可能需要一些时间
- 目前使用模拟数据分析，实际应用中可以集成真实的语音分析

#### 示例分析：
上传一段地区经理的辅导录音后，系统会分析其辅导技巧，包括：
- 目标设定是否清晰明确
- 现状分析是否全面
- 方案评估是否合理
- 行动计划是否具体可行
""")

# 添加重置按钮
if st.button("🔄 重置分析"):
    st.session_state.analysis_complete = False
    st.session_state.scores = {
        "goal_setting": {"score": 0, "details": {}},
        "situation_analysis": {"score": 0, "details": {}},
        "options_review": {"score": 0, "details": {}},
        "way_forward": {"score": 0, "details": {}}
    }
    st.session_state.feedback = {}
    st.session_state.audio_file = None
    st.success("分析已重置")
