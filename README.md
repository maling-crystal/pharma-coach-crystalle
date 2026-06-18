# pharma-coach-crystalle
import streamlit as st
import jieba

# ================= 1. 智能分析与评分模块 (保持不变) =================
class GROW_PFI_Analyzer:
    def __init__(self):
        self.grow_keywords = {
            1: ["目标", "期望", "希望达成", "这次拜访", "目的", "想要", "上次的计划"],
            2: ["现状", "具体发生了", "当时", "医生的反馈", "探寻", "聆听", "陈述", "传递", "怎么做的", "情况", "执行"],
            3: ["方案", "选择", "如果", "可以尝试", "疑虑", "同理", "处理", "探讨", "还有什么办法", "应对", "调整"],
            4: ["行动", "计划", "下一步", "跟进", "缔结", "承诺", "时间", "具体怎么做", "复盘", "再次跟进"]
        }
        self.pfi_keywords = ["访前计划", "观念分析", "SMART", "开场", "寒暄", "价值陈述", "探寻", "开放式", "封闭式", "增长机会", "积极聆听", "FAB", "特征利益", "差异化", "疑虑", "误解", "怀疑", "缺点", "澄清", "缔结", "总结", "行动方案", "跟进", "患者获益"]

    def analyze_and_score(self, user_input, current_stage):
        words = list(jieba.cut(user_input))
        score, feedback = 0, ""
        grow_kws = self.grow_keywords.get(current_stage, [])
        grow_hits = [w for w in words if w in grow_kws]
        if grow_hits:
            score += 30
            feedback += f"✅ GROW辅导行为：成功引导至 {['Goal','Reality','Options','Will'][current_stage-1]} 阶段。\n"
        else:
            score += 10
            feedback += f"❌ GROW辅导行为：未体现当前阶段应有的辅导动作。\n"

        pfi_hits = [w for w in words if w in self.pfi_keywords]
        if pfi_hits:
            score += 20 + min(10, len(pfi_hits) * 5)
            feedback += f"✅ PFI技巧聚焦：辅导紧扣专业拜访技能。\n"
        else:
            score += 10
            feedback += f"⚠️ PFI技巧聚焦：建议多使用PFI术语。\n"

        if "?" in user_input or "？" in user_input or "怎么" in user_input or "如何" in user_input:
            score += 20
            feedback += "✅ 启发式提问：运用提问引导代表自主反思。\n"
        else:
            feedback += "⚠️ 启发式提问：经理应多提问。\n"

        return max(0, min(100, score)), feedback

# ================= 2. 持续辅导场景模拟器 (多周期记忆) =================
class ContinuousCoachingSimulator:
    def __init__(self):
        # 场景设计了 2 个辅导周期，代表在第1周期的改变，会在第2周期成为新的现状
        self.scenarios = [
            {
                "title": "场景1: 从单向传递到探寻疑虑的持续转化 (张主任)",
                "cycles": [
                    { # 第一次辅导：发现问题，制定探寻方案
                        "intro": "代表反馈张主任习惯处方竞品，代表自认为传递了详尽的临床数据，但无效。",
                        "stage_reply": {
                            1: "经理，这次拜访张主任，我的目标是让他把我们产品加进二线方案。但我讲了很多数据，他还是没开处方。",
                            2: "我一进去就给他看了临床数据图表。他听完说竞品用了多年安全性有数。我没多问，又强调了一遍疗效。感觉他没在听。",
                            3: "他主要是觉得我们缺乏老年患者的长期安全性数据。我当时有点慌，不知道怎么接话。我是不是该直接换话题？",
                            4: "好的经理。我本周五前找医学部申请安全性亚组数据，下周二拜访时先用开放式问题探寻他门诊老年患者的现状，再用FAB做针对性回应。"
                        }
                    },
                    { # 第二次辅导：基于上次的承诺，代表尝试了探寻，但遇到了新的处理疑虑难题
                        "intro": "（距上次辅导一周后）代表执行了上周制定的“先探寻后传递”的计划，有了新进展，但也暴露了新问题。",
                        "stage_reply": {
                            1: "经理，上次您辅导后，我去拜访了张主任。我确实按计划先用开放式问题探寻了他对老年患者的顾虑，他愿意跟我多聊两句了。但最后还是没处方，我觉得目标还是没达成。",
                            2: "我按照计划递交了安全性亚组数据。他说'数据看着不错，但你们这药说明书上写着有肝肾功能受损的禁忌，我这部分患者不敢用'。我当时没准备这个疑问，只能说'我回去查查'，缔结得很仓促。",
                            3: "这次他不是怀疑疗效了，是针对禁忌症的'缺点'类疑虑。我是不是该找医学部明确一下轻中度肾损患者的用法用量？还是直接告诉他临床中这部分人群监测指标即可？",
                            4: "明白了。我明天找医学部确认轻中度肾损患者的剂量调整建议。后天去找张主任，用FAB话术说明在监测下的安全性保障，争取他开具首张处方。下周三我给您看处方照片。"
                        }
                    }
                ]
            }
        ]
        self.grow_pfi_mapping = {
            1: "【GROW: Goal】📍引导代表明确本次拜访目标(可回顾上次目标)",
            2: "【GROW: Reality】📍引导代表复盘PFI执行现状(探寻/传递/疑虑处理)",
            3: "【GROW: Options】📍探讨PFI方案(如何调整应对新问题)",
            4: "【GROW: Will】📍推动PFI缔结与跟进计划"
        }

    def get_intro(self, scenario_idx, cycle_idx):
        return self.scenarios[scenario_idx]["cycles"][cycle_idx]["intro"]

    def get_reply(self, scenario_idx, cycle_idx, stage):
        return self.scenarios[scenario_idx]["cycles"][cycle_idx]["stage_reply"].get(stage, "本轮辅导完成")

