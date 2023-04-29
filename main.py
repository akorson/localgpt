import os

import streamlit as st
from dotenv import load_dotenv
from search_engines import bing_search, github_search, google_search

from chatgpt_api import get_response, recall, remember

load_dotenv()

# Add main styling and a good-looking color palette
st.markdown(
    """
<style>
    body {
        color: #4f4f4f;
        background-color: #f5f0e1;
    }
    .sidebar .sidebar-content {
        background-color: #f5f0e1;
    }
    h1 {
        color: #375a7f;
    }
    .reportview-container .main .block-container {
        background-color: #eae7dc;
        padding: 2rem;
        border-radius: 5px;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
    }
</style>
""",
    unsafe_allow_html=True,
)

st.title("ChatGPT App")

short_term_memory = ""
model = st.sidebar.selectbox("Select OpenAI model",
                             ("text-davinci-002", "text-davinci-003"))

recall_conversations = st.sidebar.checkbox("Recall previous conversations")

if recall_conversations:
    conversations = recall()
    st.sidebar.write("Previous conversations:")
    for convo in conversations:
        st.sidebar.write(
            f"User: {convo['prompt']} \nChatGPT: {convo['response']}")


def add_short_term_memory(memory, input_msg, output_msg):
    return f"{memory}\nUser: {input_msg}\nChatGPT: {output_msg}"


def display_result(engine, result):
    st.write(f"- {result['title']} ({result['url']})")


with st.form("chat_form"):
    user_input = st.text_input("Type your message:")
    send_button = st.form_submit_button("Send")

    if send_button:
        if "search" in user_input.lower():
            query = user_input.replace("search", "").strip()
            search_results = {
                "google": google_search(query),
                "bing": bing_search(query),
                "github": github_search(query),
            }
            for engine, results in search_results.items():
                st.write(f"{engine.capitalize()} Results:")
                for result in results:
                    display_result(engine, result)
        else:
            chatgpt_response = get_response(user_input,
                                            short_term_memory,
                                            model=model)
            st.write("User:", user_input)
            st.write("ChatGPT:", chatgpt_response)
            remember(user_input, chatgpt_response)
            short_term_memory = add_short_term_memory(short_term_memory,
                                                      user_input,
                                                      chatgpt_response)
