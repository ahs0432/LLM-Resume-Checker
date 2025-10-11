import streamlit as st
import os
import json
import pandas as pd

st.title("채용 공고별 지원자 보기")

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

# --- Page Logic ---
job_postings = get_job_postings()
if not job_postings:
    st.warning("등록된 채용 공고가 없습니다.")
    st.stop()

st.header("1. 채용 공고 선택")
selected_job_id = st.selectbox("확인할 채용 공고를 선택하세요", options=list(job_postings.keys()), format_func=lambda x: job_postings[x])

st.markdown("--- ")

csv_path = os.path.join('data', 'csv', 'resume_evaluations.csv')

if os.path.exists(csv_path) and selected_job_id:
    try:
        df_all = pd.read_csv(csv_path)
        df_filtered = df_all[df_all['job_id'] == selected_job_id].copy()

        if df_filtered.empty:
            st.info("해당 채용 공고에 등록된 지원자가 없습니다.")
        else:
            st.header("2. 지원자 목록")
            st.write("상세보기를 원하는 지원자를 선택하세요.")

            # Add a 'select' column for the data_editor
            df_filtered['select'] = False
            
            # Reorder columns to have 'select' first
            cols = ['select'] + [col for col in df_filtered.columns if col != 'select']
            df_display = df_filtered[cols]

            # Use st.data_editor to create an interactive table
            edited_df = st.data_editor(
                df_display,
                hide_index=True,
                column_config={
                    "select": st.column_config.CheckboxColumn("상세보기", default=False),
                    "applicant_name": "지원자명",
                    "total_score": "총점",
                    "strengths": "강점",
                    "weaknesses": "약점",
                },
                # Disable editing for all columns except 'select'
                disabled=[col for col in df_filtered.columns if col != 'select']
            )

            # Find the selected applicants
            selected_applicants = edited_df[edited_df['select']]

            st.markdown("--- ")
            st.header("3. 지원자별 상세 평가 결과")

            if selected_applicants.empty:
                st.info("상세보기를 원하는 지원자를 위 표에서 선택해주세요.")
            else:
                for _, row in selected_applicants.iterrows():
                    with st.container(border=True):
                        st.subheader(f"{row['applicant_name']} (총점: {row['total_score']})")
                        
                        st.subheader("📊 세부 점수")
                        try:
                            scores_dict = json.loads(row['scores'])
                            scores_df = pd.DataFrame(scores_dict.items(), columns=['평가 항목', '점수'])
                            st.table(scores_df)
                        except (json.JSONDecodeError, TypeError, AttributeError):
                            st.warning("세부 점수를 표시할 수 없습니다.")

                        st.subheader("👍 강점")
                        st.info(row['strengths'])
                        
                        st.subheader("👎 약점")
                        st.warning(row['weaknesses'])
                        
                        st.subheader("💡 면접 질문 추천 (10개)")
                        questions = str(row.get('interview_questions', '')).split('; ')
                        for i, q in enumerate(questions):
                            if q:
                                st.markdown(f"{i+1}. {q}")
                        
                        st.download_button(
                            label="📄 이력서 PDF 다운로드",
                            data=open(row['pdf_path'], "rb").read(),
                            file_name=os.path.basename(row['pdf_path'])
                        )
                        st.write(" ") # Add some space

    except pd.errors.EmptyDataError:
        st.info("평가 데이터가 없습니다.")
    except FileNotFoundError:
        st.error("resume_evaluations.csv 파일을 찾을 수 없습니다. 이력서를 먼저 평가해주세요.")
    except Exception as e:
        st.error(f"데이터를 불러오는 중 오류가 발생했습니다: {e}")
else:
    st.info("아직 평가된 이력서가 없습니다.")
