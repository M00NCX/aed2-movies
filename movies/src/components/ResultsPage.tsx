import React, { useState, useEffect } from 'react';
import type { RecommendationResponse, Movie } from '../types/movie';

import FilterBar from '../components/FilterBar';
import MovieCard from '../components/MovieCard';

interface ResultsPageProps {
  data: RecommendationResponse;
  onGoBack: () => void;
}

const ResultsPage: React.FC<ResultsPageProps> = ({ data, onGoBack }) => {
  const [filteredMovies, setFilteredMovies] = useState<Movie[]>(
    data.recommendations
  );
  const [selectedGenre, setSelectedGenre] = useState('all');

  const availableGenres = Array.from(
    new Set(data.recommendations.flatMap((movie) => movie.genre || []))
  );

  useEffect(() => {
    if (selectedGenre === 'all') {
      setFilteredMovies(data.recommendations);
    } else {
      const newFilteredMovies = data.recommendations.filter((movie) =>
        movie.genre?.includes(selectedGenre)
      );
      setFilteredMovies(newFilteredMovies);
    }
  }, [selectedGenre, data.recommendations]);

  return (
    <div className="w-full max-w-7xl mx-auto px-4">
      <div className="flex justify-between items-center my-4">
        <h2 className="text-3xl font-bold text-gray-800">
          Filmes similares a{' '}
          <span className="text-purple-600">{data.searched_movie.title}</span>
        </h2>
        <button
          onClick={onGoBack}
          className="px-4 py-2 bg-purple-100 text-purple-700 font-semibold rounded-lg hover:bg-purple-200"
        >
          ← Nova Busca
        </button>
      </div>

      <FilterBar genres={availableGenres} onGenreChange={setSelectedGenre} />

      {filteredMovies.length > 0 ? (
        <div className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 lg:grid-cols-5 xl:grid-cols-6 gap-6">
          {filteredMovies.map((movie) => (
            <MovieCard key={movie.id} movie={movie} />
          ))}
        </div>
      ) : (
        <p className="text-center text-gray-500 mt-8">
          Nenhum filme encontrado com o filtro selecionado.
        </p>
      )}
    </div>
  );
};

export default ResultsPage;
