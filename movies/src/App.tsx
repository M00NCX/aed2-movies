import React, { useState } from 'react';
import axios from 'axios';

import Header from './components/Header';
import SearchBar from './components/SearchBar';

import type { RecommendationResponse } from './types/movie';

const App: React.FC = () => {
  const [results, setResults] = useState<RecommendationResponse | null>(null);
  const [isLoading, setIsLoading] = useState<boolean>(false);
  const [error, setError] = useState<string | null>(null);

  const handleSearch = async (query: string) => {
    if (!query) return;

    setIsLoading(true);
    setError(null);
    setResults(null);
    //aqui foi a ia que disse pra colocar a busca quando for integrar com python no back
    try {
      const apiUrl = `http://127.0.0.1:8000/recommendations/${query}`;
      const response = await axios.get<RecommendationResponse>(apiUrl);
      setResults(response.data);
    } catch (err) {
      console.error('Erro ao buscar recomendações:', err);
      setError(
        'Não foi possível encontrar o filme ou obter recomendações. Tente novamente.'
      );
    } finally {
      setIsLoading(false);
    }
  };

  const handleGoBack = () => {
    setResults(null);
    setError(null);
  };

  return (
    <div className="h-screen bg-pink-50 flex flex-col overflow-hidden">
      <Header />

      <main className="flex-1 container mx-auto flex flex-col justify-center items-center p-4">
        {!results && !isLoading && !error && (
          <div className="w-full max-w-5xl flex flex-col items-center justify-center gap-10 ">
            <div className="text-center">
              <h2 className="text-xl font-semibold text-gray-600">
                Projeto algoritmos e estruturas de dados
              </h2>
              <h1 className="mt-2 text-4xl md:text-5xl font-extrabold text-gray-800 leading-tight">
                Encontre filmes similares com <br />
                <span className="text-purple-600">algoritmos inteligentes</span>
              </h1>
            </div>

            <div className="w-full flex flex-col md:flex-row items-center justify-center gap-8">
              <div className="w-full md:w-1/2 flex justify-center md:justify-end">
                <SearchBar onSearch={handleSearch} isLoading={isLoading} />
              </div>
              <div className="hidden md:flex w-full md:w-1/2 justify-end">
                <img src="/home.png" alt="home" width={400} />
              </div>
            </div>
          </div>
        )}
        // abaixo também foi a ia
        {isLoading && (
          <div className="text-center">
            <p className="text-xl font-semibold text-purple-600">
              Buscando recomendações...
            </p>
          </div>
        )}
        {error && !isLoading && (
          <div className="text-center">
            <p className="text-xl font-semibold text-red-500">{error}</p>
            <button
              onClick={handleGoBack}
              className="mt-4 px-4 py-2 bg-purple-600 text-white rounded-lg hover:bg-purple-700"
            >
              Tentar Novamente
            </button>
          </div>
        )}
        {results && (
          <div className="w-full max-w-6xl flex flex-col h-full py-4">
            <div className="flex justify-between items-center mb-4 px-2">
              <h2 className="text-2xl font-bold text-gray-800">
                Recomendações para{' '}
                <span className="text-purple-600">
                  {results.searched_movie.title}
                </span>
              </h2>
              <button
                onClick={handleGoBack}
                className="px-4 py-2 bg-purple-100 text-purple-700 font-semibold rounded-lg hover:bg-purple-200"
              >
                ← Nova Busca
              </button>
            </div>

            <div className="flex-1 grid grid-cols-2 md:grid-cols-4 lg:grid-cols-5 gap-4 overflow-y-auto pr-2">
              {results.recommendations.map((movie) => (
                <div
                  key={movie.id}
                  className="bg-white p-2 rounded-lg shadow transition-transform hover:scale-105"
                >
                  <img
                    src={`https://image.tmdb.org/t/p/w500${movie.poster_path}`}
                    alt={movie.title}
                    className="rounded-md w-full object-cover"
                  />
                  <h3 className="font-bold mt-2 text-sm text-gray-800 truncate">
                    {movie.title}
                  </h3>
                </div>
              ))}
            </div>
          </div>
        )}
      </main>
    </div>
  );
};

export default App;
