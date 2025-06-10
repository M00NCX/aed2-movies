import React from 'react';
import type { Movie } from '../types/movie';

interface MovieCardProps {
  movie: Movie;
}

const MovieCard: React.FC<MovieCardProps> = ({ movie }) => {
  const imageUrl = movie.poster_path
    ? `https://image.tmdb.org/t/p/w500${movie.poster_path}`
    : 'https://via.placeholder.com/500x750?text=No+Image';

  return (
    <div
      className="group relative cursor-pointer overflow-hidden rounded-lg shadow-md
                   transition-all duration-300 ease-in-out
                   hover:scale-105 hover:shadow-xl hover:shadow-purple-400/30 
                   hover:ring-2 hover:ring-purple-500"
    >
      <img
        src={imageUrl}
        alt={`Pôster de ${movie.title}`}
        className="w-full h-full object-cover transition-transform duration-300 ease-in-out group-hover:scale-110"
      />

      <div className="absolute inset-0 bg-black bg-opacity-0 group-hover:bg-opacity-60 transition-all duration-300"></div>

      <div className="absolute bottom-0 left-0 p-4 opacity-0 group-hover:opacity-100 transition-opacity duration-300">
        <h3 className="text-white font-bold text-lg">{movie.title}</h3>
      </div>
    </div>
  );
};

export default MovieCard;
