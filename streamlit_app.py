## 
## API를 숨기기
## 01. 해당 작업 폴더 내에 '.streamlit'라는 폴더를 만든다.
## 02. 해당 폴더 내에 'secrets.toml'이라는 파일을 만든다.
## 03. secrets.toml 파일에 아래와 같이 작성한다.
## [openai]
## API_KEY = "sk-..." # 본인의 API 키를 입력한다.

import openai
import streamlit as st
from openai import OpenAI
import os
import time

st.title("ChatGPT와 대화 챗봇")

# 비행기 애니메이션 CSS 스타일
airplane_animation_css = """
<style>
.airplane-container {
    display: flex;
    justify-content: center;
    align-items: center;
    height: 120px;
    margin: 20px 0;
}

.airplane {
    width: 100px;
    height: 100px;
    position: relative;
    animation: fly 2s ease-in-out infinite;
}

.airplane::before {
    content: "✈️";
    font-size: 60px;
    position: absolute;
    left: 50%;
    top: 50%;
    transform: translate(-50%, -50%);
    animation: bounce 1.5s ease-in-out infinite;
}

@keyframes fly {
    0%, 100% { transform: translateX(-20px) rotate(-5deg); }
    50% { transform: translateX(20px) rotate(5deg); }
}

@keyframes bounce {
    0%, 100% { transform: translate(-50%, -50%) translateY(0px); }
    50% { transform: translate(-50%, -50%) translateY(-10px); }
}

.loading-text {
    text-align: center;
    font-size: 18px;
    color: #666;
    margin-top: 10px;
    animation: pulse 1.5s ease-in-out infinite;
}

@keyframes pulse {
    0%, 100% { opacity: 0.6; }
    50% { opacity: 1; }
}
</style>
"""

st.markdown(airplane_animation_css, unsafe_allow_html=True)

st.sidebar.title("설정")
openai_api_key = st.sidebar.text_input("OpenAI 키를 입력하세요", type="password")

if not openai_api_key:
    st.sidebar.warning("OpenAI 키를 입력해주세요.")
    st.stop()

client = OpenAI(api_key=openai_api_key)

# 초기 대화 상태 설정
if "messages" not in st.session_state:
    st.session_state.messages = [  
        { "role": "system", 
          "content": "기본적으로 한국어로 먼저 답하고 아래에 영어로도 함께 답변해드립니다. "
                     "당신은 여행에 관한 질문에 답하는 챗봇입니다. "
                     "모르는 내용은 모른다고 얘기해드립니다."
                     "여행지 추천, 준비물, 문화, 음식 등 다양한 주제에 대해 친절하게 안내하는 챗봇입니다."
        }  
    ]

# 대화 초기화 버튼 추가
if st.button("대화 초기화") and st.session_state.messages:
    st.session_state.messages = []

# 폼을 사용하여 엔터키 입력 시 자동 전송 구현
with st.form(key="chat_form", clear_on_submit=True):
    user_input = st.text_input("사용자:", key="user_input", placeholder="메시지를 입력하고 엔터키를 누르세요...")
    submitted = st.form_submit_button("전송")

# 폼이 제출되었거나 전송 버튼이 클릭되었을 때 처리
if submitted and user_input.strip():
    # 사용자 메시지 추가
    st.session_state.messages.append({ "role": "user", 
                                       "content": user_input.strip()})

    # 로딩 애니메이션 표시
    loading_placeholder = st.empty()
    with loading_placeholder.container():
        st.markdown("""
        <div class="airplane-container">
            <div class="airplane"></div>
        </div>
        <div class="loading-text">답변을 생성하고 있습니다...</div>
        """, unsafe_allow_html=True)

    try:
        # OpenAI API 호출
        response = client.chat.completions.create(
            model="gpt-4o-mini",  # gpt-4o-mini로 변경
            messages=st.session_state.messages
        )

        # OpenAI 응답 추가
        response_message = response.choices[0].message.content
        st.session_state.messages.append({ "role": "assistant", 
                                           "content": response_message})
        
        # 로딩 애니메이션 제거
        loading_placeholder.empty()
        
        # 페이지 새로고침으로 최신 대화 내용 표시
        st.rerun()
        
    except Exception as e:
        # 오류 발생 시 로딩 애니메이션 제거하고 오류 메시지 표시
        loading_placeholder.empty()
        st.error(f"오류가 발생했습니다: {str(e)}")
        # 오류 발생 시 사용자 메시지 제거
        if st.session_state.messages and st.session_state.messages[-1]["role"] == "user":
            st.session_state.messages.pop()

# 대화 내용 표시
for message in st.session_state.messages:
    if message["role"] == "system":
        continue

    role = "👤"  if message["role"] == "user" else "🤖"
    st.markdown(f"{role}: {message['content']}")
