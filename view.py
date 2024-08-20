import streamlit as st
import polars as pl
import altair as alt
import streamlit.components.v1 as components

df = pl.read_csv("./data/tweets_classified.csv", try_parse_dates=True)
df_grouped = df.group_by("Minister", "Name", "is_relevant").count().sort("count", descending=True)
st.write("# Intro")
st.write("Are there different communication strategies on *Twitter* among Government members? Do Ministers mainly tweet about topics that are strictly **related** to their role? For each Minister of the Italia Government with a Twitter account, we collected a set of recent Tweets. For each Tweet, we classified as `is_relevant=Yes/No` with respect to the Ministery that the tweeting minister is currently leading.  ")

st.write("The following tweet is an example of a tweet that is relevant (`is_relevant=Yes`) to the Minister of Foreign Affairs.")

components.html(
    """
    <blockquote class="twitter-tweet"><p lang="it" dir="ltr">Insieme ai colleghi di 🇬🇧 🇩🇪 🇫🇷 sostengo gli sforzi di mediazione in corso di USA, Egitto e Qatar per accordo sul <a href="https://twitter.com/hashtag/cessateilfuoco?src=hash&amp;ref_src=twsrc%5Etfw">#cessateilfuoco</a> e su rilascio ostaggi.<br>Non possiamo perdere tempo: lavoriamo insieme a tutti i paesi della regione per dare al M.O. prospettive di stabilità e pace.</p>&mdash; Antonio Tajani (@Antonio_Tajani) <a href="https://twitter.com/Antonio_Tajani/status/1824809969964798414?ref_src=twsrc%5Etfw">August 17, 2024</a></blockquote> <script async src="https://platform.twitter.com/widgets.js" charset="utf-8"></script>
    """,
    height=300
)

st.write("The following tweet is an example of a tweet that is **not relevant** (`is_relevant=No`) to the Minister of Foreign Affairs.")

components.html(
    """
    <blockquote class="twitter-tweet"><p lang="it" dir="ltr">Oggi festeggiamo l’Assunzione di Maria in cielo, una ricorrenza di grande valore spirituale per tutti i cristiani devoti alla Vergine. Guardiamo al futuro con una speranza di pace e auguro a tutti gli italiani momenti di serenità e amore in famiglia. Buon <a href="https://twitter.com/hashtag/Ferragosto?src=hash&amp;ref_src=twsrc%5Etfw">#Ferragosto</a>! 🇮🇹 ☀️ <a href="https://t.co/zg1vVDUZRe">pic.twitter.com/zg1vVDUZRe</a></p>&mdash; Antonio Tajani (@Antonio_Tajani) <a href="https://twitter.com/Antonio_Tajani/status/1823976948013384031?ref_src=twsrc%5Etfw">August 15, 2024</a></blockquote> <script async src="https://platform.twitter.com/widgets.js" charset="utf-8"></script>
    """,
    height=300
)

st.write(
    "I analyzed {n_tweets} tweets from the following {n_ministers} Ministers.".format(
        n_tweets=df.shape[0],
        n_ministers=df['Minister'].n_unique()
    )
)
st.dataframe(df.select(['Minister', 'Name', "Twitter Handle"]).unique())

st.write("# Disclaimer")
st.write("When classifying the tweets by a Minister, I do not aim at judging the effectiveness of the work by the Minister. The fact that a Minister mostly Tweets about topics that are **not** related to its Ministery does **not** imply that the Minister is not doing his/her job properly. The analysis has purely the goal of measuring quantitavely the communication style.")

st.write("# Results")

st.write("I collected the most recent (up to) 100 tweets on August 16th 2024. The oldest Tweet in the data set is on {min_date} while the latest on {max_date}. Consider that Tweets are not evenly distributed in this time period though.".format(
    min_date=df['created_at'].min().date().strftime("%Y-%m-%d"),
    max_date=df['created_at'].max().date().strftime("%Y-%m-%d")
))

