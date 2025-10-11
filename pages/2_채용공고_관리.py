import streamlit as st
import os
import json

st.set_page_config(layout="wide")
st.title("등록된 채용 공고 관리")

# --- Utility Functions ---
def get_job_postings():
    job_postings_dir = os.path.join('data', 'job_postings')
    if not os.path.exists(job_postings_dir):
        return {}
    postings = {}
    for filename in sorted(os.listdir(job_postings_dir), reverse=True):
        if filename.endswith('.json'):
            file_path = os.path.join(job_postings_dir, filename)
            with open(file_path, 'r', encoding='utf-8') as f:
                job_data = json.load(f)
                postings[job_data['id']] = job_data
    return postings

def format_criteria_for_display(criteria_dict):
    return "\n".join([f"{item}: {score}" for item, score in criteria_dict.items()])

# --- Initialize Session State ---
if 'editing_job_id' not in st.session_state:
    st.session_state.editing_job_id = None

# --- Page Logic ---
job_postings = get_job_postings()

# If we are in editing mode, show the form
if st.session_state.editing_job_id:
    job_id = st.session_state.editing_job_id
    job_data = job_postings[job_id]

    st.header(f"'{job_data['title']}' 공고 수정")

    with st.form(key=f"edit_form_{job_id}"):
        new_title = st.text_input("채용 공고 제목", value=job_data['title'])
        new_description = st.text_area("채용 공고 내용", value=job_data['description'], height=200)
        new_criteria_str = st.text_area("평가 항목", value=format_criteria_for_display(job_data['evaluation_criteria']), height=150)
        new_prompt = st.text_area("LLM 프롬프트", value=job_data['prompt'], height=300)

        save_button = st.form_submit_button("저장")
        cancel_button = st.form_submit_button("취소")

    if save_button:
        # Parse and validate criteria
        criteria_lines = new_criteria_str.strip().split('\n')
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

        # Update data
        job_data['title'] = new_title
        job_data['description'] = new_description
        job_data['evaluation_criteria'] = criteria_dict
        job_data['prompt'] = new_prompt

        # Save to file
        file_path = os.path.join('data', 'job_postings', f"{job_id}.json")
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(job_data, f, ensure_ascii=False, indent=4)
        
        st.success("채용 공고가 성공적으로 수정되었습니다.")
        st.session_state.editing_job_id = None
        st.rerun()

    if cancel_button:
        st.session_state.editing_job_id = None
        st.rerun()

# If not in editing mode, show the list
else:
    if not job_postings:
        st.warning("등록된 채용 공고가 없습니다. '채용공고 등록' 페이지에서 먼저 공고를 등록해주세요.")
        st.stop()

    st.header("채용 공고 목록")
    st.write("수정 또는 삭제할 채용 공고를 펼쳐서 확인하세요.")

    for job_id, posting in job_postings.items():
        with st.expander(f"{posting['title']}"):
            st.markdown(f"**ID:** `{posting['id']}`")
            st.subheader("공고 내용")
            st.code(posting['description'], language='markdown')
            st.subheader("평가 항목")
            st.json(posting['evaluation_criteria'])
            st.subheader("LLM 프롬프트")
            st.code(posting['prompt'], language='markdown')

            col1, col2, _ = st.columns([0.1, 0.1, 0.8])
            
            if col1.button("수정", key=f"edit_{job_id}"):
                st.session_state.editing_job_id = job_id
                st.rerun()
            
            if col2.button("삭제", key=f"delete_{job_id}"):
                file_path = os.path.join('data', 'job_postings', f"{job_id}.json")
                if os.path.exists(file_path):
                    os.remove(file_path)
                    st.success(f"'{posting['title']}' 공고가 삭제되었습니다.")
                    st.rerun()
