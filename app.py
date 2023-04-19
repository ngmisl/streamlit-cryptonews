import feedparser
import pytz
import openai
import streamlit as st
from datetime import datetime, timedelta

st.title("AI generated summary of Crypto news from the last 24 hours")

# List of RSS feed URLs
rss_feeds = [
    "https://decrypt.co/feed",
    "https://www.coindesk.com/arc/outboundfeeds/rss/",
    # Add more RSS feeds here
]

# OpenAI API key input
openai_api_key = st.text_input("Enter your OpenAI API Key:")
openai.api_key = openai_api_key


def get_summary_and_sentiment(text):
    messages = [
        {
            "role": "system",
            "content": "You are a helpful assistant that can provide a short summary with less than 400 characters",  # noqa: E501
        },
        {"role": "user", "content": text},
    ]
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=messages,
        max_tokens=150,
        n=1,
        stop=None,
        temperature=0.7,
    )
    result = response.choices[0].message["content"].strip()

    # Limit the output to 450 characters and stop at the last full sentence
    limited_result = ""
    for sentence in result.split(". "):
        if len(limited_result) + len(sentence) + 1 <= 450:
            if limited_result != "":
                limited_result += ". "
            limited_result += sentence
        else:
            break

    return limited_result


# Get headlines
def get_headlines(feed_url, time_limit):
    headlines_and_links = []

    feed = feedparser.parse(feed_url)
    for entry in feed.entries:
        published_date = datetime.strptime(entry.published, "%a, %d %b %Y %H:%M:%S %z")
        if published_date >= time_limit:
            headlines_and_links.append((entry.title, entry.link))

    return headlines_and_links


if openai_api_key:
    # Main function
    local_tz = pytz.timezone(
        "UTC"
    )  # Replace 'your_local_timezone' with your actual timezone
    time_limit = datetime.now(local_tz) - timedelta(days=1)
    all_headlines_and_links = []

    for feed_url in rss_feeds:
        headlines_and_links = get_headlines(feed_url, time_limit)
        all_headlines_and_links.extend(headlines_and_links)

    combined_titles = " ".join([headline for headline, _ in all_headlines_and_links])
    summary_and_sentiment = get_summary_and_sentiment(combined_titles)

    st.write(f"**Summary:**\n{summary_and_sentiment}")

    st.header("News articles:")
    for title, link in all_headlines_and_links:
        st.markdown(f"[{title}]({link})")

else:
    st.write("Please enter your OpenAI API key to get the summary.")
