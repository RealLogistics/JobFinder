
import openai
import streamlit as st
import fitz  # For PDFs
import docx  # For DOCX files
import requests  # For live job listings

# Set your OpenAI API key here
openai.api_key = st.secrets ["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"]

st.set_page_config(page_title="Job Finder AI", layout="centered")
st.markdown("""
<style>
    body {
        background-color: #f4f7fa;
        color: #333;
        font-family: 'Segoe UI', sans-serif;
    }
    .stApp {
        background-image: linear-gradient(to right, #e0f7fa, #e8f5e9);
        border-radius: 10px;
        padding: 20px;
    }
    .stButton>button {
        background-color: #00796b;
        color: white;
        border-radius: 10px;
        font-weight: bold;
    }
    .stTextInput>div>input, .stTextArea>div>textarea {
        border-radius: 10px;
        padding: 10px;
    }
</style>
""", unsafe_allow_html=True)

st.title("🌟 Job Finder AI")

st.markdown("""
Welcome! Upload your resume (PDF or Word), and this app will extract your skills, match them to job listings, and even generate a custom cover letter.
""")

st.markdown("### 📄 Upload your resume (PDF or DOCX)")
uploaded_file = st.file_uploader("Choose your resume file", type=["pdf", "docx"])
resume_text = ""

if uploaded_file:
    if uploaded_file.name.endswith(".pdf"):
        with fitz.open(stream=uploaded_file.read(), filetype="pdf") as doc:
            for page in doc:
                resume_text += page.get_text()
    elif uploaded_file.name.endswith(".docx"):
        doc = docx.Document(uploaded_file)
        for para in doc.paragraphs:
            resume_text += para.text + "\n"

    st.success("✅ Resume loaded successfully!")
    st.text_area("📝 Extracted Resume Text", resume_text, height=300)

# 🔄 Fetch sample remote jobs (placeholder using RemoteOK API-style public sample)
def fetch_remote_jobs():
    try:
        url = "https://remoteok.io/api"
        response = requests.get(url)
        if response.status_code == 200:
            jobs_data = response.json()
            jobs = []
            for job in jobs_data:
                if isinstance(job, dict) and 'position' in job and 'tags' in job:
                    jobs.append({
                        "title": job.get("position", "Unknown Position"),
                        "skills": job.get("tags", [])
                    })
            return jobs[:10]  # limit to top 10
    except Exception as e:
        st.error("❌ Failed to fetch live jobs.")
        return []

    return []

# Combine sample and live jobs
sample_jobs = [
    {"title": "Data Analyst", "skills": ["Python", "SQL", "Excel"]},
    {"title": "Software Engineer", "skills": ["Python", "React", "AWS"]},
    {"title": "Marketing Manager", "skills": ["SEO", "Google Analytics", "Content Creation"]},
    {"title": "Project Coordinator", "skills": ["Organization", "Scheduling", "Communication"]}
]
live_jobs = fetch_remote_jobs()
all_jobs = sample_jobs + live_jobs

if st.button("🔍 Find Matching Jobs"):
    if not resume_text.strip():
        st.warning("⚠️ Please upload a resume file.")
    else:
        with st.spinner("🔎 Analyzing your resume..."):
            response = openai.ChatCompletion.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": "You are a helpful assistant that extracts skills from resumes."},
                    {"role": "user", "content": f"Extract a list of key skills and job-related terms from this resume:\n\n{resume_text}"}
                ]
            )
            extracted = response['choices'][0]['message']['content']
            skills = [s.strip().lower() for s in extracted.split(',') if len(s.strip()) > 0]

        st.subheader("📋 Extracted Skills")
        st.write(skills)

        st.subheader("💼 Matching Jobs")
        matches = []
        for job in all_jobs:
            job_skills = [s.lower() for s in job.get("skills", [])]
            matched_skills = set(skills) & set(job_skills)
            if matched_skills:
                matches.append((job["title"], matched_skills))

        if matches:
            for title, matched in matches:
                st.success(f"✅ **{title}** — matched skills: {', '.join(matched)}")

            selected_title = st.selectbox("📌 Pick a job to generate a cover letter for:", [m[0] for m in matches])
            if st.button("✍️ Generate Cover Letter"):
                with st.spinner("✒️ Writing your cover letter..."):
                    cover_prompt = f"""
                    Based on this resume:
                    {resume_text}

                    Write a professional, friendly, tailored cover letter for a job titled: {selected_title}.
                    """
                    cover_response = openai.ChatCompletion.create(
                        model="gpt-4",
                        messages=[{"role": "user", "content": cover_prompt}]
                    )
                    st.subheader("📄 Cover Letter")
                    st.write(cover_response['choices'][0]['message']['content'])
        else:
            st.info("ℹ️ No strong matches found. Try refining your resume or skill list.")
