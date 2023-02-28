import argparse
import numpy as np
import os
import pandas as pd
import requests
import time

from datetime import datetime

parser = argparse.ArgumentParser()
parser.add_argument("filename")
parser.add_argument("keyword")
parser.add_argument("--tokens", required=True, nargs="+")
parser.add_argument("-o", default="results.csv")

args = parser.parse_args()

# Function to search for a string in a repository
def search_repo(name, token):
    api_url = f"https://api.github.com/search/code?q=repo:{name}+{args.keyword}"
    response = requests.get(
        api_url,
        headers={"Authorization": f"Bearer {token}", "Accept": "application/vnd.github.v3+json"}
    )
    if response.status_code == 422:
        return False
    if response.status_code != 200:
        response.raise_for_status()
    data = response.json()
    return data["total_count"] > 0


def check_rate(token):
    api_url = f"https://api.github.com/rate_limit"
    response = requests.get(
        api_url,
        headers={"Authorization": f"Bearer {token}", "Accept": "application/vnd.github.v3+json"}
    )
    if response.status_code != 200:
        response.raise_for_status()
    data = response.json()
    return data["resources"]["search"]


def main(token):
    COLUMNS = ["name", "url", "created_at", "updated_at", "stars"]

    orig = pd.read_csv(args.filename, index_col="name")

    # For keeping track of the progress
    if os.path.exists("done.csv"):
        done = pd.read_csv("done.csv", index_col="name")
    else:
        done = pd.DataFrame(columns=COLUMNS)
        done.index.name = "name"

    # For storing the results
    if os.path.exists(args.o):
        results = pd.read_csv(args.o, index_col="name")
    else:
        results = pd.DataFrame(columns=COLUMNS)
        results.index.name = "name"

    df = orig.loc[orig.index.difference(done.index)]

    finished = True
    # Search for the string in each repository
    for repo in df.index:
        print(f'\t{repo}...', end='')
        try:
            found = search_repo(repo, token)
            if found:
                results = results.append(df.loc[repo])
            done = done.append(df.loc[repo])
            print(found)
        except Exception as e:
            print(e)
            finished = False
            break
    done.to_csv("done.csv")
    results.to_csv(args.o)

    return finished


next_token_index = 0
while True:
    print(f"Using token index: {next_token_index}")
    token = args.tokens[next_token_index]
    if main(token):
        break

    deadlines = []
    remaining = []
    for i, tok in enumerate(args.tokens):
        rate = check_rate(tok)
        deadlines.append(rate["reset"])
        remaining.append(rate["remaining"])

    max_remaining = np.max(remaining)
    if max_remaining > 0:
        next_token_index = np.argmax(remaining)
        next_deadline = 0
    else:    
        next_token_index = np.argmin(deadlines)
        next_deadline = np.min(deadlines)

    print(
        f"Next token index: {next_token_index}. Remaining allowance: {remaining[next_token_index]}. "
        f"Next deadline: {datetime.fromtimestamp(next_deadline).strftime('%Y-%m-%d %H:%M:%S')}"
    )

    sleep_for = next_deadline - round(time.time())
    if sleep_for > 0:
        for i in range(sleep_for):
            print(".", end='', flush=True)
            time.sleep(1)
        print()