# ================= 3. 手机网页界面 (状态管理) =================
def main():
    st.set_page_config(page_title="持续辅导模拟器", page_icon="💊", layout="centered")
    
    # 初始化全局状态
    if 'initialized' not in st.session_state:
        st.session_state.initialized = True
        st.session_state.scenario_idx = 0
        st.session_state.cycle_idx = 0
        st.session_state.stage = 1
        st.session_state.score = 0
        st.session_state.history = []
        st.session_state.max_cycles = 2 # 设定最多辅导2个周期

    analyzer = GROW_PFI_Analyzer()
    simulator = ContinuousCoachingSimulator()

    st.title("💊 GROW × PFI 持续辅导模拟器")
    st.caption("模拟跨周期的代表辅导，追踪行为改变的持续过程")

    # 侧边栏：历史辅导档案
    with st.sidebar:
        st.header("📂 辅导档案")
        st.markdown(f"**当前场景:** {simulator.scenarios[st.session_state.scenario_idx]['title']}")
        st.markdown(f"**辅导周期:** 第 {st.session_state.cycle_idx + 1} 次 / 共 {st.session_state.max_cycles} 次")
        st.markdown(f"**累计得分:** {st.session_state.score}")
        if st.button("🔄 重置所有辅导进程", use_container_width=True):
            for key in st.session_state.keys():
                del st.session_state[key]
            st.rerun()

    # 显示当前辅导周期的背景信息
    current_intro = simulator.get_intro(st.session_state.scenario_idx, st.session_state.cycle_idx)
    if st.session_state.stage == 1 and len(st.session_state.history) == 0:
        if st.session_state.cycle_idx == 0:
            st.info(f"**【初次辅导背景】**\n\n{current_intro}\n\n---\n{simulator.grow_pfi_mapping[1]}")
        else:
            st.warning(f"**【第 {st.session_state.cycle_idx + 1} 次跟进辅导】**\n\n{current_intro}\n\n---\n{simulator.grow_pfi_mapping[1]}")

    # 进度条与指标
    total_stages = st.session_state.max_cycles * 4
    current_progress = (st.session_state.cycle_idx * 4 + st.session_state.stage) / total_stages
    st.progress(min(1.0, current_progress), text=f"整体辅导进度 (当前: 第{st.session_state.cycle_idx+1}轮 - {['Goal','Reality','Options','Will','完成'][st.session_state.stage-1]})")

    # 历史对话展示
    for msg in st.session_state.history:
        if msg['role'] == 'user':
            st.chat_message('user', avatar='👨‍💼').write(msg['content'])
        elif msg['role'] == 'bot':
            st.chat_message('assistant', avatar='💊').write(msg['content'])
        elif msg['role'] == 'feedback':
            st.success(msg['content'])

    # 输入区
    if st.session_state.stage <= 4:
        user_input = st.chat_input("输入你作为地区经理(DSM)的辅导话术...")
        if user_input:
            # 评分
            score, feedback = analyzer.analyze_and_score(user_input, st.session_state.stage)
            st.session_state.score += score
            
            st.session_state.history.append({'role': 'user', 'content': user_input})
            
            # 推进阶段
            st.session_state.stage += 1
            rep_reply = simulator.get_reply(st.session_state.scenario_idx, st.session_state.cycle_idx, st.session_state.stage - 1)
            
            feedback_text = f"📋 评估反馈:\n{feedback}\n本轮得分: +{score}"
            
            # 判断是否需要进入下一个辅导周期
            if st.session_state.stage > 4:
                if st.session_state.cycle_idx < st.session_state.max_cycles - 1:
                    feedback_text += f"\n\n🎉 **第 {st.session_state.cycle_idx + 1} 轮辅导完成！**\n代表将执行计划并在下次拜访中遇到新情况，请进入下一跟进周期。"
                else:
                    feedback_text += f"\n\n🎉 **全周期持续辅导完成！** 代表已实现行为转变并达成目标。"
            else:
                feedback_text += f"\n\n➡️ 下一阶段:\n{simulator.grow_pfi_mapping[st.session_state.stage]}"

            st.session_state.history.append({'role': 'feedback', 'content': feedback_text})
            st.session_state.history.append({'role': 'bot', 'content': f"【医药代表回应】: {rep_reply}"})
            st.rerun()
    
    # 周期切换按钮
    elif st.session_state.stage > 4 and st.session_state.cycle_idx < st.session_state.max_cycles - 1:
        if st.button("➡️ 开始下一周期的跟进辅导", type="primary", use_container_width=True):
            st.session_state.cycle_idx += 1
            st.session_state.stage = 1
            st.session_state.history = [] # 清空当前屏幕对话，保留侧边栏累计分数
            st.rerun()

if __name__ == "__main__":
    main()
