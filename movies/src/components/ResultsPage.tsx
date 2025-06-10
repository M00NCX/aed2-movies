import React, { useState } from 'react';
import type { RecommendationResponse, Movie } from '../types/movie';

import { Swiper, SwiperSlide } from 'swiper/react';
import { Grid, Navigation } from 'swiper/modules';
import type { Swiper as SwiperCore } from 'swiper/types';

import 'swiper/css';
import 'swiper/css/grid';
import 'swiper/css/navigation';

import MovieCard from '../components/MovieCard';

interface ResultsPageProps {
  data: RecommendationResponse;
  onGoBack: () => void;
}

const ResultsPage: React.FC<ResultsPageProps> = ({ data, onGoBack }) => {
  const movies = data.recommendations;
  const [swiperInstance, setSwiperInstance] = useState<SwiperCore | null>(null);

  return (
    <div className="w-full max-w-7xl mx-auto px-4 py-8">
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

      <div className="relative mt-8">
        <Swiper
          onSwiper={setSwiperInstance}
          modules={[Grid, Navigation]}
          spaceBetween={16}
          className="!py-4 !pb-10"
          breakpoints={{
            320: {
              slidesPerView: 2,
              slidesPerGroup: 2,
              grid: {
                rows: 2,
                fill: 'row',
              },
            },

            768: {
              slidesPerView: 4,
              slidesPerGroup: 4,
              grid: {
                rows: 2,
                fill: 'row',
              },
            },

            1024: {
              slidesPerView: 6,
              slidesPerGroup: 1,
              grid: {
                rows: 2,
                fill: 'row',
              },
            },
          }}
        >
          {movies.map((movie) => (
            <SwiperSlide key={movie.id}>
              {/* O MovieCard não precisa de alterações */}
              <MovieCard movie={movie} />
            </SwiperSlide>
          ))}
        </Swiper>

        <button
          onClick={() => swiperInstance?.slidePrev()}
          onMouseEnter={() => swiperInstance?.slidePrev()}
          className="absolute top-1/2 left-0 -translate-y-1/2 -translate-x-4 sm:-translate-x-10 z-10 p-2 bg-white/80 rounded-full shadow-lg hover:bg-white transition opacity-0 sm:opacity-100 group-hover:opacity-100"
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
          className="absolute top-1/2 right-0 -translate-y-1/2 translate-x-4 sm:translate-x-10 z-10 p-2 bg-white/80 rounded-full shadow-lg hover:bg-white transition opacity-0 sm:opacity-100 group-hover:opacity-100"
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
      </div>
    </div>
  );
};

export default ResultsPage;
