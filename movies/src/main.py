# main.py

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
import os
import requests
from pydantic import BaseModel
from typing import List, Optional

load_dotenv()
app = FastAPI()

origins = ["http://localhost:5173"]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

TMDB_API_KEY = os.getenv("TMDB_API_KEY")
TMDB_API_URL = "https://api.themoviedb.org/3"

# --- PARTE 1: DECLARAÇÃO GLOBAL DA VARIÁVEL ---
# Esta linha é crucial. Ela cria o dicionário que será usado por outras funções.
GENRE_MAP = {}

# --- PARTE 2: PREENCHIMENTO DA VARIÁVEL NA INICIALIZAÇÃO ---
@app.on_event("startup")
def load_genres():
    global GENRE_MAP # Usamos 'global' para modificar a variável que está fora da função
    if not TMDB_API_KEY:
        print("AVISO: Chave da API do TMDB não configurada.")
        return
    
    genres_url = f"{TMDB_API_URL}/genre/movie/list"
    params = {"api_key": TMDB_API_KEY, "language": "pt-BR"}
    try:
        response = requests.get(genres_url, params=params)
        response.raise_for_status()
        genres_data = response.json()
        GENRE_MAP = {genre["id"]: genre["name"] for genre in genres_data.get("genres", [])}
        print("--- Mapa de gêneros carregado com sucesso ---")
    except requests.exceptions.RequestException as e:
        print(f"--- Erro ao carregar mapa de gêneros: {e} ---")

# --- MODELOS DE DADOS ---
class Movie(BaseModel):
    id: int; title: str; overview: Optional[str] = None; poster_path: Optional[str] = None; release_date: Optional[str] = None; vote_average: Optional[float] = None; genre_ids: Optional[List[int]] = []; genre: Optional[List[str]] = []; director: Optional[str] = None; popularity: Optional[float] = None

class RecommendationResponse(BaseModel):
    searched_movie: Movie; recommendations: List[Movie]

# --- ENDPOINTS ---
@app.get("/genres")
def get_genres_endpoint():
    return GENRE_MAP

def get_director(movie_id: int) -> Optional[str]:
    credits_url = f"{TMDB_API_URL}/movie/{movie_id}/credits"
    params = {"api_key": TMDB_API_KEY, "language": "pt-BR"}
    try:
        response = requests.get(credits_url, params=params)
        response.raise_for_status()
        for member in response.json().get("crew", []):
            if member.get("job") == "Director":
                return member.get("name")
        return None
    except requests.exceptions.RequestException:
        return None

@app.get("/recommendations/{movie_title}", response_model=RecommendationResponse)
def get_recommendations_from_tmdb(movie_title: str):
    if not TMDB_API_KEY: raise HTTPException(status_code=500, detail="Chave da API não configurada.")
    
    # --- PARTE 3: USO DA VARIÁVEL GLOBAL DENTRO DO ENDPOINT ---
    def process_movie_data(movie_data: dict) -> dict:
        genre_ids = movie_data.get("genre_ids", [])
        # Esta linha agora funciona, pois GENRE_MAP existe no escopo global
        movie_data["genre"] = [GENRE_MAP.get(gid, "Desconhecido") for gid in genre_ids if gid in GENRE_MAP]
        movie_data["director"] = get_director(movie_data["id"])
        return movie_data
        
    try:
        search_url = f"{TMDB_API_URL}/search/movie"
        params = {"api_key": TMDB_API_KEY, "query": movie_title, "language": "pt-BR"}
        response = requests.get(search_url, params=params)
        response.raise_for_status()
        search_results = response.json().get("results")
        if not search_results: raise HTTPException(status_code=404, detail=f"Filme '{movie_title}' não encontrado.")
        
        searched_movie_data = search_results[0]
        movie_id = searched_movie_data["id"]
        
        reco_url = f"{TMDB_API_URL}/movie/{movie_id}/recommendations"
        params = {"api_key": TMDB_API_KEY, "language": "pt-BR"}
        reco_response = requests.get(reco_url, params=params)
        reco_response.raise_for_status()
        recommendations_list = reco_response.json().get("results", [])

        processed_searched_movie = process_movie_data(searched_movie_data)
        processed_recommendations = [process_movie_data(movie) for movie in recommendations_list]

        return {"searched_movie": processed_searched_movie, "recommendations": processed_recommendations}
    except requests.exceptions.RequestException as e:
        raise HTTPException(status_code=503, detail=f"Erro de comunicação com TMDB: {e}")