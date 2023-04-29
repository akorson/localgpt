import json
import os

import googleapiclient.discovery
import requests
import streamlit as st
from bing_search_api_v7 import BingSearch
from dotenv import load_dotenv
from github import Github
from google.oauth2 import service_account

from chatgpt_api import get_response, recall, remember, save_file, read_file, delete_file

load_dotenv()

# Define search engines
search_engines = {
    "google": {
        "api_key": os.environ["GOOGLE_API_KEY"],
        "cse_id": os.environ["GOOGLE_CSE_ID"],
        "function": google_search,
    },
    "bing": {
        "api_key": os.environ["BING_API_KEY"],
        "function": bing_search,
    },
    "github": {
        "access_token": os.environ["GITHUB_ACCESS_TOKEN"],
        "function": github_search,
    },
}

# Google Custom Search API
def google_search(query):
    service = googleapiclient.discovery.build(
        "customsearch", "v1", developerKey=search_engines["google"]["api_key"])
    result = (service.cse().list(
        q=query, cx=search_engines["google"]["cse_id"]).execute())
    return result["items"]

# Bing Search API
def bing_search(query):
    bing = BingSearch(search_engines["bing"]["api_key"])
    results = bing.search(query)
    return results["webPages"]["value"]

# Github Search API
def github_search(query):
    github = Github(search_engines["github"]["access_token"])
    results = github.search_repositories(query)
    return results

# Add short term memory
def add_short_term_memory(short_term_memory, user_input, chatgpt_response):
    return f"{short_term_memory}\nUser: {user_input}\nChatGPT: {chatgpt_response}"

# Function to handle user input
def handle_input(short_term_memory):
    user_input = st.text_input("Type your message:")
    if st.button("Send"):
        if "search" in user_input.lower():
            query = user_input.replace("search", "").strip()
            for engine, settings in search_engines.items():
                if engine in user_input.lower():
                    results = settings["function"](query)
                    st.write(f"{engine.capitalize()} Results:")
                    for result in results:
                        st.write(f"- {result['title']} ({result['url']})")
                    return short_term_memory
            st.write("Invalid search engine")
            return short_term_memory
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
            # Save the response to a file
            save_file("response.txt", chatgpt_response)

            # Read the content of the saved file
            content = read_file("response.txt")
            st.write("Content from file:", content)

            # Delete the saved file
            delete_file("response.txt")

            return short_term_memory
