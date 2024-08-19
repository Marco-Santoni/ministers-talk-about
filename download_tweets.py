import tweepy
from dotenv import load_dotenv
import os

# Load environment variables from .env file
load_dotenv(".env")

# Twitter API credentials
bearer_token = os.getenv("TWITTER_BEARER_TOKEN")

# Authenticate to Twitter
client = tweepy.Client(
    bearer_token=bearer_token
)

# Get the user
response = client.get_user(username="Antonio_Tajani", user_fields="id")
# print the id of the user
print(response.data.id)

response_tweet = client.get_users_tweets(
    "529247064",
    tweet_fields="text",
    max_results=10
)

# Print the tweets
for tweet in response_tweet.data:
    print(tweet.text)
