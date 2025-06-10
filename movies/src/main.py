# src/main.py

# --- 1. IMPORTS ---
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
import os
import requests
from pydantic import BaseModel
from typing import List, Optional

from neo4j import GraphDatabase, Driver
# Assumindo que seu arquivo de algoritmo se chama aStar.py
from .aStar import build_graph, a_star_search

# --- 2. CONFIGURAÇÃO DA APLICAÇÃO E VARIÁVEIS GLOBAIS ---
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
NEO4J_URI = os.getenv("NEO4J_URI")
NEO4J_USER = os.getenv("NEO4J_USER")
NEO4J_PASSWORD = os.getenv("NEO4J_PASSWORD")

driver: Optional[Driver] = None
GENRE_MAP = {}

# --- 3. EVENTOS DE CICLO DE VIDA (STARTUP / SHUTDOWN) ---
@app.on_event("startup")
def startup_event():
    global driver, GENRE_MAP
    try:
        driver = GraphDatabase.driver(NEO4J_URI, auth=(NEO4J_USER, NEO4J_PASSWORD), encrypted=False)
        driver.verify_connectivity()
        print("--- Conexão com o Neo4j estabelecida com sucesso! ---")
    except Exception as e:
        print(f"--- Falha ao conectar com o Neo4j: {e} ---")
    
    if TMDB_API_KEY:
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
    else:
        print("AVISO: Chave da API do TMDB não configurada.")

@app.on_event("shutdown")
def shutdown_db_client():
    if driver:
        driver.close()
        print("--- Conexão com o Neo4j fechada. ---")

# --- 4. MODELOS DE DADOS (PYDANTIC) ---
class Movie(BaseModel):
    id: int; title: str; overview: Optional[str] = None; poster_path: Optional[str] = None; release_date: Optional[str] = None; vote_average: Optional[float] = None; genre_ids: Optional[List[int]] = []; genre: Optional[List[str]] = []; director: Optional[str] = None; popularity: Optional[float] = None

class RecommendationResponse(BaseModel):
    searched_movie: Movie; recommendations: List[Movie]

# --- 5. FUNÇÕES AUXILIARES ---
def find_movie_by_title(title: str) -> dict:
    search_url = f"{TMDB_API_URL}/search/movie"
    params = {"api_key": TMDB_API_KEY, "query": title, "language": "pt-BR"}
    response = requests.get(search_url, params=params)
    response.raise_for_status()
    results = response.json().get("results")
    if not results:
        raise HTTPException(status_code=404, detail=f"Filme '{title}' não encontrado.")
    return results[0]

def get_director(movie_id: int) -> Optional[str]:
    if not movie_id or not TMDB_API_KEY: return None
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

def process_movie_data(movie_data: dict) -> dict:
    if 'tmdbId' in movie_data and 'id' not in movie_data:
        movie_data['id'] = movie_data['tmdbId']
    genre_ids = movie_data.get("genre_ids", [])
    movie_data["genre"] = [GENRE_MAP.get(gid) for gid in genre_ids if GENRE_MAP.get(gid)]
    movie_data["director"] = get_director(movie_data.get("id"))
    return movie_data

def create_movie_in_neo4j(tx, movie_data: dict):
    tx.run("""
        MERGE (m:Movie {tmdbId: $movie.id})
        ON CREATE SET m.title = $movie.title, m.release_date = $movie.release_date, m.popularity = $movie.popularity
    """, movie=movie_data)
    if movie_data.get("director"):
        tx.run("""
            MATCH (m:Movie {tmdbId: $movie.id})
            MERGE (p:Person {name: $movie.director})
            MERGE (p)-[:DIRECTED]->(m)
        """, movie=movie_data)
    if movie_data.get("genre"):
        tx.run("""
            MATCH (m:Movie {tmdbId: $movie.id})
            UNWIND $movie.genre as genre_name
            MERGE (g:Genre {name: genre_name})
            MERGE (m)-[:HAS_GENRE]->(g)
        """, movie=movie_data)

