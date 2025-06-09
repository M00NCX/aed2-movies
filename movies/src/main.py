# main.py (exemplo do seu backend FastAPI)

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware # Importe o middleware
from dotenv import load_dotenv
import os
import requests

# Carrega as variáveis de ambiente do arquivo .env
load_dotenv()

app = FastAPI()
# --- CONFIGURAÇÃO DO CORS ---
# Adicione os endereços do seu frontend
origins = [
    "http://localhost:5173",  # Endereço padrão do Vite/React
    "http://localhost:3000",  # Endereço padrão do create-react-app
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],  # Permite todos os métodos (GET, POST, etc)
    allow_headers=["*"],  # Permite todos os cabeçalhos
)
# --- FIM DA CONFIGURAÇÃO DO CORS ---

# Pega a chave da API das variáveis de ambiente
TMDB_API_KEY = os.getenv("TMDB_API_KEY")
TMDB_API_URL = "https://api.themoviedb.org/3"

# --- MODELOS DE DADOS (Boa prática com Pydantic) ---
# Isso ajuda na validação e documentação automática da API
from pydantic import BaseModel
from typing import List, Optional

class Movie(BaseModel):
    id: int
    title: str
    overview: Optional[str] = None
    poster_path: Optional[str] = None
    release_date: Optional[str] = None
    # Adicionamos genre_ids para poder usar na lógica de filtro, se quiser
    genre_ids: Optional[List[int]] = None

class RecommendationResponse(BaseModel):
    searched_movie: Movie
    recommendations: List[Movie]


# --- ENDPOINT PRINCIPAL ---


@app.get("/recommendations/{movie_title}", response_model=RecommendationResponse)
def get_recommendations_from_tmdb(movie_title: str):
    """
    Busca um filme pelo título, encontra seu ID e retorna as recomendações do TMDB.
    """
    if not TMDB_API_KEY:
        raise HTTPException(status_code=500, detail="Chave da API do TMDB não configurada.")

    # --- PARTE 1: Buscar o filme e seu ID ---
    search_url = f"{TMDB_API_URL}/search/movie"
    params = {"api_key": TMDB_API_KEY, "query": movie_title, "language": "pt-BR"}
    
    try:
        response = requests.get(search_url, params=params)
        response.raise_for_status()
        search_data = response.json()
        
        if not search_data.get("results"):
            raise HTTPException(status_code=404, detail=f"Filme '{movie_title}' não encontrado.")
        
        searched_movie_data = search_data["results"][0]
        movie_id = searched_movie_data["id"]

    except requests.exceptions.RequestException as e:
        raise HTTPException(status_code=503, detail=f"Erro de comunicação com TMDB: {e}")

    # --- PARTE 2: Buscar as recomendações com o ID encontrado ---
    reco_url = f"{TMDB_API_URL}/movie/{movie_id}/recommendations"
    params = {"api_key": TMDB_API_KEY, "language": "pt-BR"}

    try:
        response = requests.get(reco_url, params=params)
        response.raise_for_status()
        reco_data = response.json()
        recommendations_list = reco_data.get("results", [])

    except requests.exceptions.RequestException as e:
        raise HTTPException(status_code=503, detail=f"Erro ao buscar recomendações no TMDB: {e}")

    # --- PARTE 3: Montar a resposta final no formato esperado pelo Frontend ---
    final_response = {
        "searched_movie": searched_movie_data,
        "recommendations": recommendations_list
    }
    
    return final_response