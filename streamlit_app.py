import streamlit as st
import pandas as pd
import itertools

# ==========================================
# 1. 核心配置与样式
# ==========================================

st.set_page_config(page_title="Oi｜基拉祈祈愿", page_icon="🛡️", layout="wide")

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
# 2. 从 CSV 文件加载数据
# ==========================================

def load_data_from_file(file_path="data.csv"):
    """
    从 CSV 文件加载数据并转换为 DEFAULT_DATA 格式
    
    参数:
        file_path: CSV 文件路径，默认为 data.csv
    
    返回:
        列表，每个元素是队员的数据字典
    """
    try:
        # 读取 CSV 文件
        df = pd.read_csv(file_path, encoding='utf-8')
        
        # 转换数据格式
        default_data = []
        
        for _, row in df.iterrows():
            # 提取队员基本信息
            player_data = {
                "player": row["队员昵称"],
                "deck": row["使用卡组"],
                "matchups": {}
            }
            
            # 提取对阵评分数据（跳过前两列基本信息列）
            for col in df.columns[2:]:
                # 确保数值是整数
                player_data["matchups"][col] = int(row[col])
            
            default_data.append(player_data)
        
        return default_data
        
    except FileNotFoundError:
        st.error(f"❌ 数据文件 '{file_path}' 未找到")
        st.info("请确保在同一目录下创建 data.csv 文件")
        return None
    except Exception as e:
        st.error(f"❌ 读取数据文件时出错: {e}")
        return None

# 加载数据
DEFAULT_DATA = load_data_from_file()

# 如果数据加载失败，显示错误并停止运行
if DEFAULT_DATA is None:
    st.stop()

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

    results['pick_combo'] = best_combo_4
    results['remaining_opponents'] = remaining_opponents
    
    # --- 3. 风险评估 (Worst Case) ---
    if best_combo_4:
        worst_case_score = float('-inf')
        worst_case_banned = None
        
        for banned_player in best_combo_4:
            remaining_3 = [p for p in best_combo_4 if p != banned_player]
            
            score_3 = 0
            for player_name in remaining_3:
                player_data = next(p for p in team_data if p['player'] == player_name)
                for opp_deck in remaining_opponents:
                    rating = player_data['matchups'].get(opp_deck, player_data['matchups'].get("其它", 3))
                    score_3 += rating
            
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

st.title("🛡️ Oi｜基拉祈祈愿 战队 BP 助手")
st.caption("策略：推荐 4 名队友，防止对方 Ban 人导致阵容崩盘")

# 侧边栏：数据信息和对手卡组选择
with st.sidebar:
    st.header("⚙️ 对局设置")
    
    # 显示数据加载信息
    st.subheader("📁 数据信息")
    st.write(f"已加载 {len(DEFAULT_DATA)} 名队员数据")
    st.write(f"包含 {len(DEFAULT_DATA[0]['matchups'])} 种对手卡组")
    
    # 显示队员列表
    st.subheader("👥 当前队员")
    for member in DEFAULT_DATA:
        st.write(f"• {member['player']} ({member['deck']})")
    
    st.divider()
    
    # 提取所有对手卡组
    all_possible_opponents = set()
    for member in DEFAULT_DATA:
        all_possible_opponents.update(member['matchups'].keys())
    sorted_opponents = sorted([x for x in all_possible_opponents if x != "其它"])
    
    selected_opponents = []
    default_values = ["沙奈朵", "鬼龙", "恶喷", "密勒顿", "(无)", "(无)"]
    
    st.subheader("🎯 选择对手卡组")
    for i in range(6):
        options = ["(无)"] + sorted_opponents
        def_index = 0
        if i < len(default_values) and default_values[i] in options:
             def_index = options.index(default_values[i])
        
        deck = st.selectbox(f"对手卡组 #{i+1}", options=options, index=def_index, key=f"deck_select_{i}")
        if deck != "(无)":
            selected_opponents.append(deck)
    
    # 添加重新加载数据按钮
    if st.button("🔄 重新加载数据"):
        st.cache_data.clear()
        st.rerun()
            
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
