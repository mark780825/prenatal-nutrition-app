
import streamlit as st
from auth import login  # 你需要準備 auth.py 並內含 login(email, password) 函式
import base64
from PIL import Image

# ===== 使用者登入驗證 =====
if "user" not in st.session_state:
    st.set_page_config(page_title="登入", layout="centered")
    st.title("🔐 登入系統")
    email = st.text_input("Email")
    password = st.text_input("密碼", type="password")
    if st.button("登入"):
        user = login(email, password)
        if user:
            st.session_state.user = user
            st.rerun()
        else:
            st.error("登入失敗，請檢查帳號密碼")
else:
    # === 頁面設定 ===
    st.set_page_config(page_title="孕婦營養補充品劑量評估", layout="wide")

    # === 登出功能 ===
    with st.sidebar:
        st.markdown(f"👤 使用者：{st.session_state.user['email']}")
        if st.button("🚪 登出"):
            del st.session_state["user"]
            st.rerun()

    # ✅ 營養素清單（含單位）
    NUTRIENTS = [
        "鈣(mg)", "鐵(mg)", "鎂(mg)", "鋅(mg)", "碘(mcg)", "維生素A(IU)", "維生素D(IU)", "維生素E(IU)", "維生素C(mg)",
        "膽鹼(mg)", "維生素B6(mg)", "維生素B12(mg)", "葉酸(mcg)", "Omega-3(mg)"
    ]

    # ✅ 建議攝取量表
    DOSAGE_INFO = {
        "鈣(mg)": {"recommended": 500, "aggressive": 1500, "upper": 2500},
        "鐵(mg)": {"recommended": 0, "aggressive": 40, "upper": 40},
        "鎂(mg)": {"recommended": 75, "aggressive": 350, "upper": 350},
        "鋅(mg)": {"recommended": 5, "aggressive": 15, "upper": 35},
        "碘(mcg)": {"recommended": 25, "aggressive": 150, "upper": 1000},
        "維生素A(IU)": {"recommended": 0, "aggressive": 1200, "upper": 5000},
        "維生素D(IU)": {"recommended": 400, "aggressive": 2000, "upper": 4000},
        "維生素E(IU)": {"recommended": 0, "aggressive": 20, "upper": 400},
        "維生素C(mg)": {"recommended": 0, "aggressive": 200, "upper": 2000},
        "膽鹼(mg)": {"recommended": 150, "aggressive": 600, "upper": 7500},
        "維生素B6(mg)": {"recommended": 0, "aggressive": 10, "upper": 100},
        "維生素B12(mg)": {"recommended": 0, "aggressive": 25, "upper": float("inf")},
        "葉酸(mcg)": {"recommended": 400, "aggressive": 600, "upper": 1000},
        "Omega-3(mg)": {"recommended": 200, "aggressive": 1000, "upper": 2000},
    }

    if "products" not in st.session_state:
        st.session_state.products = []

    def add_product():
        st.session_state.products.append({
            "name": f"產品 {len(st.session_state.products)+1}",
            "ingredients": {n: 0.0 for n in NUTRIENTS},
            "count": 1
        })

    def delete_product(index):
        st.session_state.products.pop(index)

    def image_to_base64(image_path):
        with open(image_path, "rb") as f:
            return base64.b64encode(f.read()).decode()

    logo_base64 = image_to_base64("logo.png")
    st.markdown(f"""
    <div style="display:flex;align-items:center;gap:20px;">
        <img src="data:image/png;base64,{logo_base64}" style="width:200px;height:200px;border-radius:12px;" />
        <h1 style="margin:0;">孕婦營養補充品攝取量評估工具</h1>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("## 🤰🏻 選擇孕期")
    trimester = st.radio("請選擇目前懷孕階段", ["第1～2孕期（1–28週）", "第3孕期（29週以後）"])
    if trimester == "第1～2孕期（1–28週）":
        DOSAGE_INFO["鐵(mg)"]["recommended"] = 0
        DOSAGE_INFO["鐵(mg)"]["aggressive"] = 15
        DOSAGE_INFO["膽鹼(mg)"]["recommended"] = 150
        DOSAGE_INFO["膽鹼(mg)"]["aggressive"] = 350
    else:
        DOSAGE_INFO["鐵(mg)"]["recommended"] = 30
        DOSAGE_INFO["鐵(mg)"]["aggressive"] = 40
        DOSAGE_INFO["膽鹼(mg)"]["recommended"] = 150
        DOSAGE_INFO["膽鹼(mg)"]["aggressive"] = 600

    st.markdown("## 💊 輸入補充產品內容")
    st.button("➕ 新增產品", on_click=add_product)

    for i, product in enumerate(st.session_state.products):
        with st.expander(f"{product['name']}", expanded=True):
            cols = st.columns([3, 1])
            product["name"] = cols[0].text_input("產品名稱", value=product["name"], key=f"name_{i}")
            if cols[1].button("🗑️ 刪除", key=f"delete_{i}"):
                delete_product(i)
                st.rerun()

            nutrient_cols = st.columns(4)
            for j, nutrient in enumerate(NUTRIENTS):
                with nutrient_cols[j % 4]:
                    val = st.number_input(f"{nutrient}", min_value=0.0, step=0.1, value=product["ingredients"].get(nutrient, 0.0), key=f"{nutrient}_{i}")
                    product["ingredients"][nutrient] = val

            product["count"] = st.number_input("每日服用顆數", min_value=1, step=1, value=product["count"], key=f"count_{i}")

    st.markdown("---")
    st.markdown("## 📊 總攝取量評估結果")

    total_intake = {n: 0.0 for n in NUTRIENTS}
    source_detail = {n: [] for n in NUTRIENTS}

    for p in st.session_state.products:
        for n in NUTRIENTS:
            dose = p["ingredients"][n] * p["count"]
            total_intake[n] += dose
            if dose > 0:
                source_detail[n].append(f"{p['name']} ({dose:.1f})")

    strong = ["鈣(mg)", "鐵(mg)", "碘(mcg)", "維生素D(IU)", "葉酸(mcg)", "Omega-3(mg)"]
    optional = [n for n in NUTRIENTS if n not in strong]

    def show_nutrient_block(title, nutrients, bg_color):
        st.markdown(f"<div style='background-color:{bg_color};padding:10px 20px;border-radius:10px;margin-top:1rem;'><h4 style='margin:0;'>{title}</h4></div>", unsafe_allow_html=True)
        for n in nutrients:
            total = total_intake[n]
            info = DOSAGE_INFO[n]
            sources = "，來源：" + "、".join(source_detail[n]) if source_detail[n] else ""

            if info["upper"] == float("inf"):
                if total < info["recommended"]:
                    color = "🔴 **未達建議量**"
                elif total < info["aggressive"]:
                    color = "🔵 建議補充範圍"
                else:
                    color = "🟢 積極補充（無上限）"
            else:
                if total < info["recommended"]:
                    color = "🔴 **未達建議量**"
                elif total < info["aggressive"]:
                    color = "🔵 建議補充範圍"
                elif total < info["upper"]:
                    color = "🟢 積極補充範圍"
                else:
                    color = "🔺 **超過上限**"

            st.write(f"{n}: {total:.1f} → {color}{sources}")

    show_nutrient_block("🟥 強烈建議補充（核心營養素）", strong, "#ffeeee")
    show_nutrient_block("🟦 次要建議補充（補足加分項）", optional, "#eaf4ff")
