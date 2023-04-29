import os
from dotenv import load_dotenv
import streamlit as st
import requests
from chatgpt_api import get_response, remember, recall
import googleapiclient.discovery
from google.oauth2 import service_account
from bing_search_api_v7 import BingSearch
from github import Github
import json

load_dotenv()

# Google Custom Search API
def google_search(query):
    api_key = os.environ["GOOGLE_API_KEY"]
    cse_id = os.environ["GOOGLE_CSE_ID"]
    service = googleapiclient.discovery.build("customsearch", "v1", developerKey=api_key)
    result = service.cse().list(q=query, cx=cse_id).execute()
    return result["items"]

# Bing Search API
def bing_search(query):
    api_key = os.environ["BING_API_KEY"]
    bing = BingSearch(api_key)
    results = bing.search(query)
    return results["webPages"]["value"]

# Github Search API
def github_search(query):
    access_token = os.environ["GITHUB_ACCESS_TOKEN"]
    github = Github(access_token)
    results = github.search_repositories(query)
    return results

# Add short term memory
def add_short_term_memory(short_term_memory, user_input, chatgpt_response):
    return f'{short_term_memory} User: {user_input} ChatGPT: {chatgpt_response}'

def search(query): ...
st.title("ChatGPT App")
short_term_memory = ""
model = st.sidebar.selectbox("Select OpenAI model", ("text-davinci-002", "text-davinci-003"))
recall_conversations = st.sidebar.checkbox("Recall previous conversations")

while True:
    user_input = st.text_input("Type your message:")
