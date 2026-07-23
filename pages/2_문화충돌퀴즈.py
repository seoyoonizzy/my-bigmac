import streamlit as st
import pandas as pd
import random

st.set_page_config(page_title="문화 충돌 퀴즈", layout="wide")
st.title("🎮 맥도날드 문화 충돌 퀴즈")
st.caption("나라별 맥도날드 가격과 메뉴, 얼마나 알고 있나요?")

# ────────────────────────────────────────────
# 이전 페이지에서 로드한 데이터 재사용
# ────────────────────────────────────────────
if "bigmac_df" not in st.session_state:
    st.warning("먼저 '국가별 가격지도' 페이지를 방문해서 데이터를 불러와주세요.")
    st.stop()

df = st.session_state["bigmac_df"]

# ────────────────────────────────────────────
# 점수와 퀴즈 상태를 세션에 저장 (새로고침해도 유지됨)
# ─────────────────────────────────────��──────
if "quiz_score" not in st.session_state:
    st.session_state.quiz_score = 0
if "quiz_total" not in st.session_state:
    st.session_state.quiz_total = 0
if "current_question" not in st.session_state:
    st.session_state.current_question = None
if "answered" not in st.session_state:
    st.session_state.answered = False

# ────────────────────────────────────────────
# 문제 유형 3가지를 랜덤으로 출제하는 함수
# ────────────────────────────────────────────
def generate_question():
    q_type = random.choice(["menu_to_country", "price_guess", "afford_rank"])

    if q_type == "menu_to_country":
        row = df.sample(1).iloc[0]
        correct = row["country_kr"]
        options = df["country_kr"].tolist()
        options = random.sample([o for o in options if o != correct], 3) + [correct]
        random.shuffle(options)
        return {
            "type": "menu_to_country",
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
            "type": "price_guess",
            "question": f"**{row['country_kr']}**의 빅맥 가격은 얼마일까요?",
            "options": options,
            "answer": f"${correct_price}",
        }

    else:  # afford_rank
        sorted_df = df.sort_values("bigmac_affordability_index", ascending=False)
        top_country = sorted_df.iloc[0]["country_kr"]
        options = df["country_kr"].sample(3).tolist()
        if top_country not in options:
            options[0] = top_country
        random.shuffle(options)
        return {
            "type": "afford_rank",
            "question": "다음 중 '구매력 지수'가 가장 높은(=빅맥이 상대적으로 저렴한) 나라는 어디일까요?",
            "options": options,
            "answer": top_country,
        }

# ────────────────────────────────────────────
# 첫 문제 생성
# ────────────────────────────────────────────
if st.session_state.current_question is None:
    st.session_state.current_question = generate_question()

q = st.session_state.current_question

# ────────────────────────────────────────────
# 점수판
# ────────────────────────────────────────────
col1, col2 = st.columns(2)
col1.metric("맞힌 문제", f"{st.session_state.quiz_score} / {st.session_state.quiz_total}")
if st.session_state.quiz_total > 0:
    accuracy = st.session_state.quiz_score / st.session_state.quiz_total * 100
    col2.metric("정답률", f"{accuracy:.0f}%")

st.divider()

# ────────────────────────────────────────────
# 문제 출력 및 선택지
# ────────────────────────────────────────────
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
            st.success(f"🎉 정답입니다! 정답은 **{q['answer']}** 이에요.")
        else:
            st.error(f"❌ 틀렸어요. 정답은 **{q['answer']}** 였어요.")

        # 관련 배경 설명 카드
        related_row = df[
            (df["country_kr"] == q["answer"]) | (df["signature_menu"].str.contains(str(q["answer"]), na=False))
        ]
        if not related_row.empty:
            r = related_row.iloc[0]
            st.info(
                f"💡 **{r['country_kr']}**의 빅맥 가격은 **${r['bigmac_price_usd']}**, "
                f"1인당 GDP는 **${r['gdp_per_capita_usd']:,.0f}**, "
                f"대표 메뉴는 **{r['signature_menu']}** 예요."
            )

if st.session_state.answered:
    if st.button("다음 문제 ➡️"):
        st.session_state.current_question = generate_question()
        st.session_state.answered = False
        st.rerun()

st.divider()
if st.button("🔄 점수 초기화"):
    st.session_state.quiz_score = 0
    st.session_state.quiz_total = 0
    st.session_state.current_question = generate_question()
    st.session_state.answered = False
    st.rerun()
