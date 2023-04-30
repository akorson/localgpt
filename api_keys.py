import os


def get_mongodb_uri():
    return os.environ.get("MONGODB_URI")


def get_google_cse_key():
    return os.environ.get("GOOGLE_CSE_KEY")


def get_google_cse_cx():
    return os.environ.get("GOOGLE_CSE_CX")


def get_bing_key():
    return os.environ.get("BING_KEY")


def get_github_token():
    return os.environ.get("GITHUB_TOKEN")
