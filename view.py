import streamlit as st
import polars as pl
import altair as alt

df = pl.read_csv("./data/tweets_classified.csv", try_parse_dates=True)
df_grouped = df.group_by("Minister", "Name", "is_relevant").count().sort("count", descending=True)
st.write("For each Minister of the Italia Government, the number of relevant and irrelevant tweets are as follows:")

st.write("Data refers to the period between {min_date} and {max_date}".format(
    min_date=df['created_at'].min().date().strftime("%Y-%m-%d"),
    max_date=df['created_at'].max().date().strftime("%Y-%m-%d")
))

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
