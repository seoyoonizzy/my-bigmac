import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="국가별 가격지도", layout="wide")
st.title("🗺️ 국가별 빅맥 가격 & 구매력 지도")
st.caption("나라마다 빅맥 가격이 다른 이유, 지도로 한눈에 확인해보세요")

if "bigmac_df" not in st.session_state:
    st.warning("먼저 'Home' 페이지를 방문해서 데이터를 불러와주세요.")
    st.stop()

df = st.session_state["bigmac_df"]

# ────────────────────────────────────────────
# 대표 메뉴 이미지 매핑
# 실제 위키미디어 커먼��� 등 공개 이미지가 있는 나라는 URL을 연결하고,
# 이미지를 아직 못 찾은 나라는 기본 버거 이미지로 대체해요
# ────────────────────────────────────────────
MENU_IMAGE_MAP = {
    "United States": "https://commons.wikimedia.org/wiki/Special:FilePath/Big_Mac_hamburger.jpg",
    "India": "https://commons.wikimedia.org/wiki/Special:FilePath/McAloo_Tikki_Burger.jpg",
    "South Korea": "https://commons.wikimedia.org/wiki/Special:FilePath/Mcdonalds_seoul.JPG",
    "Japan": "https://commons.wikimedia.org/wiki/Special:FilePath/Teriyaki_McBurger.jpg",
    "France": "https://commons.wikimedia.org/wiki/Special:FilePath/Le_Big_Mac.jpg",
}

DEFAULT_MENU_IMAGE = "https://commons.wikimedia.org/wiki/Special:FilePath/Big_Mac_hamburger.jpg"

def get_menu_image(country):
    return MENU_IMAGE_MAP.get(country, DEFAULT_MENU_IMAGE)

# ────────────────────────────────────────────
# 지도 1: 빅맥 가격 choropleth
# ────────────────────────────────────────────
st.subheader("💵 국가별 빅맥 가격 (USD)")

fig_price = px.choropleth(
    df,
    locations="country",
    locationmode="country names",
    color="bigmac_price_usd",
    hover_name="country_kr",
    hover_data={
        "bigmac_price_usd": True,
        "gdp_per_capita_usd": True,
        "signature_menu": True,
        "country": False,
    },
    color_continuous_scale="YlOrRd",
    labels={"bigmac_price_usd": "빅맥 가격(USD)"},
)
fig_price.update_layout(
    geo=dict(showframe=False, showcoastlines=True),
    margin=dict(l=0, r=0, t=0, b=0),
)
st.plotly_chart(fig_price, use_container_width=True)

# ────────────────────────────────────────────
# 지도 2: 구매력 지수 choropleth
# ────────────────────────────────────────────
st.subheader("💰 국가별 구매력 지수 (GDP ÷ 빅맥가격)")
st.caption("숫자가 높을수록 그 나라 사람들에게는 빅맥이 상대적으로 '저렴하게' 느껴진다는 뜻이에요")

fig_afford = px.choropleth(
    df,
    locations="country",
    locationmode="country names",
    color="bigmac_affordability_index",
    hover_name="country_kr",
    hover_data={
        "bigmac_affordability_index": True,
        "gdp_per_capita_usd": True,
        "bigmac_price_usd": True,
        "country": False,
    },
    color_continuous_scale="Blues",
    labels={"bigmac_affordability_index": "구매력 지수"},
)
fig_afford.update_layout(
    geo=dict(showframe=False, showcoastlines=True),
    margin=dict(l=0, r=0, t=0, b=0),
)
st.plotly_chart(fig_afford, use_container_width=True)

# ────────────────────────────────────────────
# 국가 선택 → 상세 정보 카드 (+ 메뉴 이미지)
# ────────────────────────────────────────────
st.divider()
st.subheader("🔍 국가별 상세 정보")

selected = st.selectbox("국가를 선택하세요", df["country_kr"].dropna().tolist())
row = df[df["country_kr"] == selected].iloc[0]

detail_col1, detail_col2 = st.columns([1, 2])

with detail_col1:
    st.image(get_menu_image(row["country"]), use_container_width=True, caption=row["signature_menu"])

with detail_col2:
    st.markdown(f"### {row['flag']} {row['country_kr']}")
    col1, col2, col3 = st.columns(3)
    col1.metric("빅맥 가격", f"${row['bigmac_price_usd']}")
    col2.metric("1인당 GDP", f"${row['gdp_per_capita_usd']:,.0f}")
    col3.metric("구매력 지수", f"{row['bigmac_affordability_index']:,.0f}")
    st.info(f"🍔 **대표 로컬 메뉴:** {row['signature_menu']}")

# ────────────────────────────────────────────
# 구매력 순위 막대그래프
# ────────────────────────────────────────────
st.divider()
st.subheader("📊 구매력 지수 순위")

fig_bar = px.bar(
    df.sort_values("bigmac_affordability_index", ascending=True),
    x="bigmac_affordability_index",
    y="country_kr",
    orientation="h",
    color="bigmac_affordability_index",
    color_continuous_scale="Blues",
    labels={"bigmac_affordability_index": "구매력 지수", "country_kr": "국가"},
)
st.plotly_chart(fig_bar, use_container_width=True)
