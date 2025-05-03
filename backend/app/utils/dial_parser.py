# utils/llm_parser.py

import os
import requests
from dotenv import load_dotenv

load_dotenv()

DIAL_API_KEY = os.getenv("DIALAPI")
DIAL_DEPLOYMENT_NAME = os.getenv("DIAL_DEPLOYMENT_NAME", "gpt-4")  # default to gpt-4
DIAL_API_VERSION = os.getenv("DIAL_API_VERSION", "2023-12-01-preview")

#getting vector embeddings
import requests
import os


async def get_text_embedding(text: str) -> list[float]:
    """Send any text to DIAL LLM Embeddings endpoint and get back vector embedding."""

    url = f"https://ai-proxy.lab.epam.com/openai/deployments/{DIAL_DEPLOYMENT_NAME}/embeddings?api-version={DIAL_API_VERSION}"
    headers = {
        "Content-Type": "application/json",
        "Api-Key": DIAL_API_KEY
    }
    payload = {
        "input": text
    }

    response = requests.post(url, headers=headers, json=payload)

    if response.status_code == 200:
        embedding_vector = response.json()["data"][0]["embedding"]
        return embedding_vector
    else:
        raise Exception(f"DIAL embedding generation failed: {response.text}")



#extracted text - json object
async def parse_resume_with_dial(resume_text: str) -> dict:
    """Send resume text to DIAL LLM and get structured JSON."""

    url = f"https://ai-proxy.lab.epam.com/openai/deployments/{DIAL_DEPLOYMENT_NAME}/chat/completions?api-version={DIAL_API_VERSION}"
    headers = {
        "Content-Type": "application/json",
        "Api-Key": DIAL_API_KEY
    }

    prompt = f"""
You are a professional resume parser.

Given the resume text below, extract the following fields as JSON:
- Name
- Email
- Phone Number
- Skills (list)
- Work Experience (list)
- Education (list)

Resume Text:
\"\"\"
{resume_text}
\"\"\"

Respond with only valid JSON, no extra text.
"""

    payload = {
        "messages": [
            {"role": "user", "content": prompt}
        ],
        "temperature": 0.2,
        "max_tokens": 1200
    }

    response = requests.post(url, headers=headers, json=payload)

    if response.status_code == 200:
        parsed_json = response.json()["choices"][0]["message"]["content"]
        return parsed_json
    else:
        raise Exception(f"DIAL parsing failed: {response.text}")

#job summary
async def generate_job_summary(job_description: str) -> str:
    """Send job description to DIAL LLM and get a summarized job text."""

    url = f"https://ai-proxy.lab.epam.com/openai/deployments/{DIAL_DEPLOYMENT_NAME}/chat/completions?api-version={DIAL_API_VERSION}"
    headers = {
        "Content-Type": "application/json",
        "Api-Key": DIAL_API_KEY
    }

    prompt = f"""
You are a professional job description summarizer.

Given the job description below, generate a short, attractive job summary (max 100 words) highlighting key responsibilities, skills, and role expectations.

Job Description:
\"\"\"
{job_description}
\"\"\"

Respond with only the summary text. No extra formatting, no JSON.
"""

    payload = {
        "messages": [
            {"role": "user", "content": prompt}
        ],
        "temperature": 0.3,
        "max_tokens": 300
    }

    response = requests.post(url, headers=headers, json=payload)

    if response.status_code == 200:
        summary_text = response.json()["choices"][0]["message"]["content"].strip()
        return summary_text
    else:
        raise Exception(f"DIAL summary generation failed: {response.text}")
