import os

import openai
import streamlit as st
from dotenv import load_dotenv
from mongoengine import connect, disconnect

from chatgpt_api import (
    delete_file,
    get_response,
    read_file,
    recall,
    remember,
    save_file,
)
from search_engines import bing_search, github_search, google_search

load_dotenv()
MONGODB_URI = os.environ["MONGODB_URI"]
db = connect("chatgpt", host=MONGODB_URI)

st.set_page_config(page_title="ChatGPT App", page_icon=":speech_balloon:")
st.title("ChatGPT App")

short_term_memory = ""
model = st.sidebar.selectbox("Select OpenAI model",
                             ("gpt-3.5-turbo", "davinci-codex"))
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
            search_results = {
                "google": google_search(query),
                "bing": bing_search(query),
                "github": github_search(query),
            }
            for engine, results in search_results.items():
                st.write(f"{engine.capitalize()} Results:")
                [
                    st.write(f"- {result['title']} ({result['url']})")
                    for result in results
                ]
        else:
            if model == "gpt-3.5-turbo":
                prompt = [
                    {
                        "role": "system",
                        "content": "You are a helpful assistant."
                    },
                    {
                        "role": "user",
                        "content": user_input
                    },
                ]
                chatgpt_response = (openai.Completion.create(
                    engine="text-davinci-002",
                    prompt=prompt,
                    max_tokens=1024,
                    n=1,
                    stop=None,
                    temperature=0.1,
                    presence_penalty=0.5,
                    frequency_penalty=0.5,
                    user=None,
                    model="text-davinci-002",
                    chat_log=None,
                    examples=None,
                ).choices[0].text.strip())
            else:
                chatgpt_response = get_response(user_input,
                                                short_term_memory,
                                                model=model)
            st.write("User:", user_input, "\nChatGPT:", chatgpt_response)
            remember(user_input, chatgpt_response)
            short_term_memory = add_short_term_memory(short_term_memory,
                                                      user_input,
                                                      chatgpt_response)

            save_file("response.txt", chatgpt_response)

            content = read_file("response.txt")
            st.write("Content from file:", content)

            delete_file("response.txt")
