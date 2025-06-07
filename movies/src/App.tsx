import React, { useState } from 'react';
import axios from 'axios';

import Header from './components/Header';
import SearchBar from './components/SearchBar';

import type { RecommendationResponse } from './/types/movie';

const App: React.FC = () => {
  // Tipando os estados com useState
  const [results, setResults] = useState<RecommendationResponse | null>(null);
  const [isLoading, setIsLoading] = useState<boolean>(false);
  const [error, setError] = useState<string | null>(null);

  const handleSearch = async (query: string) => {
    if (!query) return;

    setIsLoading(true);
    setError(null);
    setResults(null);

    try {
      // A URL da sua API FastAPI
      const apiUrl = `http://127.0.0.1:8000/recommendations/${query}`;

      // Informamos ao axios o tipo de resposta esperado
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

  return (
    <div className="min-h-screen bg-pink-50">
      <Header />
      <main className="container mx-auto px-4 py-16 flex flex-col items-center justify-center gap-12">
        <div className="text-center w-full max-w-2xl">
          <h2 className="text-xl font-semibold text-gray-600">
            Projeto algoritmos e estruturas de dados
          </h2>
          <h1 className="mt-2 text-4xl md:text-5xl font-extrabold text-gray-800 leading-tight">
            Encontre <span className="text-purple-600">filmes similares</span>{' '}
            com algoritmos inteligentes
          </h1>
          <div className="mt-8 mx-auto">
            <SearchBar onSearch={handleSearch} isLoading={isLoading} />
          </div>
        </div>

        {/* Área de Resultados */}
        <div className="w-full max-w-4xl mt-8">
          {error && <p className="text-center text-red-500">{error}</p>}

          {/* Aqui você renderizaria os resultados */}
          {results && (
            <div>
              <h2 className="text-2xl font-bold text-center">
                Recomendações para{' '}
                <span className="text-purple-600">
                  {results.searched_movie.title}
                </span>
              </h2>
              {/* Crie um componente MovieCard para mostrar cada filme */}
              <div className="grid grid-cols-2 md:grid-cols-4 lg:grid-cols-5 gap-4 mt-6">
                {results.recommendations.map((movie) => (
                  <div
                    key={movie.id}
                    className="bg-white p-2 rounded-lg shadow"
                  >
                    <img
                      src={`https://image.tmdb.org/t/p/w500${movie.poster_path}`}
                      alt={movie.title}
                      className="rounded-md"
                    />
                    <h3 className="font-bold mt-2 text-sm">{movie.title}</h3>
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>
      </main>
    </div>
  );
};

export default App;
