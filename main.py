import os
import streamlit as st
from dotenv import load_dotenv
from mongoengine import connect, disconnect
from search_engines import bing_search, github_search, google_search
import openai

from chatgpt_api import get_response, recall, remember, save_file, read_file, delete_file

load_dotenv()

# Get Environment Variables
MONGODB_URI = os.getenv("MONGODB_URI")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
GOOGLE_CSE_ID = os.getenv("GOOGLE_CSE_ID")
BING_API_KEY = os.getenv("BING_API_KEY")
GITHUB_ACCESS_TOKEN = os.getenv("GITHUB_ACCESS_TOKEN")

# Set API Keys
openai.api_key = OPENAI_API_KEY

# Initialize DB
db = connect("chatgpt", host=MONGODB_URI)

# Configure Streamlit
st.set_page_config(page_title="ChatGPT App", page_icon=":speech_balloon:")
st.title("ChatGPT App")

# Set Theme
st.markdown(
    """
    <style>
        body {
            font-family: 'Montserrat', sans-serif;
            background: linear-gradient(to bottom right, #96F550, #0D3B66, #6CCFF6, #E39774, #45CB85);
            color: #ffffff;
        }
        .sidebar .sidebar-content {
            background-color: #283040;
        }
        h1, h2, h3 {
            color: #e5e5e5;
        }
        .css-1vu1vkj {
            background-color: #210cae;
            border-color: #210cae;
        }
        .primary-color {
            color: #96F550;
        }
        .secondary-color {
            color: #0D3B66;
        }
        .accent-color {
            color: #45CB85;
        }
    </style>
    """,
    unsafe_allow_html=True,
)

short_term_memory = ""
model = st.sidebar.selectbox("Select OpenAI model", ("gpt-3.5-turbo", "davinci-codex"))
recall_conversations = st.sidebar.checkbox("Recall previous conversations")

if recall_conversations:
    st.sidebar.write("Previous conversations:")
    for convo in recall():
        st.sidebar.write(f"User: {convo['prompt']} \nChatGPT: {convo['response']}")

def add_short_term_memory(memory, input_msg, output_msg):
    return f"{memory}\nUser: {input_msg}\nChatGPT: {output_msg}"

with st.form("chat_form"):
    user_input = st.text_input("Type your message:")
    send_button = st.form_submit_button("Send")

    if send_button:
        if "search" in user_input.lower():
            query = user_input.replace("search", "").strip()
            search_results = {
                "google": google_search(query, GOOGLE_API_KEY, GOOGLE_CSE_ID), 
                "bing": bing_search(query, BING_API_KEY), 
                "github": github_search(query, GITHUB_ACCESS_TOKEN)
            }
            for engine, results in search_results.items():
                st.write(f"{engine.capitalize()} Results:")
                [st.write(f"- {result['title']} ({result['url']})") for result in results]
        else:
            chatgpt_response = ""
            if model == "gpt-3.5-turbo":
                                prompt = [
                    {"role": "system", "content": "You are a helpful assistant."},
                    {"role": "user", "content": user_input}
                ]
                chatgpt_response = openai.Completion.create(
                    engine=model,
                    prompt=prompt,
                    max_tokens=1024,
                    temperature=0.1,
                    n=1,
                    stop=None,
                    presence_penalty=0.5,
                    frequency_penalty=0.5
                ).choices[0].text.strip()
            else:
                chatgpt_response = get_response(user_input, short_term_memory, model=model)
            st.write("User:", user_input, "\nChatGPT:", chatgpt_response)
            remember(user_input, chatgpt_response)
            short_term_memory = add_short_term_memory(short_term_memory, user_input, chatgpt_response)

            save_file("response.txt", chatgpt_response)

            content = read_file("response.txt")
            st.write("Content from file:", content)

            delete_file("response.txt")

