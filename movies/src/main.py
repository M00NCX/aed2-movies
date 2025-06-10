# main.py (exemplo do seu backend FastAPI)

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware # Importe o middleware
from dotenv import load_dotenv
import os
import requests
from pydantic import BaseModel
from typing import List, Optional

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
    genre_ids: Optional[List[int]] = None # TMDB envia genre_ids
    genre: Optional[List[str]] = None # Podemos preencher depois
    director: Optional[str] = None
    vote_average: Optional[float] = None
    popularity: Optional[float] = None # ADICIONE ESTA LINHA

class RecommendationResponse(BaseModel):
    searched_movie: Movie
    recommendations: List[Movie]


# --- ENDPOINT PRINCIPAL ---


@app.get("/recommendations/{movie_title}", response_model=RecommendationResponse)
def get_recommendations_from_tmdb(movie_title: str):
    if not TMDB_API_KEY:
        raise HTTPException(status_code=500, detail="Chave da API do TMDB não configurada.")

    # --- Função auxiliar para buscar créditos (diretor) ---
    def get_director(movie_id: int) -> Optional[str]:
        credits_url = f"{TMDB_API_URL}/movie/{movie_id}/credits"
        params = {"api_key": TMDB_API_KEY, "language": "pt-BR"}
        try:
            response = requests.get(credits_url, params=params)
            response.raise_for_status()
            credits_data = response.json()
            # Procura na lista de 'crew' por alguém com o trabalho de 'Director'
            for member in credits_data.get("crew", []):
                if member.get("job") == "Director":
                    return member.get("name")
            return None # Retorna None se não encontrar diretor
        except requests.exceptions.RequestException:
            return None # Em caso de erro na chamada, retorna None

    # --- PARTE 1: Buscar o filme principal e seu ID ---
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

        # MUDANÇA: Busca o diretor do filme principal
        searched_movie_data["director"] = get_director(movie_id)

    except requests.exceptions.RequestException as e:
        raise HTTPException(status_code=503, detail=f"Erro de comunicação com TMDB: {e}")

    # --- PARTE 2: Buscar as recomendações ---
    reco_url = f"{TMDB_API_URL}/movie/{movie_id}/recommendations"
    params = {"api_key": TMDB_API_KEY, "language": "pt-BR"}
    try:
        response = requests.get(reco_url, params=params)
        response.raise_for_status()
        reco_data = response.json()
        recommendations_list = reco_data.get("results", [])

        # MUDANÇA: Itera sobre cada recomendação para buscar seu diretor
        for movie in recommendations_list:
            movie["director"] = get_director(movie["id"])

    except requests.exceptions.RequestException as e:
        raise HTTPException(status_code=503, detail=f"Erro ao buscar recomendações no TMDB: {e}")

    # --- PARTE 3: Montar a resposta final ---
    final_response = {
        "searched_movie": searched_movie_data,
        "recommendations": recommendations_list
    }
    return final_response