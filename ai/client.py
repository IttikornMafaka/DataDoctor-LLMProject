import os
from dotenv import load_dotenv
from huggingface_hub import InferenceClient 

load_dotenv(override=True)
MODEL_NAME = "Qwen/Qwen3-8B"
HF_TOKEN = os.getenv("HF_TOKEN")

client = InferenceClient(api_key=os.getenv("HF_TOKEN"),provider="auto")

def chat(prompt:str) -> str :
    response = client.chat.completions.create(model=MODEL_NAME,messages=[{"role":"user","content":prompt}],temperature=0.3,max_tokens=1024)
    return response.choices[0].message.content
    