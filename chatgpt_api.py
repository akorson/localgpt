import os
from dotenv import load_dotenv
import openai
import pymongo

load_dotenv()

openai.api_key = os.environ["OPENAI_API_KEY"]
MONGO_URI = os.environ["MONGO_URI"]
client = pymongo.MongoClient(MONGO_URI)
db = client["chatgpt"]
memory_collection = db["memory"]

def add_short_term_memory(prompt, response):
    return f"{prompt}\n{response}\n"

def add_long_term_memory(prompt, response):
    memory = {"prompt": prompt, "response": response}
    memory_collection.insert_one(memory)

def get_response(prompt, short_term_memory="", model="text-davinci-002", max_tokens=150, temperature=0.7):
    model_cfg = {
        "text-davinci-002": {"temperature": 0.6, "max_tokens": 100},
        "text-davinci-003": {"temperature": 0.8, "max_tokens": 150},
    }
    if model in model_cfg:
        temperature = model_cfg[model]["temperature"]
        max_tokens = model_cfg[model]["max_tokens"]

    response = openai.Completion.create(
        engine=model,
        prompt=add_short_term_memory(short_term_memory, prompt),
        max_tokens=max_tokens,
        n=1,
        stop=None,
        temperature=temperature,
    )

    return response.choices[0].text.strip()

def remember(prompt, response):
    add_long_term_memory(prompt, response)
