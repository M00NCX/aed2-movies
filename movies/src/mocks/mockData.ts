// src/mocks/mockData.ts
import type { RecommendationResponse } from '../types/movie';

// Lembre-se de adicionar 'genre' e 'director' à sua interface Movie em 'src/types/movie.ts'
// export interface Movie {
//   ...
//   genre?: string[];
//   director?: string;
// }

export const mockApiResponse: RecommendationResponse = {
  // O filme que o usuário "pesquisou"
  searched_movie: {
    id: 1,
    title: 'O Filme Pesquisado',
    overview: 'Um filme incrível que serve de base para as recomendações.',
    poster_path: '/9Gg1JEVuzmJvVT5d7P2aC3TDC4i.jpg', // Poster de "A Origem"
    release_date: '2010-07-15',
    vote_average: 8.8,
    genre: ['Ação', 'Ficção Científica'],
    director: 'Christopher Nolan',
  },
  // A lista de filmes recomendados
  recommendations: [
    {
      id: 27205,
      title: 'A Origem',
      poster_path: '/9Gg1JEVuzmJvVT5d7P2aC3TDC4i.jpg',
      overview: '',
      release_date: '',
      vote_average: 0,
      genre: ['Ação', 'Ficção Científica'],
      director: 'Christopher Nolan',
    },
    {
      id: 157336,
      title: 'Interestelar',
      poster_path: '/nCbkIeFMDvO6k_nL9T00I2i1Mbi.jpg',
      overview: '',
      release_date: '',
      vote_average: 0,
      genre: ['Aventura', 'Ficção Científica'],
      director: 'Christopher Nolan',
    },
    {
      id: 155,
      title: 'Batman: O Cavaleiro Das Trevas',
      poster_path: '/8QDQExnfN0w4unM_f2i5N2FFa4T.jpg',
      overview: '',
      release_date: '',
      vote_average: 0,
      genre: ['Ação', 'Drama'],
      director: 'Christopher Nolan',
    },
    {
      id: 680,
      title: 'Pulp Fiction: Tempo de Violência',
      poster_path: '/602Nl0zZp3BvWqitg1N6yrw5d2Y.jpg',
      overview: '',
      release_date: '',
      vote_average: 0,
      genre: ['Suspense', 'Crime'],
      director: 'Quentin Tarantino',
    },
    {
      id: 496243,
      title: 'Parasita',
      poster_path: '/igw938inbvl0aG21ob5fS4C324i.jpg',
      overview: '',
      release_date: '',
      vote_average: 0,
      genre: ['Suspense', 'Drama'],
      director: 'Bong Joon Ho',
    },
    {
      id: 13,
      title: 'Forrest Gump: O Contador de Histórias',
      poster_path: '/pcgHFa5hL0KAa2sXm2A2s9yv5N5.jpg',
      overview: '',
      release_date: '',
      vote_average: 0,
      genre: ['Comédia', 'Drama'],
      director: 'Robert Zemeckis',
    },
    {
      id: 634649,
      title: 'Homem-Aranha: Sem Volta para Casa',
      poster_path: '/fVzXp3NwovUlC5CiE0BTLBwLhkw.jpg',
      overview: '',
      release_date: '',
      vote_average: 0,
      genre: ['Ação', 'Aventura'],
      director: 'Jon Watts',
    },
    {
      id: 299534,
      title: 'Vingadores: Ultimato',
      poster_path: '/q6725aR8Zs4IwGMXzZT8aC8j4bV.jpg',
      overview: '',
      release_date: '',
      vote_average: 0,
      genre: ['Ação', 'Aventura'],
      director: 'Anthony & Joe Russo',
    },
  ],
};
