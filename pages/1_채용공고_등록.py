import streamlit as st
import json
import uuid
import os
import google.generativeai as genai
import openai

st.set_page_config(layout="wide")
st.title('채용 공고 관리')

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
        model = genai.GenerativeModel('gemini-2.5-pro')
    else:
        error_messages.append("Gemini API 키가 설정되지 않았습니다. 환경 변수(GOOGLE_API_KEY 또는 GEMINI_API_KEY) 또는 .streamlit/secrets.toml 파일을 확인해주세요.")

elif LLM_PROVIDER == "OPENAI":
    api_key = os.environ.get("OPENAI_API_KEY")
    if not api_key:
        api_key = st.secrets.get("OPENAI_API_KEY")
    
    if api_key:
        # OpenAI는 모델 객체를 미리 만들지 않고, API 호출 시 모델 이름을 지정합니다.
        model = "gpt-5" # 사용할 모델
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
def generate_with_llm(job_description):
    """Calls the selected LLM API to generate evaluation criteria and prompt."""
    prompt = f'''당신은 IT 회사 전문 채용 관리자입니다.
    아래 주어진 채용 공고 내용을 분석하여, 지원자의 역량을 평가하기 위한 기준과 LLM 평가자에게 전달할 프롬프트를 생성해야 합니다.

    **채용 공고:**
    --- 
    {job_description}
    ---

    **요구사항:**
    1.  **평가 항목 (evaluation_criteria):**
        - 채용 공고의 핵심 역량을 기반으로 3~5개의 평가 항목을 만드세요.
        - 각 항목의 배점은 총합이 200점이 되도록 분배하세요.
        - 예: "기술 스택 활용 능력", "문제 해결 능력", "커뮤니케이션 능력"
    2.  **LLM 프롬프트 (prompt):**
        - 지원자의 이력서를 평가할 LLM 평가자에게 제공할 프롬프트를 작성하세요.
        - 프롬프트에는 LLM의 역할, 평가 기준, 그리고 주어진 채용 공고 내용이 포함되어야 합니다.

    **출력 형식:**
    반드시 아래와 같은 JSON 형식으로만 응답해야 합니다. 다른 설명은 추가하지 마세요.

    ```json
    {{
        "evaluation_criteria": {{
            "항목1": 점수1,
            "항목2": 점수2
        }},
        "prompt": "LLM 평가자를 위한 프롬프트 내용"
    }}
    ```
    '''
    try:
        if LLM_PROVIDER == "GEMINI":
            # Set strict safety settings to prevent blocking
            safety_settings = {
                'HATE': 'BLOCK_NONE',
                'HARASSMENT': 'BLOCK_NONE',
                'SEXUAL': 'BLOCK_NONE',
                'DANGEROUS': 'BLOCK_NONE'
            }
            response = model.generate_content(prompt, safety_settings=safety_settings)

            # 1. Check for safety feedback
            if response.prompt_feedback and response.prompt_feedback.block_reason:
                st.error(f"Gemini API 요청이 안전 설정에 의해 차단되었습니다. 이유: {response.prompt_feedback.block_reason}")
                return None

            # 2. Check for empty response text
            if not response.text:
                st.error("Gemini API로부터 빈 응답을 받았습니다. 이력서 내용이나 API 설정에 문제가 있을 수 있습니다.")
                st.warning(f"전체 API 응답: {response}") # Log full response for debugging
                return None

            # 3. Clean and parse JSON
            cleaned_response = response.text.strip().replace("```json", "").replace("```", "")
            if not cleaned_response:
                st.error("API 응답에서 JSON 데이터를 찾을 수 없습니다.")
                st.warning(f"수신된 원본 텍스트: {response.text}")
                return None
                
            try:
                return json.loads(cleaned_response)
            except json.JSONDecodeError as e:
                st.error(f"API 응답을 JSON으로 파싱하는 데 실패했습니다: {e}")
                st.warning(f"파싱에 실패한 텍스트: {cleaned_response}")
                return None
        
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
            if not content:
                st.error("OpenAI API로부터 빈 응답을 받았습니다.")
                return None
            try:
                return json.loads(content)
            except json.JSONDecodeError as e:
                st.error(f"OpenAI API 응답을 JSON으로 파싱하는 데 실패했습니다: {e}")
                st.warning(f"파싱에 실패한 텍스트: {content}")
                return None

    except Exception as e:
        st.error(f"{LLM_PROVIDER} API 호출 중 오류가 발생했습니다: {e}")
        return None

