import tweepy
from dotenv import load_dotenv
import os
import polars as pl

# Load environment variables from .env file
load_dotenv(".env")

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
    return df.head(2)


def get_tweets(twitter_id: str, twitter_username: str) -> pl.DataFrame:
    response_tweet = client.get_users_tweets(
        id=twitter_id,
        tweet_fields="text,created_at",
        start_time="2024-08-12T00:00:00Z",
        end_time="2024-08-19T00:00:00Z",
    )
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
    return response.data.id

output_df = pl.DataFrame(
    schema=[
        ("text", pl.String),
        ("created_at", pl.Datetime('us','UTC')),
        ("twitter_username", pl.String)
    ]
)

for minister in read_ministers().iter_rows(named=True):
    print(minister)
    twitter_username = minister["Twitter Handle"]
    twitter_id = get_twitter_id(twitter_username)
    print(twitter_id)
    print(output_df)
    import pdb; pdb.set_trace()
    new_df = get_tweets(twitter_id, twitter_username)
    output_df = output_df.vstack(new_df)
import pdb; pdb.set_trace()
output_df.write_csv("./data/tweets.csv")
