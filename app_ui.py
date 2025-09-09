import streamlit as st
import pickle
import pandas as pd
import requests
import time


st.markdown(
    """
    <style>
    .stApp {
        background: linear-gradient(135deg, #181C36 40%, #1D2576 100%);
        min-height: 100vh;
        background-attachment: fixed;
    }
    section[data-testid="stSidebar"] {
        background: linear-gradient(135deg, #232859 60%, #181C36 100%);
    }
    </style>
    """,
    unsafe_allow_html=True
)

st.set_page_config(layout="wide", page_title="🎬 Movie Recommender")

# Load data
movies_list = pickle.load(open('movie_list.pkl', 'rb'))
movies = pd.DataFrame(movies_list)
similarity = pickle.load(open('similarity.pkl', 'rb'))

def fetch_poster(movie_id):
    url = f"https://api.themoviedb.org/3/movie/{movie_id}?api_key=8265bd1679663a7ea12ac168da84d2e8&language=en-US"
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        data = response.json()
        poster_path = data.get('poster_path')
        time.sleep(0.2)
        return f"https://image.tmdb.org/t/p/w500/{poster_path}" if poster_path else None
    except Exception as e:
        print(f"❌ Error fetching poster for {movie_id}: {e}")
        return None

def recommend(movie, num_recs=5):
    filtered = movies[movies['title'] == movie]
    if filtered.empty:
        st.error("Selected movie not found in database.")
        return [], []
    movie_index = filtered.index[0]
    distances = similarity[movie_index]

    if len(distances) != len(movies):
        st.error("Similarity data mismatch. Please check data files.")
        return [], []

    movie_list = sorted(list(enumerate(distances)), reverse=True, key=lambda x: x[1])[1:num_recs+1]
    recommended_movies = []
    recommended_movies_posters = []
    for i in movie_list:
        try:
            movie_id = movies.iloc[i[0]].movie_id
            recommended_movies.append(movies.iloc[i[0]].title)
            recommended_movies_posters.append(fetch_poster(movie_id))
        except Exception as e:
            print(f"Error getting recommendation for index {i[0]}: {e}")

    return recommended_movies, recommended_movies_posters

st.markdown("<h1 style='text-align: center; color:white;'>🎬 Movie Recommender System</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center; color:white;'>Find your next favorite movie. Search, select, and see recommendations instantly!</p>", unsafe_allow_html=True)
st.divider()

st.sidebar.header("Get Recommendations")
selected_movie_name = st.sidebar.selectbox('Select a movie:', movies['title'].values)
num_recs = st.sidebar.slider('Number of recommendations:', min_value=3, max_value=10, value=5)
if st.sidebar.button('Show Recommendations'):
    with st.spinner("Fetching recommendations..."):
        names, posters = recommend(selected_movie_name, num_recs=num_recs)
        if names:
            st.subheader("Recommended Movies 🍿")
            cols = st.columns(len(names))
            for name, poster, col in zip(names, posters, cols):
                with col:
                    st.markdown(f"<span style='color:white; font-weight:bold;'>{name}</span>", unsafe_allow_html=True)
                    if poster:
                        st.image(poster, use_container_width=True)  # Updated here
                    else:
                        st.write("🚫 Poster not available")
        else:
            st.warning("No recommendations available.")

st.divider()
st.markdown("<p style='text-align: center; color:lightgray;'>Made with Streamlit | Powered by TMDB API</p>", unsafe_allow_html=True)
