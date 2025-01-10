import streamlit as st
import pandas as pd
import requests
import re

def clean_title(full_title):
    match = re.match(r'^(.*)\s\(\d{4}\)$', full_title)
    if match:
        return match.group(1)
    return full_title

def get_poster(movie_title, api_key = "ff24dd611d23ace017d1162967cd1075"):
    url = f'https://api.themoviedb.org/3/search/movie'
    params = {'api_key' : api_key, 'query': clean_title(movie_title)}
    resp = requests.get(url, params = params)
    data = resp.json()
    if data['results']:
        print(data)
        return f"https://image.tmdb.org/t/p/w500{data['results'][0]['poster_path']}"
    return None


recommendation_df = pd.read_csv('data/recommendations.csv')
st.title("Movie Recommendations")
user_id = st.number_input("Enter your User ID", min_value=1, max_value=601, step=1)

if st.button("Get Recommendations"):
    user_recs = recommendation_df[recommendation_df["userId"] == user_id]

    if user_recs.empty:
        st.warning("No recommendations found for this User ID.")
    else:
        st.success(f"Recommendations for User ID {user_id}:")
        for _, row in user_recs.iterrows():
            movie_title = row["title"]
            genres = row["genres"]
            poster_url = get_poster(movie_title)
            col1, col2 = st.columns([1, 4])
            with col1:
                if poster_url:
                    st.image(poster_url, width=100)
                else:
                    st.write("No Poster")
            with col2:
                st.write(f"**{movie_title}**")
                st.write(f"*Genres:* {genres}")
