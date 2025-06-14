export interface Movie {
  genre_ids: any;
  popularity: number;
  genre: string[];
  id: number;
  title: string;
  overview: string;
  poster_path: string;
  release_date: string;
  vote_average: number;
  director: string;
}

export interface RecommendationResponse {
  searched_movie: Movie;
  recommendations: Movie[];
}
