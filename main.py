import streamlit as st
from dotenv import load_dotenv
from models import ChatGPT, CodexGPT, InstructGPT
from mongoengine import connect, disconnect

from api_keys import (
    get_bing_key,
    get_github_token,
    get_google_cse_cx,
    get_google_cse_key,
    get_mongodb_uri,
)
from chatgpt_api import delete_file, read_file, recall, remember, save_file
from search_engines import bing_search, github_search, google_search

load_dotenv()
MONGODB_URI = get_mongodb_uri()
db = connect("chatgpt", host=MONGODB_URI)

st.set_page_config(page_title="ChatGPT App", page_icon=":speech_balloon:")

CSS = """
body {
    background: linear-gradient(to bottom right, #1f4037, #99f2c8);
}
"""

st.markdown(f"<style>{CSS}</style>", unsafe_allow_html=True)

st.title("ChatGPT App")

models = {
    "ChatGPT": ChatGPT(),
    "CodexGPT": CodexGPT(),
    "InstructGPT": InstructGPT()
}
model_name = st.sidebar.selectbox("Select OpenAI model", list(models.keys()))
model = models[model_name]
recall_conversations = st.sidebar.checkbox("Recall previous conversations")

if recall_conversations:
    st.sidebar.write("Previous conversations:")
    for convo in recall():
        st.sidebar.write(
            f"User: {convo['prompt']} \nChatGPT: {convo['response']}")


def add_short_term_memory(memory, input_msg, output_msg):
    return f"{memory}\nUser: {input_msg}\nChatGPT: {output_msg}"


with st.form("chat_form"):
    user_input = st.text_input("Type your message:")
    send_button = st.form_submit_button("Send")

    if send_button:
        if "search" in user_input.lower():
            query = user_input.replace("search", "").strip()
            google_cse_key = get_google_cse_key()
            google_cse_cx = get_google_cse_cx()
            bing_key = get_bing_key()
            github_token = get_github_token()

            search_results = {
                "google": google_search(query, google_cse_key, google_cse_cx),
                "bing": bing_search(query, bing_key),
                "github": github_search(query, github_token),
            }
            for engine, results in search_results.items():
                st.write(f"{engine.capitalize()} Results:")
                [
                    st.write(f"- {result['title']} ({result['url']})")
                    for result in results
                ]
        else:
            chatgpt_response = model.get_response(user_input,
                                                  short_term_memory)
            st.write("User:", user_input, "\nChatGPT:", chatgpt_response)
            remember(user_input, chatgpt_response)
            short_term_memory = add_short_term_memory(short_term_memory,
                                                      user_input,
                                                      chatgpt_response)

            save_file("response.txt", chatgpt_response)

            content = read_file("response.txt")
            st.write("Content from file:", content)

            delete_file("response.txt")
