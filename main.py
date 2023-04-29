import os

import streamlit as st
from dotenv import load_dotenv
from mongoengine import connect as mongoengine_connect
from mongoengine import disconnect as mongoengine_disconnect
from pymongo import MongoClient
from pymongo.errors import PyMongoError
from search_engines import bing_search, github_search, google_search

from chatgpt_api import (
    delete_file,
    get_response,
    read_file,
    recall,
    recall_mongoengine,
    remember,
    remember_mongoengine,
    save_file,
)

load_dotenv()

# Connect to MongoDB using pymongo
try:
    client = MongoClient(os.environ["MONGO_URI"])
    db = client[os.environ["MONGO_DB_NAME"]]
except PyMongoError:
    st.error(
        "Error connecting to the database using pymongo. Please check the connection details."
    )

# Connect to MongoDB using mongoengine
try:
    mongoengine_connect(db=os.environ["MONGO_DB_NAME"],
                        host=os.environ["MONGO_URI"],
                        alias="default")
except PyMongoError:
    st.error(
        "Error connecting to the database using mongoengine. Please check the connection details."
    )

st.set_page_config(page_title="ChatGPT App", page_icon=":speech_balloon:")
st.title("ChatGPT App")

short_term_memory = ""
model = st.sidebar.selectbox("Select OpenAI model",
                             ("text-davinci-002", "text-davinci-003"))
recall_conversations = st.sidebar.checkbox("Recall previous conversations")

if recall_conversations:
    st.sidebar.write("Previous conversations:")
    for convo in recall():
        st.sidebar.write(
            f"User: {convo['prompt']} \nChatGPT: {convo['response']}")
    for convo in recall_mongoengine():
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
            chatgpt_response = get_response(user_input,
                                            short_term_memory,
                                            model=model)
            st.write("User:", user_input, "\nChatGPT:", chatgpt_response)
            remember(user_input, chatgpt_response)
            remember_mongoengine(user_input, chatgpt_response)
            short_term_memory = add_short_term_memory(short_term_memory,
                                                      user_input,
                                                      chatgpt_response)
            # Save the response to a file
            save_file("response.txt", chatgpt_response)

            # Read the content of the saved file
            content = read_file("response.txt")
            st.write("Content from file:", content)

            # Delete the saved file
            delete_file("response.txt")

# Disconnect from the MongoDB database
mongoengine_disconnect(alias="default")
