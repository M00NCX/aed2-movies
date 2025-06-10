# src/a_star_logic.py

from typing import List, Dict, Tuple, Optional
import heapq
import itertools

class MovieNode:
    """Representa um filme como um nó no nosso grafo."""
    def __init__(self, movie: Dict):
        self.id = movie["id"]
        self.title = movie["title"]
        self.genres = movie.get("genre_ids", [])
        self.popularity = movie.get("popularity", 0)
        self.director = movie.get("director", None)
        self.neighbors: List[Tuple["MovieNode", float]] = []

def build_graph(movies: List[Dict]) -> Dict[int, MovieNode]:
    """Constrói o grafo de filmes com conexões baseadas em gêneros."""
    graph = {}
    for movie in movies:
        node = MovieNode(movie)
        graph[node.id] = node

    # Conecta filmes com base na similaridade de gêneros
    for node in graph.values():
        for other in graph.values():
            if node.id != other.id:
                shared_genres = len(set(node.genres) & set(other.genres))
                if shared_genres > 0:
                    weight = 1 / shared_genres  # Custo é o inverso da similaridade
                    node.neighbors.append((other, weight))
    return graph

def heuristic(node: MovieNode, goal_node: MovieNode) -> float:
    """Estima o 'custo' de ir do 'node' atual até o 'goal_node'."""
    # Custo base pela similaridade de gênero
    shared_genres = len(set(node.genres) & set(goal_node.genres))
    genre_cost = 1 / (shared_genres + 1)

    # Penalidade por diretor diferente
    DIRECTOR_MISMATCH_PENALTY = 0.5
    penalty = 0.0
    if node.director and goal_node.director and node.director != goal_node.director:
        penalty = DIRECTOR_MISMATCH_PENALTY
        
    return genre_cost + penalty

def a_star_search(graph: Dict[int, MovieNode], start_id: int, goal_id: int) -> Tuple[Optional[List[int]], float]:
    """
    Executa o algoritmo A* para encontrar o caminho de menor custo.
    Retorna o caminho e o custo total (g_score).
    """
    counter = itertools.count()
    open_set = []
    heapq.heappush(open_set, (0, next(counter), graph[start_id]))
    
    came_from = {}
    g_score = {node_id: float('inf') for node_id in graph}
    g_score[start_id] = 0

    while open_set:
        _, _, current = heapq.heappop(open_set)

        if current.id == goal_id:
            path = [current.id]
            while current.id in came_from:
                current = came_from[current.id]
                path.append(current.id)
            # Retorna o caminho e o custo final para chegar ao objetivo
            return path[::-1], g_score[goal_id]

        for neighbor, weight in current.neighbors:
            tentative_g_score = g_score[current.id] + weight
            if tentative_g_score < g_score.get(neighbor.id, float('inf')):
                came_from[neighbor.id] = current
                g_score[neighbor.id] = tentative_g_score
                f_score = tentative_g_score + heuristic(neighbor, graph[goal_id])
                heapq.heappush(open_set, (f_score, next(counter), neighbor))
                
    return None, float('inf') # Retorna None se não encontrar caminho
