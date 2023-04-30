import openai
import os
from dotenv import load_dotenv
from mongoengine import Document, StringField

load_dotenv()

openai.api_key = os.environ["OPENAI_API_KEY"]

# Define the ChatHistory model using mongoengine
class ChatHistory(Document):
    prompt = StringField(required=True)
    response = StringField(required=True)

# Get response from OpenAI API
def get_response(prompt, context, model="code-x-002", turbo=False):
    if turbo:
        model = "3.5-turbo"

    completions = openai.Completion.create(
        engine=model,
        prompt=f"{context}\nUser: {prompt}\nChatGPT:",
        max_tokens=100,
        n=1,
        stop=None,
        temperature=0,
    )

    message = completions.choices[0].text.strip()
    return message

# Save the chat history
def remember(prompt, response):
    chat_history = ChatHistory(prompt=prompt, response=response)
    chat_history.save()

# Recall the chat history using mongoengine
def recall():
    return ChatHistory.objects.all()

# Save content to a file
def save_file(file_name, content):
    with open(file_name, "w") as f:
        f.write(content)

# Read content from a file
def read_file(file_name):
    with open(file_name, "r") as f:
        content = f.read()
    return content

# Delete a file
def delete_file(file_name):
    if os.path.exists(file_name):
        os.remove(file_name)
