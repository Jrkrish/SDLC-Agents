import axios from 'axios';

// API Base URL - adjust this to match your FastAPI server
const API_BASE_URL = 'http://localhost:8000';

// Create axios instance with default configuration
const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Request interceptor to add auth headers if needed
api.interceptors.request.use(
  (config) => {
    // Add auth token if available
    const token = localStorage.getItem('auth_token');
    if (token && config.headers) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// Response interceptor for error handling
api.interceptors.response.use(
  (response) => {
    return response;
  },
  (error) => {
    console.error('API Error:', error);
    return Promise.reject(error);
  }
);

// API Types based on your FastAPI models
export interface SDLCRequest {
  project_name?: string;
  task_id?: string;
  requirements?: string;
  status?: string;
  feedback?: string;
  next_node?: string;
}

export interface SDLCResponse {
  status: string;
  message: string;
  task_id?: string;
  state?: any;
  error?: string;
}

// API Service functions
export const apiService = {
  // Health check
  async healthCheck(): Promise<any> {
    const response = await api.get<any>('/');
    return response.data;
  },

  // Start SDLC process
  async startSDLC(projectName: string): Promise<SDLCResponse> {
    const response = await api.post<SDLCResponse>('/api/v1/sdlc/start', {
      project_name: projectName
    });
    return response.data;
  },

  // Generate user stories
  async generateUserStories(taskId: string, requirements: string): Promise<SDLCResponse> {
    const response = await api.post<SDLCResponse>('/api/v1/sdlc/user_stories', {
      task_id: taskId,
      requirements: requirements
    });
    return response.data;
  },

  // Progress the flow to next step
  async progressFlow(
    taskId: string, 
    status: string, 
    feedback: string, 
    nextNode: string
  ): Promise<SDLCResponse> {
    const response = await api.post<SDLCResponse>('/api/v1/sdlc/progress_flow', {
      task_id: taskId,
      status: status,
      feedback: feedback,
      next_node: nextNode
    });
    return response.data;
  }
};

export default apiService;
