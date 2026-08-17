import axios from 'axios';

const api = axios.create({
  baseURL: 'http://localhost:8000/api',
});

// Add interceptor to include token
api.interceptors.request.use((config) => {
  const token = localStorage.getItem('access_token');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

export const reportService = {
  getDashboard: async () => {
    const response = await api.get('/reports/dashboard/');
    return response.data;
  },
  
  getSessionReport: async (id) => {
    const response = await api.get(`/reports/sessions/${id}/`);
    return response.data;
  },
  
  getStudentAnalytics: async (id) => {
    const response = await api.get(`/reports/students/${id}/`);
    return response.data;
  },
  
  getHistory: async (params) => {
    const response = await api.get('/reports/history/', { params });
    return response.data;
  },
  
  getLowAttendance: async () => {
    const response = await api.get('/reports/low-attendance/');
    return response.data;
  },
  
  // For export, we need a special approach to trigger file download
  exportSessionCSV: async (id) => {
    const response = await api.get(`/reports/sessions/${id}/export/`, {
      responseType: 'blob'
    });
    
    // Create a temporary link to download the file
    const url = window.URL.createObjectURL(new Blob([response.data]));
    const link = document.createElement('a');
    link.href = url;
    
    // Extract filename from content-disposition header if available
    const contentDisposition = response.headers['content-disposition'];
    let filename = `session_${id}_export.csv`;
    if (contentDisposition) {
      const filenameMatch = contentDisposition.match(/filename="?([^"]+)"?/);
      if (filenameMatch && filenameMatch.length === 2) {
        filename = filenameMatch[1];
      }
    }
    
    link.setAttribute('download', filename);
    document.body.appendChild(link);
    link.click();
    link.parentNode.removeChild(link);
  }
};
