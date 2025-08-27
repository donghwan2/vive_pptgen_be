import os
import json
import re
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware  # CORS 추가
from pydantic import BaseModel
from langchain_anthropic import ChatAnthropic
from typing import List, Optional
import tempfile
import subprocess
from datetime import datetime

from models import ChatRequest, ChatResponse, PPTRequest, Slide, PPTResponse
from ppt_converter import ContentToPPTXConverter

load_dotenv()

SYSTEM_PROMPT = "보고서를 작성해줘"
llm = ChatAnthropic(model_name="claude-sonnet-4-20250514", temperature=0.2)

# FastAPI 애플리케이션
app = FastAPI(title="LLM Chatbot & PPT Generator API")

# CORS 설정 추가
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://43.202.0.119:8080",
        "http://localhost:3000",       # React 개발 서버
        "http://127.0.0.1:3000",       # 로컬호스트 대안
        "http://10.34.11.38:3000"      # 네트워크 주소
    ],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE"],
    allow_headers=["*"],
)

# 전역 대화 히스토리
chat_history = [{"role": "system", "content": SYSTEM_PROMPT}]

# /chat 엔드포인트
@app.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    """사용자 메시지를 받아 LLM 응답 반환"""
    
    chat_history.append({"role": "user", "content": request.message})
    llm_response = llm.invoke(chat_history)
    chat_history.append({"role": "assistant", "content": llm_response.content})
    
    return {"response": llm_response.content}
    print("chat 실행됨")

# /generate-ppt 엔드포인트
@app.post("/generate-ppt", response_model=PPTResponse)
async def generate_ppt(request: PPTRequest):
    """보고서 내용을 받아 PPT 슬라이드 생성"""
    
    try:
        # Claude API 키 확인
        claude_api_key = os.getenv("ANTHROPIC_API_KEY")
        if not claude_api_key:
            raise HTTPException(status_code=500, detail="ANTHROPIC_API_KEY가 설정되지 않았습니다.")
        
        # PPT 변환기 초기화
        converter = ContentToPPTXConverter(claude_api_key)
        
        # Claude를 통해 슬라이드 생성
        claude_response = converter.generate_slides_from_content(request.report_content)
        if not claude_response:
            raise HTTPException(status_code=500, detail="Claude API 호출에 실패했습니다.")
        
        # 슬라이드 데이터 추출
        slides_data = converter.extract_json_from_response(claude_response)
        if not slides_data:
            raise HTTPException(status_code=500, detail="슬라이드 데이터를 추출할 수 없습니다.")
        
        # 슬라이드 정리
        slides = []
        for slide_data in slides_data:
            cleaned_svg = converter.clean_svg_content(slide_data.get("svg", ""))
            slides.append(Slide(
                title=slide_data.get("title", ""),
                svg=cleaned_svg
            ))
        
        return PPTResponse(
            slides=slides,
            message=f"총 {len(slides)}개의 고품질 슬라이드가 생성되었습니다."
        )
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"PPT 생성 중 오류가 발생했습니다: {str(e)}")

# 서버 상태 확인용 엔드포인트 추가
@app.get("/")
async def root():
    return {"message": "PPT Generator API is running!!!"}

@app.get("/health")
async def health_check():
    return {"status": "healthy", "timestamp": datetime.now().isoformat()}