import streamlit as st
import pandas as pd
import itertools

# ==========================================
# 1. 核心配置与样式
# ==========================================

st.set_page_config(page_title="PTCG 战队 BP 助手 (Pro 4人版)", page_icon="🛡️", layout="wide")

# 颜色样式：根据 1-6 的数值上色
# 1=大优(绿) -> 6=大劣(红)
def get_color_style(val):
    if not isinstance(val, (int, float)): return ""
    if val <= 1.5: return "background-color: #22c55e; color: white" # 1: 深绿 (大优)
    if val <= 2.5: return "background-color: #86efac; color: #14532d" # 2: 浅绿 (小优)
    if val <= 3.5: return "background-color: #dbeafe; color: #1e3a8a" # 3: 蓝 (均势)
    if val <= 4.5: return "background-color: #fef08a; color: #713f12" # 4: 黄 (小劣)
    if val <= 5.5: return "background-color: #fca5a5; color: #7f1d1d" # 5: 橙红 (劣)
    return "background-color: #ef4444; color: white; font-weight: bold" # 6: 深红 (不想打)

# ==========================================
# 2. 默认数据
# ==========================================
#DEFAULT_DATA = [
#   { "player": "三毛九鬼龙", "deck": "鬼龙", "matchups": { "比雕恶喷": 2, "尾狸恶喷": 4, "沙奈朵": 3, "鬼龙": 5, "轰鬼": 5, "密勒顿": 4, "勾喷": 6, "LTB": 5, "纯恶轰明月": 6, "水轰明月": 6, "汇流梦幻": 5, "双无梦幻": 6, "水熊": 3, "炎帝铁武者": 2, "古剑豹": 6, "赛富豪": 3, "宙斯系列": 2, "洛奇亚": 6, "卡比兽": 2, "索罗": 2, "毛崖蟹": 2 } },
#    { "player": "土豆", "deck": "鬼龙", "matchups": { "比雕恶喷": 1, "尾狸恶喷": 3, "沙奈朵": 2, "鬼龙": 4, "轰鬼": 3, "密勒顿": 3, "勾喷": 5, "LTB": 4, "纯恶轰明月": 4, "水轰明月": 4, "汇流梦幻": 2, "双无梦幻": 4, "水熊": 2, "炎帝铁武者": 1, "古剑豹": 4, "赛富豪": 1, "宙斯系列": 1, "洛奇亚": 5, "卡比兽": 1, "索罗": 1, "毛崖蟹": 1 } },
#    { "player": "语申", "deck": "尾狸恶喷", "matchups": { "比雕恶喷": 5, "尾狸恶喷": 5, "沙奈朵": 4, "鬼龙": 6, "轰鬼": 6, "密勒顿": 1, "勾喷": 4, "LTB": 6, "纯恶轰明月": 1, "水轰明月": 1, "汇流梦幻": 1, "双无梦幻": 1, "水熊": 5, "炎帝铁武者": 4, "古剑豹": 3, "赛富豪": 5, "宙斯系列": 5, "洛奇亚": 1, "卡比兽": 6, "索罗": 6, "毛崖蟹": 6 } },
#    { "player": "ZZ", "deck": "沙奈朵", "matchups": { "比雕恶喷": 4, "尾狸恶喷": 2, "沙奈朵": 1, "鬼龙": 3, "轰鬼": 2, "密勒顿": 5, "勾喷": 1, "LTB": 3, "纯恶轰明月": 3, "水轰明月": 3, "汇流梦幻": 3, "双无梦幻": 2, "水熊": 4, "炎帝铁武者": 5, "古剑豹": 5, "赛富豪": 2, "宙斯系列": 4, "洛奇亚": 2, "卡比兽": 3, "索罗": 4, "毛崖蟹": 4 } },
#   { "player": "乐子人", "deck": "lostK喷", "matchups": { "比雕恶喷": 3, "尾狸恶喷": 1, "沙奈朵": 6, "鬼龙": 2, "轰鬼": 1, "密勒顿": 6, "勾喷": 3, "LTB": 2, "纯恶轰明月": 2, "水轰明月": 2, "汇流梦幻": 6, "双无梦幻": 5, "水熊": 6, "炎帝铁武者": 6, "古剑豹": 2, "赛富豪": 4, "宙斯系列": 6, "洛奇亚": 4, "卡比兽": 5, "索罗": 3, "毛崖蟹": 3 } },
#    { "player": "龟龟", "deck": "涡轮梦幻", "matchups": { "比雕恶喷": 6, "尾狸恶喷": 6, "沙奈朵": 5, "鬼龙": 1, "轰鬼": 4, "密勒顿": 2, "勾喷": 2, "LTB": 1, "纯恶轰明月": 5, "水轰明月": 5, "汇流梦幻": 4, "双无梦幻": 3, "水熊": 1, "炎帝铁武者": 3, "古剑豹": 1, "赛富豪": 6, "宙斯系列": 3, "洛奇亚": 3, "卡比兽": 4, "索罗": 5, "毛崖蟹": 5 } }
#]
DEFAULT_DATA = [
    { "player": "皇子", "deck": "白洛", "matchups": { "恶喷": 3, "沙奈朵": 3, "鬼龙": 3, "密勒顿": 3, "轰鸣月": 3, "赛富豪": 1, "双窝梦幻": 2, "古剑豹": 3, "洛奇亚": 3, "卡比兽": 1, "连击熊": 1, "炎帝": 3, "汇流梦幻": 3, "宙斯": 2, "团结之翼": 3 } },
    { "player": "奉先", "deck": "密勒顿", "matchups": { "恶喷": 3, "沙奈朵": 3, "鬼龙": 3, "密勒顿": 3, "轰鸣月": 3, "赛富豪": 3, "双窝梦幻": 4, "古剑豹": 2, "洛奇亚": 1, "卡比兽": 6, "连击熊": 4, "炎帝": 3, "汇流梦幻": 3, "宙斯": 3, "团结之翼": 1 } },
    { "player": "xtime", "deck": "ltb恶喷", "matchups": { "恶喷": 2, "沙奈朵": 3, "鬼龙": 4, "密勒顿": 2, "轰鸣月": 3, "赛富豪": 3, "双窝梦幻": 2, "古剑豹": 3, "洛奇亚": 3, "卡比兽": 6, "连击熊": 4, "炎帝": 2, "汇流梦幻": 1, "宙斯": 2, "团结之翼": 2 } },
    { "player": "ciaos", "deck": "轰鸣月", "matchups": { "恶喷": 3, "沙奈朵": 3, "鬼龙": 3, "密勒顿": 2, "轰鸣月": 3, "赛富豪": 3, "双窝梦幻": 2, "古剑豹": 2, "洛奇亚": 2, "卡比兽": 3, "连击熊": 1, "炎帝": 3, "汇流梦幻": 2, "宙斯": 1, "团结之翼": 1 } },
    { "player": "裤伽", "deck": "剑豹", "matchups": { "恶喷": 3, "沙奈朵": 3, "鬼龙": 3, "密勒顿": 2, "轰鸣月": 3, "赛富豪": 2, "双窝梦幻": 3, "古剑豹": 3, "洛奇亚": 3, "卡比兽": 3, "连击熊": 3, "炎帝": 3, "汇流梦幻": 3, "宙斯": 3, "团结之翼": 3 } }
]
# ==========================================
# 3. 核心算法 (推荐 4 人)
# ==========================================
def calculate_ban_pick(team_data, selected_opponents):
    results = {}
    
    # --- 1. Ban 计算 ---
    unique_opponents = list(set(selected_opponents))
    opponent_scores = {} 
    
    for opp_deck in unique_opponents:
        total_score = 0
        for member in team_data:
            rating = member['matchups'].get(opp_deck, member['matchups'].get("其它", 3))
            total_score += rating
        opponent_scores[opp_deck] = total_score
    
    if opponent_scores:
        ban_target = max(opponent_scores, key=opponent_scores.get)
        ban_reason_score = opponent_scores[ban_target]
    else:
        ban_target = None
        ban_reason_score = 0

    results['ban_target'] = ban_target
    results['ban_score'] = ban_reason_score

    # --- 2. Pick 计算 (选4个) ---
    remaining_opponents = selected_opponents.copy()
    if ban_target and ban_target in remaining_opponents:
        remaining_opponents.remove(ban_target)

    if not remaining_opponents:
        return results

    all_members = [m['player'] for m in team_data]
    # 修改：组合数改为 4
    combos_4 = list(itertools.combinations(all_members, 4))
    
    best_combo_4 = None
    best_score_4 = float('inf')

    # 寻找总分最低的 4 人组
    for combo in combos_4:
        current_combo_score = 0
        for player_name in combo:
            player_data = next(p for p in team_data if p['player'] == player_name)
            for opp_deck in remaining_opponents:
                rating = player_data['matchups'].get(opp_deck, player_data['matchups'].get("其它", 3))
                current_combo_score += rating
        
        if current_combo_score < best_score_4:
            best_score_4 = current_combo_score
            best_combo_4 = combo

    results['pick_combo'] = best_combo_4 # 这是一个 4 人元组
    results['remaining_opponents'] = remaining_opponents
    
    # --- 3. 风险评估 (Worst Case) ---
    # 在这 4 个人中，如果被 Ban 掉核心（对这 4 人中贡献最大的），剩下的 3 人表现如何？
    if best_combo_4:
        worst_case_score = float('-inf') # 找最坏情况
        worst_case_banned = None
        
        # 遍历这4个人，假设每人都可能被Ban
        for banned_player in best_combo_4:
            remaining_3 = [p for p in best_combo_4 if p != banned_player]
            
            # 计算这剩下的3人总分
            score_3 = 0
            for player_name in remaining_3:
                player_data = next(p for p in team_data if p['player'] == player_name)
                for opp_deck in remaining_opponents:
                    rating = player_data['matchups'].get(opp_deck, player_data['matchups'].get("其它", 3))
                    score_3 += rating
            
            # 如果分数变高（变差），说明这个被Ban的人很重要
            if score_3 > worst_case_score:
                worst_case_score = score_3
                worst_case_banned = banned_player
        
        results['risk_analysis'] = {
            'if_ban': worst_case_banned,
            'remaining_score': worst_case_score
        }

    return results

