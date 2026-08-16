import api from './api';

const sessionService = {
  getAll: async () => {
    const response = await api.get('/sessions/');
    return response.data;
  },
  getById: async (id) => {
    const response = await api.get(`/sessions/${id}/`);
    return response.data;
  },
  create: async (data) => {
    const response = await api.post('/sessions/', data);
    return response.data;
  },
  start: async (id) => {
    const response = await api.post(`/sessions/${id}/start/`);
    return response.data;
  },
  end: async (id) => {
    const response = await api.post(`/sessions/${id}/end/`);
    return response.data;
  },
  getAttendance: async (id) => {
    const response = await api.get(`/sessions/${id}/attendance/`);
    return response.data;
  },
  getStatus: async (id) => {
    const response = await api.get(`/sessions/${id}/status/`);
    return response.data;
  }
};

export default sessionService;
