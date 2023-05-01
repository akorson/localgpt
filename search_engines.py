import os

import googleapiclient.discovery
import requests
from github import Github
from google.oauth2 import service_account


def google_search(query):
    api_key = os.environ["GOOGLE_API_KEY"]
    cse_id = os.environ["GOOGLE_CSE_ID"]
    credentials = service_account.Credentials.from_service_account_info(
        api_key)
    service = googleapiclient.discovery.build("customsearch",
                                              "v1",
                                              credentials=credentials)
    result = service.cse().list(q=query, cx=cse_id).execute()
    return result["items"]


def bing_search(query):
    api_key = os.environ["BING_API_KEY"]
    url = "https://api.bing.microsoft.com/v7.0/search"
    headers = {"Ocp-Apim-Subscription-Key": api_key}
    params = {"q": query}
    response = requests.get(url, headers=headers, params=params)
    results = response.json()
    return results["webPages"]["value"]


def github_search(query):
    access_token = os.environ["GITHUB_ACCESS_TOKEN"]
    github = Github(access_token)
    results = github.search_repositories(query)
    return results


def search_all(query):
    google_results = google_search(query)
    bing_results = bing_search(query)
    github_results = github_search(query)

    return {
        "google_results": google_results,
        "bing_results": bing_results,
        "github_results": github_results,
    }
