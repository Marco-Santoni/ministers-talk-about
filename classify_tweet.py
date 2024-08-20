from openai import OpenAI
import dotenv
import os
import polars as pl

PROMPT = """Consider the following Tweet posted by a {minister_role} in Italy.
"{tweet_text}"

Is the content of the Tweet relevant and pertaining to his role of a {minister_role}?
Answer only with Yes or No or Not Sure
"""

dotenv.load_dotenv(".env")

client = OpenAI(
  organization=os.getenv("OPEN_AI_ORGANIZATION"),
  project=os.getenv("OPEN_AI_PROJECT"),
  api_key=os.getenv("OPEN_AI_API_KEY")
)

df = pl.read_csv("./data/tweets.csv")
df_ministers = pl.read_csv("./data/italian_ministers.csv").with_columns(
        pl.col("Twitter Handle").str.replace("@", "").alias("twitter_username")
    )
df = df.join(df_ministers, how="inner", on="twitter_username")

tweet_classified = []
for tweet in df.iter_rows(named=True):
  completion = client.chat.completions.create(
    model="gpt-4o",
    messages=[
      {
        "role": "system",
        "content": PROMPT.format(
          minister_role=tweet["Minister"],
          tweet_text=tweet["text"]
        )
      }
    ]
  )
  tweet["is_relevant"] = completion.choices[0].message.content
  print(tweet["Minister"], tweet['Twitter Handle'], tweet['created_at'], tweet["is_relevant"])
  tweet_classified.append(tweet)

pl.DataFrame(tweet_classified).write_csv("./data/tweets_classified.csv")
exit()
