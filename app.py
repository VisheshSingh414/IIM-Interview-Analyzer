import streamlit as st
import pdfplumber
from google import genai
import requests

client = genai.Client(api_key=st.secrets["GEMINI_API_KEY"])

st.title("AI IIM Interview Readiness Analyzer")

uploaded_file = st.file_uploader(
    "Upload CAT profile",
    type=["pdf", "txt"]
)

user_question = st.text_input("Ask a question about your IIM chances")

recipient_email = st.text_input("Enter recipient email")

# EVERYTHING BELOW must be inside uploaded_file block
if uploaded_file:

    text = ""

    if uploaded_file.type == "application/pdf":
        with pdfplumber.open(uploaded_file) as pdf:
            for page in pdf.pages:
                text += page.extract_text()

    elif uploaded_file.type == "text/plain":
        text = uploaded_file.read().decode("utf-8")

    st.subheader("Extracted Document Text")
    st.write(text)
    if user_question:

        prompt = f"""
        Extract structured CAT profile data.

        Document:
        {text}

        Question:
        {user_question}

        Return JSON only.
        """

        with st.spinner("Analyzing CAT profile with AI..."):

            response = client.models.generate_content(
                model="gemini-2.5-flash",
                contents=prompt
            )

        st.subheader("Structured Data")
        st.write(response.text)
        # Send email via n8n webhook
        if recipient_email:

            webhook_url = "http://localhost:5678/webhook-test/iim-analysis"

            payload = {
                "email": recipient_email,
                "analysis": response.text
            }

            r = requests.post(webhook_url, json=payload)

            if r.status_code == 200:
                st.success("Email Sent Successfully")
            else:
                st.error("Failed to send email")