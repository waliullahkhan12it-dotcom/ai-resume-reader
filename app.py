import os
import streamlit as st
from google import genai
from google.genai import types
import pypdf
from docx import Document

# Page Configuration
st.set_page_config(
    page_title="AI ATS Resume Analyzer",
    page_icon="📄",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for styling
st.markdown("""
    <style>
    .main-header {
        font-size: 2.2rem;
        color: #1E3A8A;
        font-weight: 700;
        margin-bottom: 0.5rem;
    }
    .sub-header {
        font-size: 1.1rem;
        color: #4B5563;
        margin-bottom: 2rem;
    }
    </style>
""", unsafe_allow_html=True)

def extract_text_from_pdf(uploaded_file) -> str:
    reader = pypdf.PdfReader(uploaded_file)
    text = ""
    for page in reader.pages:
        extracted = page.extract_text()
        if extracted:
            text += extracted + "\n"
    return text

def extract_text_from_docx(uploaded_file) -> str:
    doc = Document(uploaded_file)
    text = ""
    for paragraph in doc.paragraphs:
        text += paragraph.text + "\n"
    return text

def analyze_resume(api_key: str, resume_text: str, job_description: str) -> str:
    client = genai.Client(api_key=api_key)
    
    prompt = f"""
    You are an expert ATS (Applicant Tracking System) scanner, career coach, and professional technical recruiter.
    Analyze the following resume against the provided job description.

    JOB DESCRIPTION:
    {job_description}

    RESUME TEXT:
    {resume_text}

    Provide your evaluation strictly in the following structured markdown format:

    ### 📊 ATS Match Score
    Provide a score out of 100 (e.g., **78/100**) based on keyword optimization, formatting suitability, and relevance to the job description.

    ### 🎯 Strengths
    - Bullet points highlighting what the resume does well regarding the target role.

    ### ⚠️ Missing Keywords & Gaps
    - Bullet points identifying crucial skills, technologies, or keywords from the job description missing in the resume.

    ### 🛠️ Actionable Improvements
    - Clear, specific advice on how to rewrite sections, bullet points, or add missing details to boost the ATS score.

    ### 📝 Polished Summary Recommendation
    - Suggest an optimized, impactful professional summary tailored to this job description.
    """

    response = client.models.generate_content(
        model='gemini-2.5-flash',
        contents=prompt
    )
    return response.text

# --- Sidebar ---
with st.sidebar:
    st.image("https://img.icons8.com/color/96/resume.png", width=80)
    st.title("Configuration")
    
    api_key_input = st.text_input(
        "Enter Google Gemini API Key", 
        type="password", 
        help="Get your free API key from Google AI Studio."
    )
    
    st.markdown("---")
    st.markdown("### 💡 Tips")
    st.markdown("- Upload clean, text-based PDFs or Word documents.")
    st.markdown("- Paste the complete job description including requirements.")

# --- Main Interface ---
st.markdown('<div class="main-header">📄 AI ATS Resume Analyzer</div>', unsafe_allow_html=True)
st.markdown('<div class="sub-header">Optimize your resume against specific job descriptions using Google Gemini Flash.</div>', unsafe_allow_html=True)

col1, col2 = st.columns([1, 1], gap="large")

with col1:
    st.subheader("1. Job Details")
    job_description = st.text_area(
        "Paste Target Job Description",
        placeholder="Paste role requirements, tech stack, and responsibilities here...",
        height=300
    )

with col2:
    st.subheader("2. Upload Resume")
    uploaded_file = st.file_uploader(
        "Upload Resume (PDF or DOCX)",
        type=["pdf", "docx"],
        help="Supports PDF and Word document formats."
    )
    
    if uploaded_file is not None:
        file_size_kb = uploaded_file.size / 1024
        st.success(f"Uploaded: **{uploaded_file.name}** ({file_size_kb:.1f} KB)")

st.markdown("---")

analyze_btn = st.button("🚀 Analyze Resume with AI", type="primary", use_container_width=True)

if analyze_btn:
    if not api_key_input:
        st.error("⚠️ Please enter your Google Gemini API Key in the sidebar.")
    elif not job_description.strip():
        st.error("⚠️ Please provide a target job description.")
    elif uploaded_file is None:
        st.error("⚠️ Please upload a resume file.")
    else:
        with st.spinner("🔍 Scanning resume and analyzing with Gemini Flash..."):
            try:
                if uploaded_file.type == "application/pdf":
                    resume_text = extract_text_from_pdf(uploaded_file)
                else:
                    resume_text = extract_text_from_docx(uploaded_file)
                
                if not resume_text.strip():
                    st.error("❌ Could not extract text from the uploaded file.")
                else:
                    analysis_result = analyze_resume(api_key_input, resume_text, job_description)
                    st.markdown("---")
                    st.markdown("## 📋 Analysis Results")
                    st.markdown(analysis_result)
                    
            except Exception as e:
                st.error(f"An error occurred during analysis: {e}")
