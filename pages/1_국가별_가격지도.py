import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="국가별 가격지도", layout="wide")
st.title("🗺️ 국가별 빅맥 가격 & 구매력 지도")
st.caption("나라마다 빅맥 가격이 어떻게 다르고, 체감 구매력은 얼마나 다른지 한눈에 살펴봐요")

# --------------------------------------------------
# 데이터 불러오기
# --------------------------------------------------
@st.cache_data
def load_data():
    return pd.read_csv("bigmac_country_comparison.csv")

if "bigmac_df" in st.session_state:
    df = st.session_state["bigmac_df"].copy()
else:
    df = load_data()
    st.session_state["bigmac_df"] = df

# menu_image_url 컬럼이 아직 없더라도 앱이 죽지 않게 대비해요
if "menu_image_url" not in df.columns:
    df["menu_image_url"] = ""

DEFAULT_MENU_IMAGE = "https://upload.wikimedia.org/wikipedia/commons/4/4d/Big_Mac.png"

def get_menu_image(row):
    image_url = str(row.get("menu_image_url", "")).strip()
    if image_url and image_url.lower() != "nan":
        return image_url
    return DEFAULT_MENU_IMAGE

# --------------------------------------------------
# 상단 필터
# --------------------------------------------------
region_options = ["전체"] + sorted(df["region"].dropna().unique().tolist())
selected_region = st.selectbox("지역으로 필터링해보세요", region_options)

filtered_df = df if selected_region == "전체" else df[df["region"] == selected_region]

# --------------------------------------------------
# 지도 1: 빅맥 가격
# --------------------------------------------------
st.subheader("💵 국가별 빅맥 가격 (USD)")

fig_price = px.choropleth(
    filtered_df,
    locations="country",
    locationmode="country names",
    color="bigmac_price_usd",
    hover_name="country_kr",
    hover_data={
        "bigmac_price_usd": ":.2f",
        "gdp_per_capita_usd": ":,.0f",
        "bigmac_affordability_index": ":,.0f",
        "signature_menu": True,
        "country": False,
        "region": True,
        "menu_image_url": False,
    },
    color_continuous_scale="YlOrRd",
    labels={
        "bigmac_price_usd": "빅맥 가격(USD)",
        "gdp_per_capita_usd": "1인당 GDP(USD)",
        "bigmac_affordability_index": "구매력 지수",
        "signature_menu": "대표 로컬 메뉴",
        "region": "지역",
    },
)
fig_price.update_layout(
    geo=dict(showframe=False, showcoastlines=True),
    margin=dict(l=0, r=0, t=0, b=0),
)
st.plotly_chart(fig_price, use_container_width=True)

# --------------------------------------------------
# 지도 2: 구매력 지수
# --------------------------------------------------
st.subheader("💰 국가별 구매력 지수 (GDP ÷ 빅맥 가격)")
st.caption("숫자가 높을수록 그 나라 사람들에게 빅맥이 상대적으로 덜 부담된다는 뜻이에요")

fig_afford = px.choropleth(
    filtered_df,
    locations="country",
    locationmode="country names",
    color="bigmac_affordability_index",
    hover_name="country_kr",
    hover_data={
        "bigmac_affordability_index": ":,.0f",
        "gdp_per_capita_usd": ":,.0f",
        "bigmac_price_usd": ":.2f",
        "signature_menu": True,
        "country": False,
        "region": True,
        "menu_image_url": False,
    },
    color_continuous_scale="Blues",
    labels={
        "bigmac_affordability_index": "구매력 지수",
        "gdp_per_capita_usd": "1인당 GDP(USD)",
        "bigmac_price_usd": "빅맥 가격(USD)",
        "signature_menu": "대표 로컬 메뉴",
        "region": "지역",
    },
)
fig_afford.update_layout(
    geo=dict(showframe=False, showcoastlines=True),
    margin=dict(l=0, r=0, t=0, b=0),
)
st.plotly_chart(fig_afford, use_container_width=True)

# --------------------------------------------------
# 국가별 상세 정보
# --------------------------------------------------
st.divider()
st.subheader("🔍 국가별 상세 정보")

country_options = filtered_df["country_kr"].dropna().tolist()
selected_country = st.selectbox("국가를 선택하세요", country_options)

row = filtered_df[filtered_df["country_kr"] == selected_country].iloc[0]

left, right = st.columns([1.1, 1.4])

with left:
    st.markdown(f"### {row['flag']} {row['country_kr']}")
    st.markdown(f"**대표 로컬 메뉴:** {row['signature_menu']}")
    st.image(
        get_menu_image(row),
        use_container_width=True,
        caption=row["signature_menu"]
    )

with right:
    c1, c2, c3 = st.columns(3)
    c1.metric("빅맥 가격", f"${row['bigmac_price_usd']:.2f}")
    c2.metric("1인당 GDP", f"${row['gdp_per_capita_usd']:,.0f}")
    c3.metric("구매력 지수", f"{row['bigmac_affordability_index']:,.0f}")

    st.info(
        f"{row['country_kr']}은(는) {row['region']} 지역에 속하고, "
        f"대표 로컬 메뉴는 {row['signature_menu']}예요."
    )

    with st.expander("상세 데이터 보기"):
        st.write({
            "영문 국가명": row["country"],
            "지역": row["region"],
            "빅맥 가격(USD)": round(row["bigmac_price_usd"], 2),
            "1인당 GDP(USD)": round(row["gdp_per_capita_usd"], 1),
            "구매력 지수": round(row["bigmac_affordability_index"], 1),
            "가격 기준 시점": row["price_data_date"],
        })

# --------------------------------------------------
# 구매력 순위 막대그래프
# --------------------------------------------------
st.divider()
st.subheader("📊 구매력 지수 순위")

rank_df = filtered_df.sort_values("bigmac_affordability_index", ascending=True)

fig_bar = px.bar(
    rank_df,
    x="bigmac_affordability_index",
    y="country_kr",
    orientation="h",
    color="bigmac_affordability_index",
    color_continuous_scale="Blues",
    labels={
        "bigmac_affordability_index": "구매력 지수",
        "country_kr": "국가",
    },
)
fig_bar.update_layout(margin=dict(l=0, r=0, t=10, b=0))
st.plotly_chart(fig_bar, use_container_width=True)

# --------------------------------------------------
# 하단 표
# --------------------------------------------------
st.divider()
st.subheader("📋 국가별 데이터 표")

table_df = filtered_df[[
    "flag", "country_kr", "region", "bigmac_price_usd",
    "gdp_per_capita_usd", "bigmac_affordability_index",
    "signature_menu"
]].rename(columns={
    "flag": "국기",
    "country_kr": "국가",
    "region": "지역",
    "bigmac_price_usd": "빅맥 가격(USD)",
    "gdp_per_capita_usd": "1인당 GDP(USD)",
    "bigmac_affordability_index": "구매력 지수",
    "signature_menu": "대표 로컬 메뉴",
})

st.dataframe(
    table_df.sort_values("구매력 지수", ascending=False),
    use_container_width=True,
    hide_index=True,
    column_config={
        "빅맥 가격(USD)": st.column_config.NumberColumn(format="$%.2f"),
        "1인당 GDP(USD)": st.column_config.NumberColumn(format="$%,.0f"),
        "구매력 지수": st.column_config.NumberColumn(format="%,.0f"),
    },
)
