import streamlit as st
import pandas as pd
import random

st.set_page_config(page_title="물가체험존", layout="wide")
st.title("🎢 물가체험존")
st.caption("퀴즈도 풀고, 내 월급으로 계산도 해보고, 물가를 직접 체감해보세요")

if "bigmac_df" not in st.session_state:
    st.warning("먼저 'Home' 페이지를 방문해서 데이터를 불러와주세요.")
    st.stop()

df = st.session_state["bigmac_df"]

tab1, tab2, tab3 = st.tabs(["🧩 빅맥 퀴즈", "⏱️ 내 월급으로 빅맥 사기", "🛒 이 돈이면 뭘 살까?"])

# ════════════════════════════════════════════
# 탭 1: 문화 충돌 퀴즈
# ════════════════════════════════════════════
with tab1:
    if "quiz_score" not in st.session_state:
        st.session_state.quiz_score = 0
    if "quiz_total" not in st.session_state:
        st.session_state.quiz_total = 0
    if "current_question" not in st.session_state:
        st.session_state.current_question = None
    if "answered" not in st.session_state:
        st.session_state.answered = False

    def generate_question():
        q_type = random.choice(["menu_to_country", "price_guess", "afford_rank"])

        if q_type == "menu_to_country":
            row = df.sample(1).iloc[0]
            correct = row["country_kr"]
            options = df["country_kr"].dropna().tolist()
            options = random.sample([o for o in options if o != correct], 3) + [correct]
            random.shuffle(options)
            return {
                "question": f"다음 대표 메뉴는 어느 나라 맥도날드일까요?\n\n🍔 **{row['signature_menu']}**",
                "options": options,
                "answer": correct,
            }

        elif q_type == "price_guess":
            row = df.sample(1).iloc[0]
            correct_price = row["bigmac_price_usd"]
            wrong_prices = [round(correct_price + d, 2) for d in [-2.0, -1.0, 1.5]]
            options = [f"${p}" for p in wrong_prices] + [f"${correct_price}"]
            random.shuffle(options)
            return {
                "question": f"**{row['country_kr']}**의 빅맥 가격은 얼마일까요?",
                "options": options,
                "answer": f"${correct_price}",
            }

        else:
            sorted_df = df.sort_values("bigmac_affordability_index", ascending=False)
            top_country = sorted_df.iloc[0]["country_kr"]
            options = df["country_kr"].dropna().sample(3).tolist()
            if top_country not in options:
                options[0] = top_country
            random.shuffle(options)
            return {
                "question": "다음 중 '구매력 지수'가 가장 높은(=빅맥이 상대적으로 저렴한) 나라는 어디일까요?",
                "options": options,
                "answer": top_country,
            }

    if st.session_state.current_question is None:
        st.session_state.current_question = generate_question()

    q = st.session_state.current_question

    col1, col2 = st.columns(2)
    col1.metric("맞힌 문제", f"{st.session_state.quiz_score} / {st.session_state.quiz_total}")
    if st.session_state.quiz_total > 0:
        accuracy = st.session_state.quiz_score / st.session_state.quiz_total * 100
        col2.metric("정답률", f"{accuracy:.0f}%")

    st.divider()
    st.markdown(f"### {q['question']}")

    choice = st.radio("정답을 선택하세요", q["options"], index=None, key=f"choice_{st.session_state.quiz_total}")

    if st.button("제출하기", disabled=st.session_state.answered):
        if choice is None:
            st.warning("정답을 선택해주세요!")
        else:
            st.session_state.answered = True
            st.session_state.quiz_total += 1
            if choice == q["answer"]:
                st.session_state.quiz_score += 1
                st.success(f"🎉 정답이에요! 정답은 **{q['answer']}** 예요.")
            else:
                st.error(f"❌ 틀렸어요. 정답은 **{q['answer']}** 였어요.")

    if st.session_state.answered:
        if st.button("다음 문제 ➡️"):
            st.session_state.current_question = generate_question()
            st.session_state.answered = False
            st.rerun()

    if st.button("🔄 점수 초기화"):
        st.session_state.quiz_score = 0
        st.session_state.quiz_total = 0
        st.session_state.current_question = generate_question()
        st.session_state.answered = False
        st.rerun()

