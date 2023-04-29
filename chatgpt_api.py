import os
import openai
import mongoengine
from dotenv import load_dotenv
from mongoengine import Document, StringField, connect

load_dotenv()

# set OpenAI API key
openai.api_key = os.environ["OPENAI_API_KEY"]

# connect to MongoDB
MONGO_URI = os.environ["MONGO_URI"]
connect(host=MONGO_URI)

# define memory classes
class ShortTermMemory(Document):
    prompt = StringField(required=True)
    response = StringField(required=True)


class LongTermMemory(Document):
    prompt = StringField(required=True)
    response = StringField(required=True)

# file handling functions
def save_file(file_name, content):
    with open(file_name, "w") as f:
        f.write(content)

def read_file(file_name):
    with open(file_name, "r") as f:
        return f.read()

def delete_file(file_name):
    if os.path.isfile(file_name):
        os.remove(file_name)
    else:
        print(f"Error: {file_name} not found")

# add short-term memory to the prompt
def add_short_term_memory(prompt, response):
    stm = ShortTermMemory(prompt=prompt, response=response)
    stm.save()
    return f"{prompt}\n{response}\n"

# insert a single document into the MongoDB collection
def add_long_term_memory(prompt, response):
    ltm = LongTermMemory(prompt=prompt, response=response)
    ltm.save()

# recall short-term memory
def recall_short_term_memory(prompt):
    stm = ShortTermMemory.objects(prompt=prompt).first()
    return stm.response if stm else None

# recall long-term memory
def recall_long_term_memory(prompt):
    ltm = LongTermMemory.objects(prompt=prompt).first()
    return ltm.response if ltm else None

# get a response from OpenAI API
def get_response(
    prompt,
    short_term_memory="",
    model="text-davinci-002",
    max_tokens=150,
    temperature=0.7,
):
    model_config = {
        "text-davinci-002": {
            "temperature": 0.6,
            "max_tokens": 100
        },
        "text-davinci-003": {
            "temperature": 0.8,
            "max_tokens": 150
        },
    }
    if model in model_config:
        temperature = model_config[model]["temperature"]
        max_tokens = model_config[model]["max_tokens"]

    response = openai.Completion.create(
        engine=model,
        prompt=add_short_term_memory(short_term_memory, prompt),
        max_tokens=max_tokens,
        n=1,
        stop=None,
        temperature=temperature,
    )

    return response.choices[0].text.strip()

# insert a long-term memory into the MongoDB collection
def remember(prompt, response):
    add_long_term_memory(prompt, response)