def get_movie_pool_from_tmdb(movie_id: int) -> List[dict]:
    reco_url = f"{TMDB_API_URL}/movie/{movie_id}/recommendations"
    params = {"api_key": TMDB_API_KEY, "language": "pt-BR", "page": 1}
    response = requests.get(reco_url, params=params)
    response.raise_for_status()
    return response.json().get("results", [])

# --- 6. ENDPOINTS DA API ---
@app.get("/genres")
def get_genres_endpoint():
    return GENRE_MAP

@app.get("/recommendations/{movie_title}", response_model=RecommendationResponse)
def get_recommendations(movie_title: str):
    if not driver:
        raise HTTPException(status_code=503, detail="Serviço de banco de dados indisponível.")

    # ETAPA 1: Popular o Neo4j com dados do TMDB
    try:
        start_movie_data = find_movie_by_title(movie_title)
        start_movie_id = start_movie_data["id"]
        movie_pool_from_tmdb = get_movie_pool_from_tmdb(start_movie_id)
        all_movies_to_process = [start_movie_data] + movie_pool_from_tmdb
        
        with driver.session() as session:
            for movie in all_movies_to_process:
                enriched_movie = process_movie_data(movie)
                session.write_transaction(create_movie_in_neo4j, enriched_movie)
        print(f"--- Grafo populado com {len(all_movies_to_process)} filmes ---")
    except requests.exceptions.RequestException as e:
        raise HTTPException(status_code=503, detail=f"Erro de comunicação com TMDB: {e}")
    
    # ETAPA 2: Ler do Neo4j para obter candidatos a recomendação
    with driver.session() as session:
        result = session.run("""
            MATCH (start:Movie {tmdbId: $start_id})
            OPTIONAL MATCH (start)<-[:DIRECTED]-(p:Person)-[:DIRECTED]->(rec_d:Movie)
            OPTIONAL MATCH (start)-[:HAS_GENRE]->(g:Genre)<-[:HAS_GENRE]-(rec_g:Movie)
            WITH start, collect(DISTINCT rec_d) + collect(DISTINCT rec_g) as recommendations
            UNWIND recommendations as rec
            WITH start, rec
            WHERE rec IS NOT NULL AND start <> rec
            RETURN DISTINCT rec.tmdbId as id, rec.title as title
            LIMIT 100
        """, start_id=start_movie_id)
        movie_pool_from_neo4j = [dict(record) for record in result]
    
    if not movie_pool_from_neo4j:
        raise HTTPException(status_code=404, detail="Não foram encontradas recomendações conectadas no grafo.")
    
    # ETAPA 3: "Hidratar" os candidatos com dados completos do TMDB para o A*
    hydrated_movie_pool = []
    for movie_stub in movie_pool_from_neo4j:
        details = find_movie_by_title(movie_stub['title']) # Re-busca pelo título para ter todos os dados
        if details:
            hydrated_movie_pool.append(process_movie_data(details))
            
    # Adiciona o filme inicial à lista hidratada
    processed_searched_movie = process_movie_data(start_movie_data)
    if not any(m.get('id') == start_movie_id for m in hydrated_movie_pool):
        hydrated_movie_pool.append(processed_searched_movie)
    
    # ETAPA 4: Construir o grafo em memória e rodar o A*
    graph = build_graph(hydrated_movie_pool)
    if start_movie_id not in graph:
        raise HTTPException(status_code=404, detail="Filme inicial não pôde ser processado no grafo.")

    recommendations_with_cost = []
    for movie_id in graph:
        if movie_id != start_movie_id:
            path, cost = a_star_search(graph, start_movie_id, movie_id)
            if path:
                recommendations_with_cost.append({"id": movie_id, "cost": cost})

    # ETAPA 5: Preparar a resposta final para o frontend
    sorted_recommendations = sorted(recommendations_with_cost, key=lambda x: x["cost"])
    top_recommendation_ids = {rec["id"] for rec in sorted_recommendations[:12]}
    
    # Filtra a lista de filmes JÁ HIDRATADA para pegar apenas os vencedores
    final_recommendations = [movie for movie in hydrated_movie_pool if movie.get("id") in top_recommendation_ids]
    
    return {"searched_movie": processed_searched_movie, "recommendations": final_recommendations}
