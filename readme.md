# LLM 챗봇 & PPT 생성기 (fsl5)

## 소개

이 프로젝트는 Streamlit 기반의 웹 UI와 FastAPI 백엔드를 활용하여  
- **LLM 챗봇**  
- **보고서 텍스트로부터 자동 PPT(SVG 슬라이드) 생성**  
기능을 제공합니다.

Anthropic Claude, LangChain 등 최신 LLM 기술을 활용하며,  
Streamlit UI에서 손쉽게 챗봇 대화 및 PPT 슬라이드 생성을 경험할 수 있습니다.

---

## 폴더 구조

```
fsl5/
├── app_streamlit.py      # Streamlit 프론트엔드 (웹 UI)
├── app_fastapi.py        # FastAPI 백엔드 (API 서버)
├── claude_ppt.py         # Claude 기반 PPT 생성 관련 모듈
├── requirements.txt      # Python 의존성 목록
└── __pycache__/          # 파이썬 캐시 파일 (무시해도 됨)
```

---

## 설치 및 실행 방법

### 1. 의존성 설치

```bash
pip install -r requirements.txt
```

### 2. 환경 변수 설정

`.env` 파일을 fsl5 폴더에 생성하고 아래와 같이 작성하세요.

```
ANTHROPIC_API_KEY=your_claude_api_key
```

### 3. FastAPI 서버 실행

```bash
uvicorn app_fastapi:app --reload
```

### 4. Streamlit 앱 실행

```bash
streamlit run app_streamlit.py
```

---

## 주요 기능

- **챗봇**: LLM(Claude) 기반 자연어 대화
- **PPT 생성기**: 보고서 텍스트 입력 → Claude가 SVG 슬라이드 자동 생성

---

## 주요 파일 설명

- `app_streamlit.py` : Streamlit 기반 웹 UI, 챗봇 및 PPT 생성기 모드 제공
- `app_fastapi.py`   : FastAPI 기반 API 서버, LLM 및 PPT 생성 엔드포인트 제공
- `claude_ppt.py`    : Claude API를 활용한 PPT 슬라이드 생성 로직
- `requirements.txt` : 프로젝트 의존성 목록

---

## 의존성

- streamlit
- langchain
- langchain-openai
- langchain-anthropic
- python-dotenv

---

## 참고/주의

- `__pycache__/` 폴더는 파이썬 캐시로, 버전 관리 및 배포에 포함하지 않아도 됩니다.
- 실제 서비스 배포 시, `.env` 파일 및 API 키는 외부에 노출되지 않도록 주의하세요.

---