# ==========================================
# 4. 界面渲染
# ==========================================

st.title("🛡️ PTCG 战队 BP 助手 (Pro 4人版)")
st.caption("策略：推荐 4 名队友，防止对方 Ban 人导致阵容崩盘")

# 侧边栏：对手卡组选择
with st.sidebar:
    st.header("⚙️ 对局设置")
    
    # 提取所有对手
    all_possible_opponents = set()
    for member in DEFAULT_DATA:
        all_possible_opponents.update(member['matchups'].keys())
    sorted_opponents = sorted([x for x in all_possible_opponents if x != "其它"])
    
    selected_opponents = []
    default_values = ["沙奈朵", "鬼龙", "密勒顿", "赛富豪", "(无)", "(无)"]
    
    for i in range(6):
        options = ["(无)"] + sorted_opponents
        def_index = 0
        if i < len(default_values) and default_values[i] in options:
             def_index = options.index(default_values[i])
        
        deck = st.selectbox(f"对手卡组 #{i+1}", options=options, index=def_index, key=f"deck_select_{i}")
        if deck != "(无)":
            selected_opponents.append(deck)
            
# 主区域
if not selected_opponents:
    st.info("👈 请在左侧选择对手卡组")
else:
    # 表格
    st.subheader("📊 优劣势速览 (越绿越好)")
    table_data = []
    for member in DEFAULT_DATA:
        row = {"队员": f"{member['player']} ({member['deck']})"}
        for idx, opp in enumerate(selected_opponents):
            col_name = f"{opp} (#{idx+1})"
            rating = member['matchups'].get(opp, member['matchups'].get("其它", 3))
            row[col_name] = rating
        table_data.append(row)
    
    df = pd.DataFrame(table_data)
    df.set_index("队员", inplace=True)
    st.dataframe(df.style.map(get_color_style), use_container_width=True)

    st.markdown("---")
    st.subheader("🧠 AI 战术建议")
    
    analysis = calculate_ban_pick(DEFAULT_DATA, selected_opponents)
    
    col1, col2 = st.columns(2)
    with col1:
        st.markdown("### 🔴 建议 Ban")
        if analysis['ban_target']:
            st.error(f"**{analysis['ban_target']}**")
            st.write(f"威胁指数: **{analysis['ban_score']}**")
            st.write("理由：这是对方所有卡组中，对我方全体威胁最大的。")
        else:
            st.info("数据不足")

    with col2:
        st.markdown("### 🟢 建议 4 人名单")
        if analysis.get('pick_combo'):
            # 格式化输出 4 人名单
            combo = analysis['pick_combo']
            st.success("**" + " + ".join(combo) + "**")
            
            st.markdown("#### 🛡️ 抗压分析")
            risk = analysis.get('risk_analysis')
            if risk:
                st.write(f"如果对方 Ban 掉了 **{risk['if_ban']}** (最坏情况):")
                st.write(f"剩下的 3 人组合风险值为: **{risk['remaining_score']}**")
                st.caption("注：我们推荐这 4 个人，是因为即便被 Ban 掉核心，剩下的阵容依然是所有组合中最能打的。")
                
            if analysis['remaining_opponents']:
                 st.markdown("---")
                 st.caption(f"剩余需应对的对手: {', '.join(analysis['remaining_opponents'])}")
        else:
            st.info("请选择对手")
