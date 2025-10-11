# 이력서 평가 솔루션
## 프로젝트 개요
이 프로젝트는 Gemini API를 활용하여 채용 공고 분석 및 이력서 평가를 자동화하는 Streamlit 기반 웹 애플리케이션입니다.

## 주요 기능
- **채용 공고 분석 (Gemini)**: 채용 공고 내용을 입력하면 Gemini API가 자동으로 평가 항목과 LLM 프롬프트를 생성합니다.
- **이력서 평가 (Gemini)**: 생성된 채용 공고에 이력서(PDF)를 제출하면 Gemini API가 이력서를 분석하고, 설정된 기준에 따라 점수, 강점, 약점, 면접 질문 등을 생성합니다.
- **데이터 관리**: 모든 채용 공고와 이력서 평가 결과는 영구적으로 저장 및 관리됩니다.

## 기술 스택
- **언어/프레임워크**: Python, Streamlit
- **LLM**: Google Gemini Pro
- **환경**: Python 3.11 이상, Docker

---

## 사전 준비: Gemini API 키 설정
이 애플리케이션을 사용하려면 Google Gemini API 키가 필요합니다.

1. [Google AI Studio](https://aistudio.google.com/app/apikey)에 방문하여 API 키를 발급받으세요.
2. 발급받은 API 키를 아래 실행 방법 중 하나에 맞게 설정합니다.

---

## Docker를 이용한 실행 방법 (권장)
Docker를 사용하면 복잡한 설치 과정 없이 애플리케이션을 실행할 수 있습니다.

1. **Docker 이미지 빌드**
```bash
docker build -t resume-checker .
```

2. **Docker 컨테이너 실행**
아래 명령어의 `YOUR_GEMINI_API_KEY` 부분을 실제 API 키로 교체하여 실행하세요.
```bash
docker run -p 8501:8501 \
    -v ./data:/app/data \
    -e GEMINI_API_KEY="YOUR_GEMINI_API_KEY" \
    resume-checker
```
- `-p 8501:8501`: 로컬 포트와 컨테이너 포트를 연결합니다.
- `-v ./data:/app/data`: 로컬 `data` 폴더를 컨테이너와 연결하여 데이터를 영구 저장합니다.
- `-e GEMINI_API_KEY=...`: Gemini API 키를 컨테이너의 환경 변수로 전달합니다.

3. **애플리케이션 접속**
웹 브라우저에서 `http://localhost:8501` 주소로 접속합니다.

---

## 로컬 환경 실행 방법

1. **API 키 설정**
`.streamlit/secrets.toml` 파일을 열고, `GEMINI_API_KEY` 값을 실제 API 키로 교체합니다.
```toml
# .streamlit/secrets.toml
GEMINI_API_KEY = "YOUR_API_KEY_HERE"
```

2. **가상환경 생성 및 라이브러리 설치**
```bash
# (uv가 설치되어 있다고 가정)
uv venv
source .venv/bin/activate  # Linux/macOS
.venv\Scripts\activate  # Windows
uv pip install -r requirements.txt
```

3. **Streamlit 실행**
```bash
streamlit run main.py
```
