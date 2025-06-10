import React from 'react';

interface FilterBarProps {
  genres: string[];
  onGenreChange: (genre: string) => void;
}

const FilterBar: React.FC<FilterBarProps> = ({ genres, onGenreChange }) => {
  return (
    <div className="flex items-center justify-center gap-4 my-6">
      <div className="flex items-center gap-2">
        <label htmlFor="genre-select" className="font-semibold text-gray-600">
          Gênero:
        </label>
        <select
          id="genre-select"
          onChange={(e) => onGenreChange(e.target.value)}
          className="rounded-lg border-gray-300 shadow-sm focus:border-purple-500 focus:ring-purple-500"
        >
          <option value="all">Todos</option>
          {genres.map((genre) => (
            <option key={genre} value={genre}>
              {genre}
            </option>
          ))}
        </select>
      </div>

      {
        <div className="flex items-center gap-2">
          <label
            htmlFor="director-select"
            className="font-semibold text-gray-600"
          >
            Diretor:
          </label>
          <select id="director-select" className="...">
            <option value="all">Todos</option>
            <option value="Christopher Nolan">Christopher Nolan</option>
          </select>
        </div>
      }
    </div>
  );
};

export default FilterBar;
