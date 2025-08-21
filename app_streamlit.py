import os
import requests
from dotenv import load_dotenv
import streamlit as st
import streamlit.components.v1 as components
import json
import base64

load_dotenv()

SYSTEM_PROMPT = "너는 아주 친절한 챗봇이야. 사람의 질문에 성의껏 답변해줘."
FASTAPI_URL = os.getenv("FASTAPI_URL", "http://localhost:8000/chat")
PPT_FASTAPI_URL = os.getenv("PPT_FASTAPI_URL", "http://localhost:8000/generate-ppt")

# streamlit 화면에 SVG를 HTML로 감싸서 표시할 수 있도록 변환하는 함수
def create_svg_html(svg_content, width="100%", height="600px"):
    """SVG를 HTML로 감싸서 렌더링 (여백 제거)"""
    if not svg_content:
        return "<div>SVG 내용이 없습니다.</div>"
    
    # SVG가 XML 선언으로 시작하는지 확인
    if not svg_content.strip().startswith('<?xml'):
        svg_content = '<?xml version="1.0" encoding="UTF-8"?>\n' + svg_content
    
    html_content = f'''
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="UTF-8">
        <style>
            * {{
                margin: 0;
                padding: 0;
                box-sizing: border-box;
            }}
            html, body {{
                width: 100%;
                height: 100%;
                background: transparent;
                overflow: hidden;
            }}
            .slide-container {{
                width: 100%;
                height: 100%;
                display: flex;
                justify-content: center;
                align-items: center;
                background: transparent;
            }}
            svg {{
                max-width: 100%;
                max-height: 100%;
                display: block;
                background: white;
            }}
        </style>
    </head>
    <body>
        <div class="slide-container">
            {svg_content}
        </div>
    </body>
    </html>
    '''
    return html_content

#  텍스트(슬라이드 제목/내용)를 HTML 슬라이드 형태로 예쁘게 만들어주는 함수
def create_simple_slide_html(title, content, slide_type="content"):
    """간단한 슬라이드 HTML 생성 (여백 제거)"""
    colors = {
        "title": {"bg": "#10b981", "title": "#ffffff", "content": "#d1fae5"},
        "content": {"bg": "#ffffff", "title": "#059669", "content": "#374151"},
        "conclusion": {"bg": "#059669", "title": "#ffffff", "content": "#d1fae5"}
    }
    
    color_scheme = colors.get(slide_type, colors["content"])
    content_lines = content.split('\n')
    
    html = f'''
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="UTF-8">
        <style>
            * {{
                margin: 0;
                padding: 0;
                box-sizing: border-box;
            }}
            html, body {{
                width: 100%;
                height: 100%;
                background: {color_scheme['bg']};
                font-family: 'NanumGothic', Arial, sans-serif;
                display: flex;
                flex-direction: column;
                justify-content: center;
                color: {color_scheme['content']};
                overflow: hidden;
            }}
            .title {{
                font-size: 2.5em;
                font-weight: bold;
                color: {color_scheme['title']};
                text-align: center;
                margin-bottom: 40px;
                text-shadow: 0 2px 4px rgba(0,0,0,0.1);
                padding: 0 20px;
            }}
            .content {{
                font-size: 1.3em;
                line-height: 1.8;
                max-width: 800px;
                margin: 0 auto;
                padding: 0 40px;
            }}
            .bullet {{
                margin: 15px 0;
                padding-left: 20px;
            }}
            .divider {{
                height: 3px;
                background: {color_scheme['title']};
                margin: 30px auto;
                width: 200px;
                border-radius: 2px;
            }}
        </style>
    </head>
    <body>
        <div class="title">{title}</div>
        <div class="divider"></div>
        <div class="content">
    '''
    
    for line in content_lines:
        if line.strip():
            html += f'<div class="bullet">• {line.strip()}</div>'
    
    html += '''
        </div>
    </body>
    </html>
    '''
    return html

# 페이지 레이아웃
st.set_page_config(
    page_title="LLM 챗봇 & PPT 생성기", 
    # page_icon="🤖", 
    layout="wide"
)

# 사이드바에서 모드 선택
st.sidebar.title("🎛️ 모드 선택")
mode = st.sidebar.selectbox("사용할 기능을 선택하세요:", ["📊 PPT 생성기", "💬 챗봇"])

