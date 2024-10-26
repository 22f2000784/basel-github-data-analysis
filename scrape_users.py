import requests
import csv
import os

# Set up GitHub API access
GITHUB_TOKEN = os.getenv('GITHUB_TOKEN')  # Use your environment variable
headers = {
    "Authorization": f"token {GITHUB_TOKEN}",
    "Accept": "application/vnd.github.v3+json"
}

# Function to clean company names
def clean_company_name(company):
    if company:
        company = company.strip()  # Remove leading/trailing whitespace
        if company.startswith('@'):
            company = company[1:]  # Remove leading @
        return company.upper()  # Convert to uppercase
    return ""  # Return empty string if no company

# Function to get users from Basel with more than 10 followers
def get_users_from_basel():
    users = []
    params = {
        "q": "location:Basel followers:>10",
        "per_page": 100,
        "page": 1
    }
    
    while True:
        response = requests.get("https://api.github.com/search/users", headers=headers, params=params)
        data = response.json()

        if 'items' not in data:
            break
        
        for user in data['items']:
            user_info = requests.get(f"https://api.github.com/users/{user['login']}", headers=headers).json()
            
            users.append({
                "login": user_info.get("login", ""),
                "name": user_info.get("name", ""),
                "company": clean_company_name(user_info.get("company", "")),
                "location": user_info.get("location", ""),
                "email": user_info.get("email", ""),
                "hireable": bool_to_str(user_info.get("hireable")),  # Use the updated boolean conversion function
                "bio": user_info.get("bio", ""),
                "public_repos": user_info.get("public_repos", ""),
                "followers": user_info.get("followers", ""),
                "following": user_info.get("following", ""),
                "created_at": user_info.get("created_at", "")
            })

        
        if 'next' not in response.links:
            break
        params['page'] += 1  # Move to next page if available
    
    return users

# Save the data to users.csv
def save_users_to_csv(users):
    with open('users.csv', mode='w', newline='', encoding='utf-8') as file:
        writer = csv.DictWriter(file, fieldnames=["login", "name", "company", "location", "email", "hireable", "bio", "public_repos", "followers", "following", "created_at"])
        writer.writeheader()
        writer.writerows(users)
        
def bool_to_str(value):
    if value is None:
        return ""  # Empty string for null
    return "true" if value else "false"  # Ensure lowercase

# Main function
if __name__ == "__main__":
    users = get_users_from_basel()
    save_users_to_csv(users)
    print(f"Saved {len(users)} users to users.csv.")
