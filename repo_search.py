import argparse
import requests
import csv

parser = argparse.ArgumentParser()
parser.add_argument("token", help="Github token for code search")
parser.add_argument("query", default="stars:>1000 language:typescript", help="code search query")
parser.add_argument("--output", "-o", help="path of the output file", default="github_repos.csv")

args = parser.parse_args()

# GitHub API endpoint for searching code
SEARCH_CODE_API = "https://api.github.com/search/repositories"

# Request headers with access token
headers = {"Authorization": f"Token {args.token}"}

results = []

for i in range(10):
    # Parameters for search query
    params = {
        "q": args.query,
        "sort": "stars",
        "per_page": 100,
        "page": i + 1
    }

    print(f"Page {i+1}: ", end='')

    # Send GET request to GitHub API
    response = requests.get(SEARCH_CODE_API, headers=headers, params=params)

    # Raise exception if the request was not successful
    if response.status_code != 200:
        break

    items = response.json()["items"]
    print(f"found {len(items)} items")

    # Extract the results from the response JSON
    results.extend(items)

# Write the results to a CSV file
with open(args.output, "w", newline="", encoding="utf-8") as csvfile:
    writer = csv.writer(csvfile)
    writer.writerow(["name", "url", "created_at", "updated_at", "stars"])
    for result in results:
        name = result["full_name"]
        url = result["html_url"]
        created_at = result["created_at"]
        updated_at = result["updated_at"]
        stars = result["stargazers_count"]
        writer.writerow([name, url, created_at, updated_at, stars])
