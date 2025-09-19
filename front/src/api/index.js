import axios from 'axios';
const API_BASE = 'http://localhost:3000/api'; //process.env.REACT_APP_API_BASE_URL 

const api = axios.create({
  baseURL: API_BASE,
});

api.interceptors.request.use(cfg => {
  const token = localStorage.getItem('tp_token');
  if (token) cfg.headers.Authorization = 'Bearer ' + token;
  return cfg;
});

export default api;
