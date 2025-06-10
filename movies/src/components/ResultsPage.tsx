import React, { useState, useEffect, useMemo } from 'react';
import type { RecommendationResponse, Movie } from '../types/movie';
import axios from 'axios';

import { Swiper, SwiperSlide } from 'swiper/react';
import { Grid, Navigation } from 'swiper/modules';
import type { Swiper as SwiperCore } from 'swiper/types';

import 'swiper/css';
import 'swiper/css/grid';
import 'swiper/css/navigation';

import MovieCard from '../components/MovieCard';
import MovieDetailsModal from '../components/MovieDetailsModal';

interface ResultsPageProps {
  data: RecommendationResponse;
  onGoBack: () => void;
}

type Genre = {
  id: number;
  name: string;
};

const ResultsPage: React.FC<ResultsPageProps> = ({ data, onGoBack }) => {
  const [allGenres, setAllGenres] = useState<Genre[]>([]);
  const [selectedGenre, setSelectedGenre] = useState('all');
  const [filteredMovies, setFilteredMovies] = useState<Movie[]>(
    data.recommendations
  );

  const [swiperInstance, setSwiperInstance] = useState<SwiperCore | null>(null);
  const [selectedMovie, setSelectedMovie] = useState<Movie | null>(null);

  const genreCounts = useMemo(() => {
    const counts: { [key: number]: number } = {};
    data.recommendations.forEach((movie) => {
      movie.genre_ids?.forEach((id) => {
        counts[id] = (counts[id] || 0) + 1;
      });
    });
    return counts;
  }, [data.recommendations]);

  useEffect(() => {
    const fetchGenres = async () => {
      try {
        const response = await axios.get('http://127.0.0.1:8000/genres');
        const genresArray = Object.entries(response.data).map(([id, name]) => ({
          id: Number(id),
          name: name as string,
        }));
        setAllGenres(genresArray);
      } catch (error) {
        console.error('Erro ao buscar gêneros:', error);
      }
    };
    fetchGenres();
  }, []);

  useEffect(() => {
    if (selectedGenre === 'all') {
      setFilteredMovies(data.recommendations);
    } else {
      const genreId = Number(selectedGenre);
      const newFilteredList = data.recommendations.filter((movie) =>
        movie.genre_ids?.includes(genreId)
      );
      setFilteredMovies(newFilteredList);
    }
  }, [selectedGenre, data.recommendations]);

  return (
    <>
      <div className="w-full max-w-7xl mx-auto px-4 py-8">
        <div className="flex flex-col md:flex-row justify-between items-center my-4 gap-4">
          <h2 className="text-3xl font-bold text-gray-800 text-center md:text-left">
            Filmes similares a{' '}
            <span className="text-purple-600">{data.searched_movie.title}</span>
          </h2>

          <div className="flex items-center gap-4">
            <div className="flex items-center gap-2">
              <label
                htmlFor="genre-filter"
                className="font-semibold text-gray-700 sr-only"
              >
                Gênero
              </label>
              <select
                id="genre-filter"
                value={selectedGenre}
                onChange={(e) => setSelectedGenre(e.target.value)}
                className="rounded-lg border-gray-300 shadow-sm focus:border-purple-500 focus:ring-purple-500"
              >
                <option value="all">
                  Todos os Gêneros ({data.recommendations.length})
                </option>
                {allGenres
                  .filter((genre) => genreCounts[genre.id])
                  .map((genre) => (
                    <option key={genre.id} value={genre.id}>
                      {genre.name} ({genreCounts[genre.id]})
                    </option>
                  ))}
              </select>
            </div>
            <button
              onClick={onGoBack}
              className="px-4 py-2 bg-purple-100 text-purple-700 font-semibold rounded-lg hover:bg-purple-200"
            >
              ← Nova Busca
            </button>
          </div>
        </div>

        <div className="relative mt-8 min-h-[400px] group">
          {' '}
          <Swiper
            onSwiper={setSwiperInstance}
            modules={[Grid, Navigation]}
            spaceBetween={16}
            className="!py-4 !pb-10 h-full"
            breakpoints={{
              320: {
                slidesPerView: 2,
                slidesPerGroup: 2,
                grid: { rows: 2, fill: 'row' },
              },
              768: {
                slidesPerView: 4,
                slidesPerGroup: 4,
                grid: { rows: 2, fill: 'row' },
              },
              1024: {
                slidesPerView: 6,
                slidesPerGroup: 1,
                grid: { rows: 2, fill: 'row' },
              },
            }}
          >
            {filteredMovies.map((movie) => (
              <SwiperSlide key={movie.id}>
                <MovieCard movie={movie} onClick={setSelectedMovie} />
              </SwiperSlide>
            ))}
          </Swiper>
          {filteredMovies.length === 0 && (
            <div className="absolute inset-0 flex items-center justify-center text-gray-500">
              <p>Nenhum filme encontrado para o gênero selecionado.</p>
            </div>
          )}
          {filteredMovies.length > 0 && (
            <>
              <button
                onClick={() => swiperInstance?.slidePrev()}
                onMouseEnter={() => swiperInstance?.slidePrev()}
                className="absolute top-1/2 left-0 -translate-y-1/2 -translate-x-4 sm:-translate-x-10 z-10 p-2 bg-white/80 rounded-full shadow-lg hover:bg-white transition opacity-0 md:opacity-100 group-hover:opacity-100"
              >
                <svg
                  xmlns="http://www.w3.org/2000/svg"
                  className="h-6 sm:h-8 w-6 sm:w-8 text-gray-800"
                  fill="none"
                  viewBox="0 0 24 24"
                  stroke="currentColor"
                >
                  <path
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    strokeWidth={2}
                    d="M15 19l-7-7 7-7"
                  />
                </svg>
              </button>
              <button
                onClick={() => swiperInstance?.slideNext()}
                onMouseEnter={() => swiperInstance?.slideNext()}
                className="absolute top-1/2 right-0 -translate-y-1/2 translate-x-4 sm:translate-x-10 z-10 p-2 bg-white/80 rounded-full shadow-lg hover:bg-white transition opacity-0 md:opacity-100 group-hover:opacity-100"
              >
                <svg
                  xmlns="http://www.w3.org/2000/svg"
                  className="h-6 sm:h-8 w-6 sm:w-8 text-gray-800"
                  fill="none"
                  viewBox="0 0 24 24"
                  stroke="currentColor"
                >
                  <path
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    strokeWidth={2}
                    d="M9 5l7 7-7 7"
                  />
                </svg>
              </button>
            </>
          )}
        </div>
      </div>

      {selectedMovie && (
        <MovieDetailsModal
          movie={selectedMovie}
          onClose={() => setSelectedMovie(null)}
        />
      )}
    </>
  );
};

export default ResultsPage;
