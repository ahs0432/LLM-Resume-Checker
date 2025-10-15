# AI 기반 이력서 평가 솔루션
## 프로젝트 개요
이 프로젝트는 Gemini 또는 OpenAI와 같은 LLM(거대 언어 모델)을 활용하여 채용 공고 분석 및 이력서 평가를 자동화하는 Streamlit 기반 웹 애플리케이션입니다.

## 주요 기능
- **채용 공고 분석 (AI)**: 채용 공고 내용을 입력하면 AI가 자동으로 평가 항목과 평가용 프롬프트를 생성합니다.
- **이력서 평가 (AI)**: 생성된 채용 공고에 이력서(PDF)를 제출하면 AI가 이력서를 분석하고, 설정된 기준에 따라 점수, 강점, 약점, 면접 질문 등을 생성합니다.
- **LLM 선택 가능**: 환경 변수 설정을 통해 Google Gemini와 OpenAI(ChatGPT) 모델 중에서 선택하여 사용할 수 있습니다.
- **데이터 관리**: 모든 채용 공고와 이력서 평가 결과는 영구적으로 저장 및 관리됩니다.

## 기술 스택
- **언어/프레임워크**: Python, Streamlit
- **LLM**: Google Gemini, OpenAI GPT
- **환경**: Python 3.11 이상, Docker

---

## 사전 준비: API 키 설정
이 애플리케이션을 사용하려면 LLM 공급자(Google 또는 OpenAI)의 API 키가 필요합니다.

- **Google Gemini API 키**:
  1. [Google AI Studio](https://aistudio.google.com/app/apikey)에 방문하여 API 키를 발급받으세요.
  2. 발급받은 키를 `GOOGLE_API_KEY` 또는 `GEMINI_API_KEY` 환경 변수에 설정합니다.

- **OpenAI API 키**:
  1. [OpenAI Platform](https://platform.openai.com/api-keys)에 방문하여 API 키를 발급받으세요.
  2. 발급받은 키를 `OPENAI_API_KEY` 환경 변수에 설정합니다.

---

## Docker를 이용한 실행 방법 (권장)
Docker를 사용하면 복잡한 설치 과정 없이 애플리케이션을 실행할 수 있습니다.

1. **Docker 이미지 빌드**
```bash
docker build -t resume-checker .
```

2. **Docker 컨테이너 실행**
사용하려는 LLM에 따라 아래 예시 중 하나를 선택하여 실행하세요.

**예시 1: Google Gemini 사용 시**
```bash
docker run -p 8501:8501 \
    -v ./data:/app/data \
    -e LLM_PROVIDER="GEMINI" \
    -e GOOGLE_API_KEY="YOUR_GOOGLE_API_KEY" \
    resume-checker
```

**예시 2: OpenAI 사용 시**
```bash
docker run -p 8501:8501 \
    -v ./data:/app/data \
    -e LLM_PROVIDER="OPENAI" \
    -e OPENAI_API_KEY="YOUR_OPENAI_API_KEY" \
    resume-checker
```

**환경 변수 설명:**
- `-p 8501:8501`: 로컬 포트와 컨테이너 포트를 연결합니다.
- `-v ./data:/app/data`: 로컬 `data` 폴더를 컨테이너와 연결하여 데이터를 영구 저장합니다.
- `-e LLM_PROVIDER=...`: 사용할 LLM을 지정합니다 (`GEMINI` 또는 `OPENAI`). 설정하지 않으면 `GEMINI`가 기본값입니다.
- `-e GOOGLE_API_KEY=...`: Google Gemini API 키를 전달합니다.
- `-e OPENAI_API_KEY=...`: OpenAI API 키를 전달합니다.

3. **애플리케이션 접속**
웹 브라우저에서 `http://localhost:8501` 주소로 접속합니다.

---

## 로컬 환경 실행 방법

1. **API 키 설정**
`.streamlit/secrets.toml` 파일을 열고, 사용할 API 키를 추가합니다.
```toml
# .streamlit/secrets.toml

# Google Gemini API 키 (둘 중 하나 사용)
GOOGLE_API_KEY = "YOUR_GOOGLE_API_KEY"
# GEMINI_API_KEY = "YOUR_GEMINI_API_KEY" # 이전 버전 호환용

# OpenAI API 키
OPENAI_API_KEY = "YOUR_OPENAI_API_KEY"
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
사용할 LLM에 따라 환경 변수를 설정하고 앱을 실행합니다.

**예시 1: Google Gemini 사용 시**
```bash
# Linux/macOS
export LLM_PROVIDER="GEMINI"
streamlit run main.py

# Windows
set LLM_PROVIDER="GEMINI"
streamlit run main.py
```

**예시 2: OpenAI 사용 시**
```bash
# Linux/macOS
export LLM_PROVIDER="OPENAI"
streamlit run main.py

# Windows
set LLM_PROVIDER="OPENAI"
streamlit run main.py
```