st.write("The following chart shows the number of tweets classified as `is_relevant=Yes/No/Not Sure` for each Minister.")

chart = (
    alt.Chart(df_grouped.to_pandas())
    .mark_bar()
    .encode(
        y=alt.Y("Name", sort="y"),
        x="count",
        color=alt.Color(
            "is_relevant",
            scale=alt.Scale(
                domain=['Yes', 'No', 'Not Sure'],
                range=["#9ee39a", "#cc6262", "#c7c7c7"],
            ),
        ),
        tooltip=["Name", "is_relevant", "count", "Minister"],
    )
)

st.altair_chart(chart, use_container_width=True)

st.write("Similarly, the following chart shows the percentage of tweets classified as `is_relevant=Yes/No/Not Sure` for each Minister.")

chart = (
    alt.Chart(df_grouped.to_pandas())
    .mark_bar()
    .encode(
        y=alt.Y("Name", sort="y"),
        x=alt.X("count").stack("normalize"),
        color=alt.Color(
            "is_relevant",
            scale=alt.Scale(
                domain=['Yes', 'No', 'Not Sure'],
                range=["#9ee39a", "#cc6262", "#c7c7c7"],
            ),
        ),
        tooltip=["Name", "is_relevant", "count", "Minister"],
    )
)

st.altair_chart(chart, use_container_width=True)
st.write("💡 It turns out that **Matteo Salvini** is the Minister that most often Tweets about topics that are **not related** to his Ministery.")

st.write("You can select a Minister from the following dropdown to see the tweets posted by the selected Minister.")

selected_minister = st.selectbox("Select Minister", df.select("Name").unique().sort(by="Name"))
st.write(f"Tweets posted by {selected_minister}:")

chart_2 = (
    alt.Chart(
        df.filter(pl.col("Name") == selected_minister)
        .with_columns(
            pl.col("created_at").dt.date().alias("date")
        ).group_by("date", "is_relevant")
        .count().to_pandas()
    )
    .mark_bar()
    .encode(
        y="count",
        x="date",
        color=alt.Color(
            "is_relevant",
            scale=alt.Scale(
                domain=['Yes', 'No', 'Not Sure'],
                range=["#9ee39a", "#cc6262", "#c7c7c7"],
            ),
        )
    )
)

st.altair_chart(chart_2, use_container_width=True)

st.dataframe(
    df.filter(pl.col("Name") == selected_minister).select(['is_relevant', 'text', 'created_at'])
)

st.write("# Method")

st.write("I collected the tweets using the Twitter API (yes, it is expensive 😭). I asked ChatGPT the list of the Ministers and their Twitter Handle. It worked correctly except for Lollobrigida (that I fixeed manually). I did not check if the Ministers that do not have a Twitter Handle account according to ChatGPT actually do not have one (sorry if this is not the case). For each Tweet, I asked `gpt-4o` via Open AI APIs to classify the Tweet as relevant (`Yes`, `No`, `Not Sure`) according to his/her Ministry. Data processing was done via `Polars`. I finally tried it our and loved the syntax compared to `Pandas` (perhaps because I worked quite a bit with `PySpark` over the last years).")

st.write("# Next ")

st.write("""
Wishlist on how to extend this fun project:

- compare with Ministers from other EU countries
- extend time horizon
- schedule the data collection on a regular basis
""")

st.write("""
# About

I'm [Marco Santoni](https://www.linkedin.com/in/msantoni/) and did this project for fun. I was inspired by this [post](https://www.linkedin.com/posts/pierfrancescomaran_frejus-linterrogazione-del-pd-post-di-activity-7227291478102798336-sz5D?utm_source=share&utm_medium=member_desktop) on LinkedIn. I was curious wether the critics by Pierfrancesco Maran to Matteo Salvini about his Twitter activity were statistically justified. It turned out they were (regardless of the actual meaning concerning the work by the Minister).
""")
