import api from './api';

const studentService = {
  getAll: async () => {
    const response = await api.get('/students/');
    return response.data;
  },
  create: async (data) => {
    const response = await api.post('/students/', data);
    return response.data;
  },
  registerFace: async (id, formData) => {
    const response = await api.post(`/students/${id}/register-face/`, formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    });
    return response.data;
  }
};

export default studentService;
