import React from 'react';
import type { Movie } from '../types/movie';

interface ModalProps {
  movie: Movie;
  onClose: () => void;
}

const MovieDetailsModal: React.FC<ModalProps> = ({ movie, onClose }) => {
  const handlePanelClick = (e: React.MouseEvent) => {
    e.stopPropagation();
  };

  const imageUrl = movie.poster_path
    ? `https://image.tmdb.org/t/p/w500${movie.poster_path}`
    : 'https://via.placeholder.com/500x750?text=No+Image';

  return (
    <div
      onClick={onClose}
      className="fixed inset-0 bg-black/70 flex items-center justify-center z-50 p-4 transition-opacity duration-300"
    >
      <div
        onClick={handlePanelClick}
        className="bg-white rounded-lg shadow-2xl w-full max-w-4xl max-h-[90vh] flex flex-col md:flex-row overflow-hidden"
      >
        <img
          src={imageUrl}
          alt={`Pôster de ${movie.title}`}
          className="w-full md:w-1/3 object-cover"
        />

        <div className="w-full md:w-2/3 p-6 flex flex-col overflow-y-auto">
          <div className="flex justify-between items-start mb-4">
            <h2 className="text-3xl font-bold text-gray-800">{movie.title}</h2>
            <button
              onClick={onClose}
              className="text-gray-500 hover:text-gray-800"
            >
              &times;
            </button>
          </div>

          <div className="flex flex-wrap items-center gap-x-4 gap-y-1 text-sm text-gray-600 mb-4">
            <span>{movie.release_date?.split('-')[0]}</span>
            <span className="text-gray-300">|</span>
            <span>
              Diretor:{' '}
              <span className="font-semibold">{movie.director || 'N/A'}</span>
            </span>
          </div>

          <div className="flex-1">
            <h3 className="text-lg font-semibold mb-2 text-gray-700">
              Sinopse
            </h3>
            <p className="text-gray-700 leading-relaxed">
              {movie.overview || 'Sinopse não disponível.'}
            </p>
          </div>

          {(movie.vote_average || 0) > 0 && (
            <div className="mt-6 flex items-center gap-2">
              <span className="text-yellow-500 text-2xl" title="Nota Média">
                ⭐
              </span>
              <span className="text-2xl font-bold text-gray-800">
                {(movie.vote_average || 0).toFixed(1)}
              </span>
              <span className="text-gray-500">/ 10</span>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default MovieDetailsModal;
