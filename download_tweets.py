import tweepy
from dotenv import load_dotenv
import os
import polars as pl
import time

# Load environment variables from .env file
load_dotenv(".env")

DATAFRAME_SCHEMA = [
    ("text", pl.String),
    ("created_at", pl.Datetime('us','UTC')),
    ("twitter_username", pl.String)
]
SLEEP_TIME = int(15.1 * 60)  # 15 minutes + some buffer

# Twitter API credentials
bearer_token = os.getenv("TWITTER_BEARER_TOKEN")

# Authenticate to Twitter
client = tweepy.Client(
    bearer_token=bearer_token
)

def read_ministers() -> pl.DataFrame:
    df = pl.read_csv("./data/italian_ministers.csv")
    df = df.filter(pl.col("Twitter Handle") != "N/A")
    print(df)

    df = df.with_columns(
        pl.col("Twitter Handle").str.replace("@", "").alias("Twitter Handle")
    )
    return df


def get_tweets(twitter_id: str, twitter_username: str) -> pl.DataFrame:
    # todo pagination
    # https://docs.tweepy.org/en/stable/v2_pagination.html
    # https://stackoverflow.com/questions/72016766/tweepy-only-lets-me-get-100-results-how-do-i-get-more-ive-read-about-paginati
    response_tweet = client.get_users_tweets(
        id=twitter_id,
        tweet_fields="text,created_at",
        start_time="2024-03-01T00:00:00Z",
        end_time="2024-08-16T00:00:00Z",
        max_results=100
    )
    if response_tweet.data is None:
        return pl.DataFrame(schema=DATAFRAME_SCHEMA)
    else:
        return pl.DataFrame(
            [
                {
                    "text": tweet.text,
                    "created_at": tweet.created_at,
                    "twitter_username": twitter_username
                }
                for tweet in response_tweet.data
            ]
        )

def get_twitter_id(twitter_username: str) -> str:
    response = client.get_user(username=twitter_username, user_fields="id")
    if response.data is None:
        return None
    else:
        return response.data.id

output_df = pl.DataFrame(
    schema=DATAFRAME_SCHEMA
)

for minister in read_ministers().iter_rows(named=True):
    print(minister)
    twitter_username = minister["Twitter Handle"]

    twitter_id = get_twitter_id(twitter_username)
    print(twitter_id)
    if twitter_id is None:
        continue
    else:
        try:
            new_df = get_tweets(twitter_id, twitter_username)
        except tweepy.errors.TooManyRequests:
            print("Rate limit exceeded. Sleeping for 15 minutes")
            time.sleep(SLEEP_TIME)
            new_df = get_tweets(twitter_id, twitter_username)
        output_df = output_df.vstack(new_df)

output_df.write_csv("./data/tweets.csv")
