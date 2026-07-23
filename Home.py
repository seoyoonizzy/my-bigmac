import streamlit as st
import pandas as pd

st.set_page_config(
    page_title="빅맥으로 보는 세계 경제",
    page_icon="🍔",
    layout="wide",
)

st.title("🍔 빅맥으로 보는 세계 경제")
st.caption("같은 버거, 다른 가격 — 52개국 맥도날드로 살펴보는 구매력과 문화 이야기예요")

st.markdown("""
"빅맥지수(Big Mac Index)"는 영국 경제지 The Economist가 고안한 유명한 경제 지표예요.
전 세계 어디서나 거의 동일한 빅맥의 가격을 비교하면, 각국의 물가 수준과 화폐 가치를
쉽고 재미있게 가늠할 수 있다는 아이디어에서 출발했어요.

이 앱은 이 개념을 확장해서, 단순히 가격만 비교하는 게 아니라
**"그 가격이 그 나라 사람들에게는 얼마나 부담스러운가"** (구매력 지수)와
**"왜 나라마다 메뉴 자체가 다른가"** (문화적 로컬라이징)까지 함께 살펴봐요.
""")

st.divider()

# ────────────────────────────────────────────
# 왜 만들었는지
# ────────────────────────────────────────────
st.subheader("💡 왜 이 앱을 만들었을까요?")
st.markdown("""
국제경영/마케팅을 공부하면서 "같은 브랜드가 나라마다 왜 다르게 행동할까?"라는 질문에
관심을 갖게 되었어요. 맥도날드는 전 세계 어디에나 있지만, 가격도 메뉴도 나라마다 달라요.

이 앱은 이 차이를 **데이터로 직접 확인하고, 퀴즈로 재미있게 학습하고,
AI와 대화하며 이해를 넓히는** 세 가지 방식을 하나로 묶은 프로젝트예요.
""")

st.divider()

# ────────────────────────────────────────────
# 어떻게 이용하면 되는지
# ────────────────────────────────────────────
st.subheader("🧭 이렇게 둘러보세요")

col1, col2 = st.columns(2)
with col1:
    st.markdown("""
    **🗺️ 국가별 가격 지도**
    52개국의 빅맥 가격과 구매력 지수를 지도와 그래프로 확인해보세요.
    국가를 선택하면 GDP, 가격, 대표 로컬 메뉴까지 한눈에 볼 수 있어요.
    """)
with col2:
    st.markdown("""
    **🎮 문화 충돌 퀴즈**
    가격, 메뉴, 구매력 순위를 맞히는 퀴즈로 배운 내용을 테스트해볼 수 있어요.
    문제를 풀 때마다 관련 배경지식이 함께 나와요.
    """)

st.markdown("""
**🤖 AI 문화분석 챗봇**
"왜 인도는 소고기를 안 쓸까?" 같은 질문을 자유롭게 물어보세요.
Hofstede 문화차원 이론을 바탕으로 AI가 설명해드려���.
""")

st.divider()

# ────────────────────────────────────────────
# 데이터 불러오기
# ────────────────────────────────────────────
@st.cache_data
def load_data():
    return pd.read_csv("bigmac_country_comparison.csv")

df = load_data()
st.session_state["bigmac_df"] = df

# ────────────────────────────────────────────
# 핵심 지표 요약
# ────────────────────────────────────────────
col1, col2, col3, col4 = st.columns(4)
col1.metric("비교 국가 수", f"{len(df)}개국")
col2.metric("대륙 수", f"{df['region'].nunique()}개 지역")
col3.metric("GDP 기준 연도", "2023년")
col4.metric("가격 기준 시점", df["price_data_date"].iloc[0])

st.divider()

# ────────────────────────────────────────────
# 📈 종합 인사이트: 국가별 요약 테이블
# ────────────────────────────────────────────
st.subheader("📈 종합 인사이트: 52개국 한눈에 비교하기")
st.caption("페이지를 넘기기 전에, 전체 데이터를 표로 먼저 훑어보세요")

region_options = ["전체"] + sorted(df["region"].unique().tolist())
selected_region = st.selectbox("지역으로 필터링해보세요", region_options)

filtered_df = df if selected_region == "전체" else df[df["region"] == selected_region]

display_df = filtered_df[[
    "flag", "country_kr", "bigmac_price_usd", "gdp_per_capita_usd",
    "bigmac_affordability_index", "signature_menu"
]].rename(columns={
    "flag": "국기",
    "country_kr": "국가",
    "bigmac_price_usd": "빅맥 가격(USD)",
    "gdp_per_capita_usd": "1인당 GDP(USD)",
    "bigmac_affordability_index": "구매력 지수",
    "signature_menu": "대표 로컬 메뉴",
}).sort_values("구매력 지수", ascending=False)

st.dataframe(
    display_df,
    use_container_width=True,
    hide_index=True,
    column_config={
        "빅맥 가격(USD)": st.column_config.NumberColumn(format="$%.2f"),
        "1인당 GDP(USD)": st.column_config.NumberColumn(format="$%,.0f"),
        "구매력 지수": st.column_config.NumberColumn(format="%,.0f"),
    },
)

col1, col2 = st.columns(2)
with col1:
    st.success(f"💰 구매력 지수가 가장 높은 나라는 **{display_df.iloc[0]['국가']}**예요")
with col2:
    st.error(f"💸 구매력 지수가 가장 낮은 나라는 **{display_df.iloc[-1]['국가']}**예요")

st.divider()

# ────────────────────────────────────────────
# 데이터 정확성 및 한계 안내 (중요)
# ────────────────────────────────────────────
st.subheader("⚠️ 데이터에 대해 안내드려요")
st.warning("""
이 앱의 데이터는 학습 및 데모 목적으로 제작되었고, 다음과 같은 한계가 있어요.

- **빅맥 가격**: The Economist Big Mac Index 원본 데이터(bigmacindex.app 경유)를 사용했고, 기준 시점은 표에 함께 표시돼요.
- **GDP 데이터**: World Bank의 1인당 GDP(2023년 기준) 공개 데이터를 사용했어요.
- **구매력 지수**: "1인당 GDP ÷ 빅맥 가격"으로 직접 계산한 자체 지표이며, 공식 경제 지표는 아니에요.
- **로컬 메뉴 정보**: 각국 맥도날드 공식 자료와 언론 보도를 참고해 정리했고, 실제 판매 여부는 시기와 지역에 따라 다를 수 있어요. 일부 국가는 정보가 제한적일 수 있어요.
- **국가 범위**: 유로존, 대만 등 일부 국가·지역은 GDP 데이터와 매칭되지 않아 이번 비교에서 제외됐어요.

**실제 투자, 학술 인용, 비즈니스 의사결정에는 이 앱의 데이터를 사용하지 마시고,
반드시 공식 출처(The Economist, World Bank, 각국 맥도날드 공식 홈페이지)를 확인해주세요.**
""")

st.divider()
st.caption("데이터 기반 바이브 코딩 초급반 최종 프로젝트예요 · Solar API 및 공개 경제 데이터를 활용했어요")