# ════════════════════════════════════════════
# 탭 2: 내 월급으로 빅맥 사기
# ════════════════════════════════════════════
with tab2:
    st.subheader("⏱️ 내 시급으로 각국 빅맥을 사려면 몇 분 일해야 할까요?")
    st.caption("시급을 입력하면, 각 나라 사람의 체감 물가와 나를 비교해볼 수 있어요")

    my_wage = st.number_input("나의 시급을 입력해보세요 (원)", min_value=1000, value=12000, step=500)
    exchange_rate = st.number_input("원/달러 환율 (참고용, 기본값 1,350원)", min_value=500, value=1350, step=10)

    my_minutes = (df["bigmac_price_usd"] * exchange_rate) / (my_wage / 60)
    result_df = df.copy()
    result_df["my_work_minutes"] = my_minutes.round(1)

    my_result = result_df[result_df["country_kr"] == "한국"]
    if not my_result.empty:
        st.info(f"💡 내 시급으로 한국 빅맥 하나 사려면 **{my_result['my_work_minutes'].values[0]}분** 일하면 돼요.")

    st.divider()
    display_cols = result_df[["flag", "country_kr", "bigmac_price_usd", "my_work_minutes"]].rename(columns={
        "flag": "국기", "country_kr": "국가", "bigmac_price_usd": "빅맥 가격(USD)", "my_work_minutes": "내가 일해야 하는 시간(분)"
    }).sort_values("내가 일해야 하는 시간(분)", ascending=False)

    st.dataframe(
        display_cols,
        use_container_width=True,
        hide_index=True,
        column_config={
            "빅맥 가격(USD)": st.column_config.NumberColumn(format="$%.2f"),
            "내가 일해야 하는 시간(분)": st.column_config.NumberColumn(format="%.1f분"),
        },
    )

    longest = display_cols.iloc[0]
    shortest = display_cols.iloc[-1]
    col1, col2 = st.columns(2)
    with col1:
        st.error(f"😥 내 시급 기준으로 가장 오래 일해야 하는 나라: **{longest['국가']}** ({longest['내가 일해야 하는 시간(분)']:.1f}분)")
    with col2:
        st.success(f"😄 내 시급 기준으로 가장 빨리 살 수 있는 나라: **{shortest['국가']}** ({shortest['내가 일해야 하는 시간(분)']:.1f}분)")

# ════════════════════════════════════════════
# 탭 3: 이 돈이면 뭘 살까?
# ════════════════════════════════════════════
with tab3:
    st.subheader("🛒 이 나라 빅맥 값으로 우리나라에서 뭘 살 수 있을까요?")
    st.caption("물가 차이를 숫자가 아니라 '체감'으로 느껴보는 코너예요")

    korea_items = {
        "아메리카노 한 잔 (약 4,500원)": 4500,
        "김밥 한 줄 (약 3,500원)": 3500,
        "편의점 삼각김밥 (약 1,700원)": 1700,
        "버스 요금 (약 1,500원)": 1500,
        "붕어빵 3개 (약 2,000원)": 2000,
        "떡볶이 1인분 (약 4,000원)": 4000,
    }

    selected_country_kr = st.selectbox("나라를 선택해보세요", df["country_kr"].dropna().tolist(), key="compare_country")
    row = df[df["country_kr"] == selected_country_kr].iloc[0]

    price_krw = row["bigmac_price_usd"] * exchange_rate

    st.markdown(f"### {row['flag']} {row['country_kr']}의 빅맥 값 (약 {price_krw:,.0f}원)으로 살 수 있는 것")

    cols = st.columns(3)
    for idx, (item_name, item_price) in enumerate(korea_items.items()):
        count = int(price_krw // item_price)
        with cols[idx % 3]:
            st.metric(item_name, f"{count}개")

    st.info(f"💡 즉, **{row['country_kr']}**에서 빅맥 하나 사는 돈이면, 한국에서는 위 항목들을 이만큼 살 수 있어요!")
