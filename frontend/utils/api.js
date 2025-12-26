import axios from 'axios';

const API_BASE_URL = 'http://localhost:5000/api';

// Create axios instance
const api = axios.create({
  baseURL: API_BASE_URL,
  timeout: 10000,
});

// Request interceptor to add auth token
api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// Response interceptor to handle errors
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      localStorage.removeItem('token');
      localStorage.removeItem('user');
      window.location.href = '/login';
    }
    return Promise.reject(error);
  }
);

export const authAPI = {
  login: (credentials) => api.post('/login', credentials),
  register: (userData) => api.post('/register', userData),
};

export const recommendationAPI = {
  getRecommendations: (data) => api.post('/recommendations', data),
  getEnhancedRecommendations: (data) => api.post('/enhanced-recommendations', data),
};

export const reviewAPI = {
  getReviews: () => api.get('/reviews'),
  createReview: (data) => api.post('/reviews', data),
};

export const ratingAPI = {
  submitRating: (data) => api.post('/ratings', data),
  getUserRatings: () => api.get('/user/ratings'),
};

export const healthAPI = {
  check: () => api.get('/health'),
};

export default api;