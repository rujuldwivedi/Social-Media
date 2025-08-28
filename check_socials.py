import requests
import re
import sys
from bs4 import BeautifulSoup

# --- ⚙️ YOUR CONFIGURATION ---
INSTAGRAM_USERNAME = "rujuldwivedi"
TWITTER_USERNAME = "rujuldwivedi"
# -----------------------------

NITTER_INSTANCE_URL = "https://nitter.net"

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
}

def get_instagram_counts(username):
    """Fetches follower and following counts from an Instagram profile."""
    url = f"https://www.instagram.com/rujuldwivedi/"
    try:
        response = requests.get(url, headers=HEADERS)
        response.raise_for_status() # Raises an error for bad responses (4xx or 5xx)

        # Instagram often embeds data in meta tags, which is more reliable
        # Looking for content like: "1,234 Followers, 567 Following, 89 Posts"
        soup = BeautifulSoup(response.text, 'html.parser')
        meta_description = soup.find('meta', property='og:description')
        
        if not meta_description:
            print("❌ Could not find meta description tag on Instagram page. They may have changed their HTML structure.")
            return None, None

        content = meta_description['content']
        
        # Use regex to find the numbers
        followers = re.search(r'([\d,]+)\s+Followers', content).group(1).replace(',', '')
        following = re.search(r'([\d,]+)\s+Following', content).group(1).replace(',', '')

        return int(followers), int(following)

    except Exception as e:
        print(f"❌ Failed to fetch or parse Instagram data: {e}")
        return None, None


def get_twitter_counts(username):
    """Fetches follower and following counts from a Nitter instance."""
    url = f"{NITTER_INSTANCE_URL}/rujuldwivedi"
    try:
        response = requests.get(url, headers=HEADERS)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Nitter's HTML is much cleaner and uses specific classes
        stats_div = soup.find('div', class_='profile-stats')
        if not stats_div:
            print("❌ Could not find profile stats div on Nitter page. They may have changed their HTML structure.")
            return None, None

        followers_li = stats_div.find('li', class_='followers')
        following_li = stats_div.find('li', class_='following')

        followers = followers_li.find('span', class_='stat-value').text.replace(',', '')
        following = following_li.find('span', 'stat-value').text.replace(',', '')

        return int(followers), int(following)

    except Exception as e:
        print(f"❌ Failed to fetch or parse Twitter/X data from Nitter: {e}")
        return None, None


def main():
    """Main function to check both accounts and exit with status code."""
    mismatches_found = False
    
    # --- Check Instagram ---
    print(f"Checking Instagram for user: {INSTAGRAM_USERNAME}")
    insta_followers, insta_following = get_instagram_counts(INSTAGRAM_USERNAME)
    
    if insta_followers is not None and insta_following is not None:
        print(f"Instagram Found: {insta_followers} Followers / {insta_following} Following")
        if insta_followers != insta_following:
            mismatches_found = True
            print("🚨 MISMATCH FOUND ON INSTAGRAM!")
        else:
            print("✅ Instagram counts are in sync.")
    
    print("-" * 20)

    # --- Check Twitter/X ---
    print(f"Checking X/Twitter for user: {TWITTER_USERNAME}")
    twitter_followers, twitter_following = get_twitter_counts(TWITTER_USERNAME)

    if twitter_followers is not None and twitter_following is not None:
        print(f"X/Twitter Found: {twitter_followers} Followers / {twitter_following} Following")
        if twitter_followers != twitter_following:
            mismatches_found = True
            print("🚨 MISMATCH FOUND ON X/TWITTER!")
        else:
            print("✅ X/Twitter counts are in sync.")
            
    print("-" * 20)

    if mismatches_found:
        print("Exiting with error code to trigger GitHub Action failure.")
        sys.exit(1) # Exit with a non-zero status code to indicate failure
    else:
        print("All accounts are in sync. Exiting successfully.")
        sys.exit(0) # Exit with zero to indicate success

if __name__ == "__main__":
    main()
