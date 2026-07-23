import streamlit as st
import pandas as pd
import plotly.express as px

# ────────────────────────────────────────────
# 페이지 기본 설정
# ────────────────────────────────────────────
st.set_page_config(page_title="국가별 가격 지도", layout="wide")
st.title("🗺️ 국가별 빅맥 가격 & 구매력 지도")
st.caption("나라마다 빅맥 가격이 다른 이유, 지도로 한눈에 확인해보세요")

# ────────────────────────────────────────────
# 데이터 불러오기 (세션에 저장해서 다른 페이지에서도 재사용)
# ────────────────────────────────────────────
@st.cache_data
def load_data():
    return pd.read_csv("bigmac_country_comparison.csv")

df = load_data()
st.session_state["bigmac_df"] = df

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
# 국가 선택 → 상세 정보 카드
# ────────────────────────────────────────────
st.divider()
st.subheader("🔍 국가별 상세 정보")

selected = st.selectbox("국가를 선택하세요", df["country_kr"].tolist())
row = df[df["country_kr"] == selected].iloc[0]

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
