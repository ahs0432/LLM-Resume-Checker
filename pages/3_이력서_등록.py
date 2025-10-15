import streamlit as st
import os
import json
import uuid
import pandas as pd
from pypdf import PdfReader
import google.generativeai as genai
import openai

st.title("이력서 등록 및 평가")

# --- LLM Configuration ---
LLM_PROVIDER = os.environ.get("LLM_PROVIDER").upper()
if not LLM_PROVIDER:
    LLM_PROVIDER = st.secrets.get("LLM_PROVIDER").upper()

if not LLM_PROVIDER:
    LLM_PROVIDER = "GEMINI"
    
api_key = None
model = None
error_messages = []

if LLM_PROVIDER == "GEMINI":
    # 환경 변수를 우선적으로 확인 (GOOGLE_API_KEY, GEMINI_API_KEY)
    api_key = os.environ.get("GOOGLE_API_KEY") or os.environ.get("GEMINI_API_KEY")
    # 환경 변수가 없는 경우에만 Streamlit secrets에서 가져옴
    if not api_key:
        api_key = st.secrets.get("GOOGLE_API_KEY") or st.secrets.get("GEMINI_API_KEY")

    if api_key:
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel('gemini-1.5-pro-latest')
    else:
        error_messages.append("Gemini API 키가 설정되지 않았습니다. 환경 변수(GOOGLE_API_KEY 또는 GEMINI_API_KEY) 또는 .streamlit/secrets.toml 파일을 확인해주세요.")

elif LLM_PROVIDER == "OPENAI":
    api_key = os.environ.get("OPENAI_API_KEY")
    if not api_key:
        api_key = st.secrets.get("OPENAI_API_KEY")
    
    if api_key:
        # OpenAI는 모델 객체를 미리 만들지 않고, API 호출 시 모델 이름을 지정합니다.
        model = "gpt-4-turbo" # 사용할 모델
    else:
        error_messages.append("OpenAI API 키가 설정되지 않았습니다. 환경 변수(OPENAI_API_KEY) 또는 .streamlit/secrets.toml 파일을 확인해주세요.")

else:
    error_messages.append(f"지원하지 않는 LLM_PROVIDER입니다: {LLM_PROVIDER}. 'GEMINI' 또는 'OPENAI' 중에서 선택해주세요.")

if error_messages:
    for msg in error_messages:
        st.error(msg)
    st.stop()

st.info(f"현재 사용 중인 LLM: **{LLM_PROVIDER}**")


# --- Utility Functions ---
def get_job_postings():
    job_postings_dir = os.path.join('data', 'job_postings')
    if not os.path.exists(job_postings_dir):
        return {}
    postings = {}
    for filename in os.listdir(job_postings_dir):
        if filename.endswith('.json'):
            file_path = os.path.join(job_postings_dir, filename)
            with open(file_path, 'r', encoding='utf-8') as f:
                job_data = json.load(f)
                postings[job_data['id']] = job_data['title']
    return postings

def evaluate_with_llm(job_details, resume_text):
    """Calls the selected LLM API to evaluate a resume."""
    llm_prompt = job_details['prompt']
    evaluation_criteria = job_details['evaluation_criteria']

    prompt = f'''"{llm_prompt}

    **평가 항목:**
    {json.dumps(evaluation_criteria, ensure_ascii=False, indent=4)}

    **지원자 이력서:**
    --- 
    {resume_text}
    ---

    **요구사항:**
    위 평가 항목과 채용 공고를 바탕으로 지원자의 이력서를 평가해주세요.
    각 평가 항목에 대한 점수, 총점, 강점, 약점, 그리고 면접 질문 10가지를 생성해야 합니다.

    **출력 형식:**
    반드시 아래와 같은 JSON 형식으로만 응답해야 합니다. 다른 설명은 추가하지 마세요.

    ```json
    {{
        "scores": {{
            "<평가 항목 1>": <점수1>,
            "<평가 항목 2>": <점수2>
        }},
        "total_score": <총점 (숫자만, scores의 합계)>,
        "strengths": "<강점 요약>",
        "weaknesses": "<약점 요약>",
        "interview_questions": [
            "면접 질문 1",
            "면접 질문 2",
            "면접 질문 3",
            "면접 질문 4",
            "면접 질문 5",
            "면접 질문 6",
            "면접 질문 7",
            "면접 질문 8",
            "면접 질문 9",
            "면접 질문 10"
        ]
    }}
    ```
    '''
    try:
        if LLM_PROVIDER == "GEMINI":
            response = model.generate_content(prompt)
            cleaned_response = response.text.strip().replace("```json", "").replace("```", "")
            return json.loads(cleaned_response)
        
        elif LLM_PROVIDER == "OPENAI":
            client = openai.OpenAI(api_key=api_key)
            response = client.chat.completions.create(
                model=model,
                messages=[
                    {"role": "system", "content": "You are a helpful assistant designed to output JSON."},
                    {"role": "user", "content": prompt}
                ],
                response_format={"type": "json_object"}
            )
            content = response.choices[0].message.content
            return json.loads(content)

    except Exception as e:
        st.error(f"{LLM_PROVIDER} API 호출 중 오류가 발생했습니다: {e}")
        return None

