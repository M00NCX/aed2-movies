# main.py

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
import os
import requests
from pydantic import BaseModel
from typing import List, Optional
from .aStar import build_graph, a_star_search

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
    if not TMDB_API_KEY:
        raise HTTPException(status_code=500, detail="Chave da API não configurada.")
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

    # 1. Busca o filme inicial para pegar seu ID e dados
    searched_movie_data = find_movie_by_title(movie_title)
    start_movie_id = searched_movie_data["id"]

    # 2. Busca um conjunto maior de filmes para construir o grafo
    # Usamos o endpoint 'discover' do TMDB para pegar filmes populares dos mesmos gêneros
    main_genre_id = searched_movie_data.get("genre_ids", [])[0] if searched_movie_data.get("genre_ids") else None
    
    movie_pool = get_movie_pool(genre_id=main_genre_id)
    
    # Adiciona o filme buscado ao pool, caso ele não esteja lá
    if not any(m['id'] == start_movie_id for m in movie_pool):
        movie_pool.append(searched_movie_data)

    # 3. Enriquece os dados (adiciona diretor, etc.)
    full_movie_data = [process_movie_data(movie) for movie in movie_pool]
    
    # 4. Constrói o grafo em memória
    graph = build_graph(full_movie_data)
    
    # Verifica se o filme inicial está no grafo
    if start_movie_id not in graph:
        raise HTTPException(status_code=404, detail="Não foi possível processar o filme inicial no grafo.")

    # 5. Executa o A* do filme inicial para todos os outros e ranqueia
    recommendations_with_cost = []
    for movie_id in graph:
        if movie_id != start_movie_id:
            # Roda o A* para encontrar o caminho e o custo
            path, cost = a_star_search(graph, start_movie_id, movie_id)
            if path:  # Se um caminho foi encontrado
                recommendations_with_cost.append({"id": movie_id, "cost": cost})

    # Ordena os resultados pelo menor custo
    sorted_recommendations = sorted(recommendations_with_cost, key=lambda x: x["cost"])
    
    # Pega os 12 melhores resultados (ou quantos você quiser)
    top_recommendation_ids = {rec["id"] for rec in sorted_recommendations[:12]}
    
    # Filtra a lista de filmes completa para retornar apenas os melhores
    final_recommendations = [movie for movie in full_movie_data if movie["id"] in top_recommendation_ids]

    # Processa o filme principal também
    processed_searched_movie = next((m for m in full_movie_data if m['id'] == start_movie_id), searched_movie_data)

    return {"searched_movie": processed_searched_movie, "recommendations": final_recommendations}

# --- Funções auxiliares (coloque-as em seu main.py) ---
def find_movie_by_title(title: str) -> dict:
    search_url = f"{TMDB_API_URL}/search/movie"
    params = {"api_key": TMDB_API_KEY, "query": title, "language": "pt-BR"}
    response = requests.get(search_url, params=params)
    response.raise_for_status()
    results = response.json().get("results")
    if not results:
        raise HTTPException(status_code=404, detail=f"Filme '{title}' não encontrado.")
    return results[0]

def get_movie_pool(genre_id: Optional[int] = None, page_limit: int = 3) -> List[dict]:
    pool = []
    discover_url = f"{TMDB_API_URL}/discover/movie"
    for page in range(1, page_limit + 1):
        params = {
            "api_key": TMDB_API_KEY,
            "language": "pt-BR",
            "sort_by": "popularity.desc",
            "include_adult": False,
            "page": page,
            "with_genres": str(genre_id) if genre_id else ""
        }
        response = requests.get(discover_url, params=params)
        pool.extend(response.json().get("results", []))
    
    return pool
    
   