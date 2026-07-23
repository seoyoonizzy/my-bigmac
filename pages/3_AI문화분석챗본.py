import streamlit as st
from openai import OpenAI

# ────────────────────────────────────────────
# 페이지 기본 설정
# ────────────────────────────────────────────
st.set_page_config(page_title="AI 문화분석 챗봇", layout="wide")
st.title("🤖 AI 문화분석 챗봇")
st.caption("빅맥 가격과 메뉴의 차이, AI 선생님과 함께 알아봐요")

# ────────────────────────────────────────────
# Solar API 키는 코드에 직접 쓰지 않고, secrets(비밀 금고)에서 불러와요
# .streamlit/secrets.toml 파일에 SOLAR_API_KEY = "발급받은 키" 를 적어두면 돼요
# ────────────────────────────────────────────
client = OpenAI(
    api_key=st.secrets["SOLAR_API_KEY"],
    base_url="https://api.upstage.ai/v1",
)

# ────────────────────────────────────────────
# 이전 페이지에서 불러온 데이터를 챗봇 배경지식으로 함께 전달해요
# ────────────────────────────────────────────
data_context = ""
if "bigmac_df" in st.session_state:
    df = st.session_state["bigmac_df"]
    data_context = df.to_string(index=False)

# 우리 AI 선생님의 성격과 전문 분야를 정하는 시스템 프롬프트예요
SYSTEM_PROMPT = (
    "너는 따뜻하고 친절한 국제마케팅 선생님이야. "
    "8개국(한국, 미국, 인도, 일본, 프랑스, 스위스, 인도네시아, 중국)의 "
    "맥도날드 빅맥 가격, GDP, 구매력 지수, 대표 로컬 메뉴 데이터를 알고 있어. "
    "Hofstede의 문화차원 이론(개인주의-집단주의, 권력거리 등)과 "
    "빅맥지수 같은 경제 개념을 활용해서 왜 나라마다 가격과 메뉴가 다른지 "
    "쉽고 재미있게 설명해줘. "
    "예를 들어 인도는 종교적 이유로 소고기·돼지고기를 쓰지 않는 점, "
    "구매력 지수가 높은 나라는 빅맥이 비싸도 부담이 적다는 점, "
    "스위스처럼 물가가 비싼 나라와 인도처럼 저렴한 나라의 차이를 참고해서 답해줘. "
    "아래는 참고할 실제 데이터야:\n\n"
    f"{data_context}\n\n"
    "말투는 반드시 '~요'로 끝나는 친절한 존댓말을 쓰고, 순수 한국어로만 답해."
)

# ────────────────────────────────────────────
# 대화 기록을 세션(브라우저가 열려 있는 동안 유지되는 저장공간)에 저장해요
# 처음 접속했을 때만 시스템 프롬프트를 넣어서 초기화해요
# ────────────────────────────────────────────
if "chat_history" not in st.session_state:
    st.session_state.chat_history = [
        {"role": "system", "content": SYSTEM_PROMPT}
    ]

st.info(
    "예시 질문: '왜 인도 맥도날드는 소고기를 안 써요?' / "
    "'스위스랑 인도, 구매력 차이가 왜 이렇게 커요?'"
)

# 지금까지 나눈 대화를 화면에 말풍선으로 그려줘요 (시스템 메시지는 화면에 안 보이게 제외해요)
for message in st.session_state.chat_history:
    if message["role"] == "system":
        continue
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# ────────────────────────────────────────────
# 사용자가 채팅창에 메시지를 입력하면 실행되는 부분이에요
# ────────────────────────────────────────────
user_input = st.chat_input("빅맥 가격이나 나라별 메뉴에 대해 궁금한 걸 물어보세요")

if user_input:
    # 사용자 메시지를 대화 기록에 추가하고 화면에 바로 표시해요
    st.session_state.chat_history.append({"role": "user", "content": user_input})
    with st.chat_message("user"):
        st.markdown(user_input)

    # AI의 답을 담을 빈 말풍선을 먼저 만들어둬요 (여기에 글자가 실시간으로 채워져요)
    with st.chat_message("assistant"):
        placeholder = st.empty()
        full_answer = ""

        try:
            # Solar API에 스트리밍 방식으로 요청해요
            # reasoning_effort="none" 으로 추론(생각) 기능을 꺼서 답이 빨리 나오게 해요
            stream = client.chat.completions.create(
                model="solar-open2",
                messages=st.session_state.chat_history,
                reasoning_effort="none",
                stream=True,
            )

            # 스트리밍으로 오는 글자 조각들을 하나씩 이어붙여서 실시간으로 보여줘요
            for chunk in stream:
                delta = chunk.choices[0].delta.content
                if delta:
                    full_answer += delta
                    placeholder.markdown(full_answer)

        except Exception:
            # 에러가 나도 사용자에게는 어려운 에러 메시지 대신 친절한 안내만 보여줘요
            full_answer = (
                "죄송해요, 지금 답변을 가져오는 데 문제가 생겼어요.😔"
                "잠시 후 다시 시도해 주시겠어요?"
            )
            placeholder.markdown(full_answer)

    # AI의 답변도 대화 기록에 추가해서 다음 질문에서 이어서 기억하게 해요
    st.session_state.chat_history.append({"role": "assistant", "content": full_answer})
