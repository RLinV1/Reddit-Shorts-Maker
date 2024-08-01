import os
import re

import praw
from dotenv import load_dotenv
from playwright.sync_api import sync_playwright, ViewportSize

# Load the .env file
load_dotenv()


def enable_dark_mode(page):
    # Add a custom style to enable dark mode
    page.evaluate('''
        document.documentElement.classList.add('theme-dark');
        document.querySelector('body').style.backgroundColor = '#1e1e1e';  // Optional: set background color
    ''')


def login_to_reddit(page, username, password):
    # Navigate to Reddit login page
    page.goto('https://www.reddit.com/login/')

    # Fill in the login form
    page.fill('input[name="username"]', username)
    page.fill('input[name="password"]', password)

    # Click the login button
    page.get_by_role("button", name="Log In").click()

    # Wait for login to complete
    page.wait_for_timeout(10000)  # Increase timeout if needed


def take_screenshots_of_reddit_posts(page, posts):
    """
    Takes screenshots of Reddit posts.

    :param page: The Playwright page object
    :param posts: List of tuples containing (url, post_id) for each Reddit post
    """
    for url, post_id, index in posts:
        screenshot_path = f"screenshots/post_{index}.png"

        # Navigate to the Reddit post URL
        page.goto(url)

        # Wait for the specific post to load
        page.wait_for_selector(f'#t3_{post_id}', timeout=10000)  # Adjust the timeout if needed


        # manual selection of where to clip
        # Take a screenshot of the post with custom options
        page.screenshot(
            path=screenshot_path,
            clip={
                "x": 535,
                "y": 70,
                "width": 780,
                "height": 300
            }
        )


# Function to replace bad words
def replace_bad_words(text, bad_words):
    for bad_word, replacement in bad_words.items():
        text = re.sub(r'\b' + re.escape(bad_word) + r'\b', replacement, text, flags=re.IGNORECASE)
    return text


def clean_text(text):
    """
    Clean and preprocess the text by removing unwanted lines.

    :param text: The raw text to be cleaned
    :return: Cleaned text
    """

    pattern = r'^.*https?://\S+.*$'

    # Use re.sub to replace matching lines with an empty string
    cleaned_text = re.sub(pattern, '', text, flags=re.MULTILINE)

    # Remove any extra newlines that may be left after removal
    cleaned_text = re.sub(r'\n+', '\n', cleaned_text).strip()

    # Remove URLs or specific unwanted patterns if needed
    cleaned_text = re.sub(r'https?://\S+', '', cleaned_text)

    # Remove unwanted characters or lines
    cleaned_text = re.sub(r'[^\w\s\n\'\".,!?’‘]', '', cleaned_text)

    # Optional: Further text processing as needed
    cleaned_text = re.sub(r'[^\S\n]+', ' ', cleaned_text).strip()

    return cleaned_text



def get_reddit_posts():
    # Retrieve the credentials from the environment variables
    client_id = os.getenv('CLIENT_ID')
    client_secret = os.getenv('CLIENT_SECRET')
    user_agent = os.getenv('USER_AGENT')

    # Set up the Reddit instance with your credentials
    reddit = praw.Reddit(
        client_id=client_id,
        client_secret=client_secret,
        user_agent=user_agent
    )

    # Choose the subreddit you want to get hot posts from
    subreddit = reddit.subreddit('AITAH')

    # Get the top posts
    top_posts = subreddit.top(time_filter="day", limit=10)

    if not os.path.exists("posts"):
        os.mkdir("posts")

    if not os.path.exists("screenshots"):
        os.mkdir("screenshots")

    bad_words = {
        "fuck": "frick",
        "AITAH": "Am I the a hole",
        "asshole": "a hole"
        # Add more bad words and their replacements as needed
    }

    # Collect post URLs and IDs
    posts = []
    for index, post in enumerate(top_posts):
        # Save the cleaned text of the post
        with open(f"posts/post_{index}.txt", 'w', encoding="utf-8") as file:
            cleaned_title = replace_bad_words(post.title, bad_words)
            file.write(cleaned_title + "\n")
            text = post.selftext
            cleaned_text = clean_text(text)
            cleaned_text = replace_bad_words(cleaned_text, bad_words)
            file.write(cleaned_text)

        # Append post URL and ID
        posts.append((post.url, post.id, index))

    return posts


if __name__ == "__main__":
    with sync_playwright() as p:
        # Launch Chromium browser
        browser = p.chromium.launch(
            headless=False)  # Use headless=True if you want to run the browser in the background

        # Define viewport and device scale factor
        W, H = 1920, 1080  # Example resolution
        dsf = (W // 600) + 1

        # Set up browser context
        context = browser.new_context(
            locale="en-us",
            color_scheme="dark",
            viewport=ViewportSize(width=W, height=H),
            device_scale_factor=dsf,
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36"
        )

        page = context.new_page()

        # Enable dark mode
        enable_dark_mode(page)

        # Login to Reddit
        login_to_reddit(page, os.getenv('REDDIT_USERNAME'), os.getenv('REDDIT_PASSWORD'))

        print("SUCCESSFLLY LOGGED IN")

        # Get Reddit posts
        posts = get_reddit_posts()

        # Take screenshots of Reddit posts
        take_screenshots_of_reddit_posts(page, posts)

        print("SCREENSHOTS TAKEN!")

        # Close the browser
        browser.close()
