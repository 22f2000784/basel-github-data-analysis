import requests
import csv
import os
import pandas as pd

# Set up GitHub API access
GITHUB_TOKEN = os.getenv('GITHUB_TOKEN')
headers = {
    "Authorization": f"token {GITHUB_TOKEN}",
    "Accept": "application/vnd.github.v3+json"
}

# Function to convert booleans to 'true', 'false', or empty string for null
def bool_to_str(value):
    if value is None:
        return ""  # Empty string for null
    return "true" if value else "false"  # Ensure lowercase

# Function to fetch up to 500 most recently pushed repositories for a given user
def get_repositories_for_user(username):
    repos = []
    params = {
        "per_page": 100,
        "page": 1,
        "sort": "pushed",  # Sort by push activity
        "direction": "desc"  # Descending order to get most recently pushed
    }
    
    while len(repos) < 500:
        response = requests.get(f"https://api.github.com/users/{username}/repos", headers=headers, params=params)
        data = response.json()
        
        if isinstance(data, list):
            for repo in data:
                repos.append({
                    "login": username,
                    "full_name": repo.get("full_name", ""),
                    "created_at": repo.get("created_at", ""),
                    "stargazers_count": repo.get("stargazers_count", ""),
                    "watchers_count": repo.get("watchers_count", ""),
                    "language": repo.get("language", ""),
                    "has_projects": bool_to_str(repo.get("has_projects")),  # Use bool_to_str function
                    "has_wiki": bool_to_str(repo.get("has_wiki")),  # Use bool_to_str function
                    "license_name": repo["license"]["name"] if repo.get("license") else ""
                })
                
                if len(repos) >= 500:  # Stop if we have fetched 500 repositories
                    break
        
        if 'next' not in response.links or len(repos) >= 500:
            break
        params['page'] += 1  # Move to next page if available
    
    return repos

# Read users.csv and get the list of usernames
def read_users_csv():
    users_df = pd.read_csv('users.csv')
    return users_df['login'].tolist()

# Save the repository data to repositories.csv
def save_repos_to_csv(repos):
    with open('repositories.csv', mode='w', newline='', encoding='utf-8') as file:
        writer = csv.DictWriter(file, fieldnames=["login", "full_name", "created_at", "stargazers_count", "watchers_count", "language", "has_projects", "has_wiki", "license_name"])
        writer.writeheader()
        writer.writerows(repos)

# Main function to scrape repositories for each user
if __name__ == "__main__":
    users = read_users_csv()
    all_repos = []
    
    for user in users:
        repos = get_repositories_for_user(user)
        all_repos.extend(repos)
        print(f"Fetched {len(repos)} repositories for user: {user}")
    
    save_repos_to_csv(all_repos)
    print(f"Saved {len(all_repos)} repositories to repositories.csv.")
