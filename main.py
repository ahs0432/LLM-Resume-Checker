import streamlit as st
import os
import pandas as pd

st.set_page_config(
    page_title="메인 페이지",
    page_icon="📄",
    layout="wide"
)

st.title("🏠 메인 페이지")

st.markdown("--- ")

st.subheader("🚀 프로젝트 소개")
st.write("이 애플리케이션은 Gemini API를 활용하여 채용 프로세스를 자동화하고 효율화하는 것을 목표로 합니다.")
st.write("채용 공고 내용만으로 평가 항목과 프롬프트를 생성하고, 제출된 이력서를 자동으로 평가하여 정량적인 점수와 정성적인 피드백을 제공합니다.")

st.subheader("✨ 주요 기능")
col1, col2 = st.columns(2)
with col1:
    st.info("**채용 공고 관리**")
    st.write("- 채용 공고 내용을 입력하면 Gemini가 평가 항목과 프롬프트를 자동 생성합니다.")
    st.write("- 생성된 내용은 수정 및 저장이 가능합니다.")

with col2:
    st.success("**이력서 평가**")
    st.write("- 등록된 채용 공고에 지원자 이력서(PDF)를 제출합니다.")
    st.write("- Gemini가 이력서를 심층 분석하여 점수, 강/약점, 면접 질문을 생성합니다.")

st.subheader("📊 현황 대시보드")

job_postings_dir = os.path.join('data', 'job_postings')
csv_path = os.path.join('data', 'csv', 'resume_evaluations.csv')

num_job_postings = 0
if os.path.exists(job_postings_dir):
    num_job_postings = len([name for name in os.listdir(job_postings_dir) if name.endswith('.json')])

num_resumes = 0
if os.path.exists(csv_path):
    try:
        df = pd.read_csv(csv_path)
        num_resumes = len(df)
    except pd.errors.EmptyDataError:
        num_resumes = 0

col1, col2 = st.columns(2)
col1.metric("📝 등록된 채용 공고 수", f"{num_job_postings} 개")
col2.metric("📄 총 지원자 수", f"{num_resumes} 명")

st.markdown("--- ")
st.write("👈 사이드바에서 원하는 메뉴를 선택하여 시작하세요.")
