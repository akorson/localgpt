import os
import googleapiclient.discovery
from google.oauth2 import service_account
from bing import Bing
from github import Github

def google_search(query):
    api_key = os.environ["GOOGLE_API_KEY"]
    cse_id = os.environ["GOOGLE_CSE_ID"]
    credentials = service_account.Credentials.from_service_account_info(api_key)
    service = googleapiclient.discovery.build("customsearch", "v1", credentials=credentials)
    result = service.cse().list(q=query, cx=cse_id).execute()
    return result["items"]

def bing_search(query):
    api_key = os.environ["BING_API_KEY"]
    bing = Bing(api_key)
    results = bing.search(query)
    return results["webPages"]["value"]

def github_search(query):
    access_token = os.environ["GITHUB_ACCESS_TOKEN"]
    github = Github(access_token)
    results = github.search_repositories(query)
    return results
