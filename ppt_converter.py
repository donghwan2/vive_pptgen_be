import os
import json
import re
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from langchain_anthropic import ChatAnthropic
from typing import List, Optional
import tempfile
import subprocess
from datetime import datetime

from anthropic import Anthropic

class ContentToPPTXConverter:
    def __init__(self, claude_api_key, claude_model="claude-sonnet-4-20250514"):
        self.api_key = claude_api_key
        self.model = claude_model
        
        self.anthropic = Anthropic(api_key=self.api_key)
        self.inkscape_path = "/usr/bin/inkscape"  # Linux/Mac 경로

        self.system_prompt = """# 역할
당신은 15년차 경력의 데이터 시각화, 그래픽 디자인 전문가입니다. 경영진 대상 발표자료 제작을 담당하고 있습니다.

# 목적
업로드된 문서를 검토하여, 슬라이드 표지, 차트 및 그래프로 변환 가능한 핵심 데이터를 식별해주세요. 라인 차트, 바 차트, 원형 차트 등 최적의 시각화 방식을 제안하고 구현해주세요.

# 형식
16:9 비율의 프레젠테이션용 슬라이드를 제작하려 합니다. SVG 형태로 제공해주세요. SVG 결과물의 정확성을 자체 점검하고, 문제 발견 시 재작업해주세요.

# 지침
- 전반적인 톤앤매너는 미니멀하고 세련되게 구성해주세요.
- 데이터를 시각화 하는 것이 중요합니다. 각 슬라이드마다 데이터 차트, 그래프, 인포그래픽을 배치하고, 각 페이지의 수치나 지표가 즉시 파악되도록 간결하게 설계해주세요.
- 색상은 연그린, 에메랄드, 검정, 회색, 흰색을 세련되게 적용하고, 폰트는 나눔고딕과 같은 깔끔한 폰트를 활용하세요.
- SVG 내에서 한글 폰트는 font-family="NanumGothic, Arial, sans-serif"로 설정하세요.
- 모든 텍스트는 SVG 내에서 직접 렌더링되도록 <text> 태그를 사용하세요.
- SVG는 반드시 완전한 형태로 작성하고, 특수문자는 이스케이프 처리하지 마세요.
- SVG 크기는 width="1920" height="1080"으로 16:9 비율을 맞춰주세요.

모든 출력은 JSON 형식으로 아래와 같이 구성해주세요:
```json
{
    "slides": [
        {"title": "슬라이드 제목", "svg": "완전한 SVG 코드"}
    ]
}
```"""

    def generate_slides_from_content(self, content):
        """내용을 입력받아 Claude를 통해 슬라이드 생성"""
        try:
            message = self.anthropic.messages.create(
                model=self.model,
                max_tokens=15000,
                system=self.system_prompt,
                messages=[{"role": "user", "content": content}]
            )
            return message.content[0].text
        except Exception as e:
            print(f"❌ Claude API 호출 실패: {e}")
            return None

    def extract_json_from_response(self, response_text):
        """응답에서 JSON 데이터 추출"""
        try:
            # 1. JSON 블록 찾기
            json_pattern = r'```json\s*(.*?)\s*```'
            json_matches = re.findall(json_pattern, response_text, re.DOTALL)

            for json_str in json_matches:
                try:
                    data = json.loads(json_str)
                    if "slides" in data:
                        return data["slides"]
                except json.JSONDecodeError:
                    continue

            # 2. 직접 JSON 찾기
            direct_json_pattern = r'\{\s*"slides"\s*:\s*\[(.*?)\]\s*\}'
            direct_match = re.search(direct_json_pattern, response_text, re.DOTALL)

            if direct_match:
                try:
                    full_json = direct_match.group(0)
                    data = json.loads(full_json)
                    return data["slides"]
                except json.JSONDecodeError:
                    pass

            return []

        except Exception as e:
            print(f"❌ JSON 추출 실패: {e}")
            return []

    def clean_svg_content(self, svg_content):
        """SVG 내용 정리"""
        if not svg_content:
            return ""

        svg_content = svg_content.replace('\\"', '"')
        svg_content = svg_content.replace('\\n', '\n')
        svg_content = svg_content.replace('\\t', '\t')
        svg_content = svg_content.strip()

        if not svg_content.startswith('<?xml'):
            svg_content = '<?xml version="1.0" encoding="UTF-8"?>\n' + svg_content

        if '<svg' in svg_content and 'xmlns=' not in svg_content:
            svg_content = svg_content.replace('<svg', '<svg xmlns="http://www.w3.org/2000/svg"')

        return svg_content