# --- Page Logic ---
job_postings = get_job_postings()
if not job_postings:
    st.warning("등록된 채용 공고가 없습니다. 먼저 채용 공고를 등록해주세요.")
    st.stop()

st.header("1. 이력서 제출")
selected_job_id = st.selectbox("채용 공고 선택", options=list(job_postings.keys()), format_func=lambda x: job_postings[x])
applicant_name = st.text_input("지원자 이름")
uploaded_file = st.file_uploader("이력서 파일 (PDF)", type=['pdf'])

if st.button(f"2. 제출 및 평가 시작 ({LLM_PROVIDER})"):
    if not all([selected_job_id, applicant_name, uploaded_file]):
        st.error("모든 항목을 입력하고 파일을 업로드해주세요.")
        st.stop()

    with st.spinner(f'이력서를 처리하고 {LLM_PROVIDER} API로 평가하는 중입니다...'):
        # --- File Processing ---
        submission_id = str(uuid.uuid4())
        pdf_dir = os.path.join('data', 'pdf')
        os.makedirs(pdf_dir, exist_ok=True)
        pdf_filename = f"{submission_id}_{uploaded_file.name}"
        pdf_path = os.path.join(pdf_dir, pdf_filename)
        with open(pdf_path, "wb") as f:
            f.write(uploaded_file.getbuffer())

        try:
            reader = PdfReader(pdf_path)
            resume_text = "".join([page.extract_text() or "" for page in reader.pages])
        except Exception as e:
            st.error(f"PDF 파일 처리 중 오류가 발생했습니다: {e}")
            st.stop()

        # --- LLM Evaluation ---
        job_details_path = os.path.join('data', 'job_postings', f"{selected_job_id}.json")
        with open(job_details_path, 'r', encoding='utf-8') as f:
            job_details = json.load(f)
        
        evaluation_result = evaluate_with_llm(job_details, resume_text)

        if not evaluation_result:
            st.error("평가에 실패했습니다. 이력서 내용이나 API 키를 확인해주세요.")
            st.stop()

        st.subheader("평가 결과")
        st.json(evaluation_result)

        # --- Save to CSV ---
        csv_path = os.path.join('data', 'csv', 'resume_evaluations.csv')
        os.makedirs(os.path.dirname(csv_path), exist_ok=True)
        new_data = {
            'submission_id': submission_id,
            'job_id': selected_job_id,
            'job_title': job_postings[selected_job_id],
            'applicant_name': applicant_name,
            'total_score': evaluation_result.get('total_score'),
            'scores': json.dumps(evaluation_result.get('scores', {})),
            'strengths': evaluation_result.get('strengths'),
            'weaknesses': evaluation_result.get('weaknesses'),
            'interview_questions': "; ".join(evaluation_result.get('interview_questions', [])),
            'pdf_path': pdf_path,
            'submission_date': pd.Timestamp.now()
        }

        df = pd.read_csv(csv_path) if os.path.exists(csv_path) else pd.DataFrame()
        df = pd.concat([df, pd.DataFrame([new_data])], ignore_index=True)
        df.to_csv(csv_path, index=False, encoding='utf-8-sig')
        st.success(f"평가 결과가 {csv_path}에 저장되었습니다.")