if mode == "💬 챗봇":
    st.title("🤖 챗봇")
    
    # 세션 상태 초기화
    if "messages" not in st.session_state:
        st.session_state.messages = [
            {"role": "system", "content": SYSTEM_PROMPT},
        ]

    # 기존 대화 내용 출력
    for msg in st.session_state.messages:
        if msg["role"] == "system":
            continue
        with st.chat_message("user" if msg["role"] == "user" else "assistant"):
            st.markdown(msg["content"], unsafe_allow_html=True)

    # 사용자 입력
    user_input = st.chat_input("질문을 입력하세요:")

    if user_input:
        st.session_state.messages.append({"role": "user", "content": user_input})
        with st.chat_message("user"):
            st.markdown(user_input)

        try:
            response = requests.post(
                FASTAPI_URL,
                json={"message": user_input},
                timeout=60,
            )
            bot_answer = response.json().get("response", "⚠️ 서버가 올바른 응답을 반환하지 않았습니다.")
        except Exception as e:
            bot_answer = f"⚠️ FastAPI 호출 오류: {e}"

        st.session_state.messages.append({"role": "assistant", "content": bot_answer})
        with st.chat_message("assistant"):
            st.markdown(bot_answer, unsafe_allow_html=True)

elif mode == "📊 PPT 생성기":
    st.title("📊 PPT 생성기")

    # 예시 입력 버튼들
    # st.markdown("### 💡 빠른 시작 예시")
    # col1, col2, col3 = st.columns(3)
    
    # with col1:
    if st.button("📊 예시 보고서(실적)"):
        st.session_state.example_content = """
        # 2024년 4분기 실적 보고서
        
        ## 매출 현황
        - 총 매출: 120억원 (전년 대비 15% 증가)
        - 온라인 매출: 80억원 (67%)
        - 오프라인 매출: 40억원 (33%)
        
        ## 주요 성과
        - 신규 고객 확보: 15,000명
        - 고객 만족도: 4.2/5.0
        - 시장 점유율: 8.5% (전분기 대비 1.2% 증가)

        """

    # 보고서 내용 입력
    report_content = st.text_area(
        "보고서 내용을 입력하세요:",
        value=st.session_state.get("example_content", ""),
        height=400,
        placeholder="""예시:
# 프로젝트 현황 보고서

## 주요 성과
- 매출 증가율: 25%
- 신규 고객: 1,200명
- 고객 만족도: 4.5/5.0

## 데이터 분석
- 월별 성장률 데이터
- 지역별 매출 분포
- 연령대별 고객 분석

## 향후 계획
- 마케팅 예산 확대
- 신제품 개발
- 글로벌 진출 전략
        """,
        key="report_input"
    )
    
    # PPT 생성 버튼
    generate_button = st.button("🎯 PPT 생성", type="primary", use_container_width=True)
    
    if generate_button:
        if report_content.strip():
            with st.spinner("슬라이드를 생성하고 있습니다... (30-60초 소요)"):
                try:
                    # FastAPI 서버로 PPT 생성 요청
                    response = requests.post(
                        PPT_FASTAPI_URL,
                        json={"report_content": report_content},
                        timeout=240,
                    )
                    
                    if response.status_code == 200:
                        ppt_data = response.json()
                        slides = ppt_data.get("slides", [])
                        message = ppt_data.get("message", "")
                        
                        if slides:
                            st.success(f"✅ {message}")
                            
                            # 모든 슬라이드를 위에서 아래로 순서대로 표시
                            st.markdown("---")
                            st.markdown("### 📑 생성된 프레젠테이션")
                            
                            for i, slide in enumerate(slides):
                                # SVG 내용이 있으면 렌더링, 없으면 간단한 슬라이드 생성
                                if slide.get('svg') and slide['svg'].strip():
                                    html_slide = create_svg_html(slide['svg'])
                                    components.html(html_slide, height=680, scrolling=False)
                                else:
                                    # Fallback: 간단한 HTML 슬라이드
                                    simple_slide = create_simple_slide_html(
                                        slide['title'],
                                        slide.get('content', '내용이 없습니다.'),
                                        'content'
                                    )
                                    components.html(simple_slide, height=620, scrolling=False)
                                
                                # 슬라이드 간 간격
                                if i < len(slides) - 1:
                                    st.markdown("<br>", unsafe_allow_html=True)
                            
                            # 하단 요약 정보
                            st.markdown("---")
                            st.info(f"🎯 총 **{len(slides)}개** 슬라이드가 생성되었습니다. 위에서 아래로 스크롤하여 모든 슬라이드를 확인하세요.")
                        else:
                            st.error("⚠️ 슬라이드 생성에 실패했습니다.")
                    else:
                        st.error(f"⚠️ 서버 오류: {response.status_code}")
                        if response.text:
                            st.code(response.text)
                        
                except requests.exceptions.Timeout:
                    st.error("⚠️ 요청 시간이 초과되었습니다. 내용을 단순화하거나 다시 시도해주세요.")
                except Exception as e:
                    st.error(f"⚠️ PPT 생성 중 오류가 발생했습니다: {e}")
        else:
            st.warning("⚠️ 보고서 내용을 입력해주세요.")