# --- Initialize Session State ---
if 'job_title' not in st.session_state:
    st.session_state.job_title = ""
if 'job_description' not in st.session_state:
    st.session_state.job_description = ""
if 'evaluation_criteria' not in st.session_state:
    st.session_state.evaluation_criteria = ""
if 'prompt' not in st.session_state:
    st.session_state.prompt = ""

# --- Main Form ---
st.header("1. 채용 공고 입력")
st.session_state.job_title = st.text_input("채용 공고 제목", st.session_state.job_title)
st.session_state.job_description = st.text_area("채용 공고 내용", st.session_state.job_description, height=300)

if st.button(f"2. 평가 항목 및 프롬프트 자동 생성 ({LLM_PROVIDER})"):
    if not st.session_state.job_description:
        st.error("채용 공고 내용을 입력해주세요.")
    else:
        with st.spinner(f"{LLM_PROVIDER} API를 호출하여 평가 항목과 프롬프트를 생성 중입니다..."):
            generated_data = generate_with_llm(st.session_state.job_description)
            if generated_data:
                st.session_state.evaluation_criteria = "\n".join([f"{k}:{v}" for k, v in generated_data.get('evaluation_criteria', {}).items()])
                st.session_state.prompt = generated_data.get('prompt', '')
                st.success("자동 생성이 완료되었습니다. 아래 내용을 확인하고 수정할 수 있습니다.")

# --- Submission Form ---
st.header("3. 생성 결과 확인 및 등록")
with st.form("job_posting_form"):
    evaluation_criteria_input = st.text_area(
        "평가 항목 및 배점 (총점 200점)", 
        value=st.session_state.evaluation_criteria, 
        height=150
    )
    prompt_input = st.text_area(
        "LLM 프롬프트", 
        value=st.session_state.prompt, 
        height=400
    )

    submitted = st.form_submit_button("이 내용으로 공고 등록")

if submitted:
    # ... (The rest of the submission logic remains the same)
    if not all([st.session_state.job_title, st.session_state.job_description, evaluation_criteria_input]):
        st.error("제목, 내용, 평가 항목을 모두 채워주세요.")
        st.stop()

    criteria_lines = evaluation_criteria_input.strip().split('\n')
    criteria_dict = {}
    total_score = 0
    for line in criteria_lines:
        try:
            item, score = line.split(':')
            score = int(score.strip())
            criteria_dict[item.strip()] = score
            total_score += score
        except ValueError:
            st.error(f"잘못된 형식의 평가 항목입니다: {line}")
            st.stop()

    if total_score != 200:
        st.warning(f"평가 항목의 총점은 200점이어야 합니다. 현재 총점: {total_score}")
        st.stop()

    job_id = str(uuid.uuid4())
    job_data = {
        'id': job_id,
        'title': st.session_state.job_title,
        'description': st.session_state.job_description,
        'evaluation_criteria': criteria_dict,
        'prompt': prompt_input
    }

    job_postings_dir = os.path.join('data', 'job_postings')
    os.makedirs(job_postings_dir, exist_ok=True)
    file_path = os.path.join(job_postings_dir, f"{job_id}.json")
    with open(file_path, 'w', encoding='utf-8') as f:
        json.dump(job_data, f, ensure_ascii=False, indent=4)

    st.success(f"새로운 채용 공고가 성공적으로 등록되었습니다. (ID: {job_id})")
    st.json(job_data)

    for key in ['job_title', 'job_description', 'evaluation_criteria', 'prompt']:
        if key in st.session_state:
            del st.session_state[key]
    st.rerun()