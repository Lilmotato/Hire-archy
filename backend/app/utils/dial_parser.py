import json
import os
import requests
from dotenv import load_dotenv


load_dotenv()

DIAL_API_KEY = os.getenv("DIALAPI")
DIAL_DEPLOYMENT_NAME = "text-embedding-ada-002"
DIAL_API_VERSION = os.getenv("DIAL_API_VERSION", "2023-12-01-preview")


def get_text_embedding(text: str) -> list[float]:
    """
    Send text to DIAL embedding endpoint and return the embedding vector.
    """
    url = f"https://ai-proxy.lab.epam.com/openai/deployments/{DIAL_DEPLOYMENT_NAME}/embeddings?api-version={DIAL_API_VERSION}"
    headers = {
        "Content-Type": "application/json",
        "Api-Key": DIAL_API_KEY
    }
    payload = {"input": text}

    print(f"🔍 Sending request to: {url}")
    print(f"📦 Payload: {payload}")

    response = requests.post(url, headers=headers, json=payload)
    print(f"📡 Status code: {response.status_code}")

    try:
        response.raise_for_status()
        data = response.json()
        embedding = data["data"][0]["embedding"]
        print(f"Received embedding of length {len(embedding)}")
        print(f"First 10 values: {embedding[:10]}") #testing 
        return embedding
    except Exception as e:
        print("Error parsing response:")
        print(response.text)
        raise RuntimeError("Failed to get text embedding") from e


async def parse_resume_with_dial(resume_text: str) -> dict:
    """
    Send resume text to DIAL LLM and get structured Python dict (parsed resume).
    """

    url = f"https://ai-proxy.lab.epam.com/openai/deployments/gpt-4/chat/completions?api-version={DIAL_API_VERSION}"
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
\"\"\"{resume_text}\"\"\"

Respond with only valid JSON. Do not include Markdown formatting or explanation.
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
        content = response.json()["choices"][0]["message"]["content"].strip()

        try:
            parsed = json.loads(content)  
            if not isinstance(parsed, dict):
                raise ValueError("Parsed resume is not a dictionary.")
            return parsed
        except json.JSONDecodeError as e:
            raise ValueError(f"❌ Invalid JSON from DIAL: {e}\n---\n{content}")

    else:
        raise Exception(f"❌ DIAL parsing failed: {response.text}")
