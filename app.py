import streamlit as st
import pickle
import pandas as pd
import requests
import time



movies_list = pickle.load(open('movie_list.pkl','rb'))
movies = pd.DataFrame(movies_list)
similarity = pickle.load(open('similarity.pkl','rb'))

# Fetch poster safely
def fetch_poster(movie_id):
    url = f"https://api.themoviedb.org/3/movie/{movie_id}?api_key=8265bd1679663a7ea12ac168da84d2e8&language=en-US"
    try:
        response = requests.get(url, timeout=10)  # timeout for safety
        response.raise_for_status()
        data = response.json()
        poster_path = data.get('poster_path')
        time.sleep(0.2)  # small delay to avoid TMDB blocking
        return f"https://image.tmdb.org/t/p/w500/{poster_path}" if poster_path else None
    except Exception as e:
        print(f"❌ Error fetching poster for {movie_id}: {e}")
        return None

# Recommend movies
def recommend(movie):
    movie_index = movies[movies['title'] == movie].index[0]
    distances = similarity[movie_index]
    movie_list = sorted(list(enumerate(distances)), reverse=True, key=lambda x: x[1])[1:6]
    
    recommended_movies = []
    recommended_movies_posters = []
    for i in movie_list:
        movie_id = movies.iloc[i[0]].movie_id
        recommended_movies.append(movies.iloc[i[0]].title)
        recommended_movies_posters.append(fetch_poster(movie_id))
    return recommended_movies, recommended_movies_posters

# Streamlit UI
st.title('🎬 Movie Recommender System')

selected_movie_name = st.selectbox(
    'Select a movie:',
    movies['title'].values
)

if st.button('Show Recommendation'):
    names, posters = recommend(selected_movie_name)
    cols = st.columns(5)  

    for name, poster, col in zip(names, posters, cols):
        with col:
            st.text(name)
            if poster:
                st.image(poster)
            else:
                st.write("🚫 Poster not available")
