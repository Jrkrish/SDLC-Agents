import axios from 'axios';

// API Base URL - FastAPI server
const API_BASE_URL = 'http://localhost:8000';

// Create axios instance with enhanced configuration
const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
  timeout: 300000, // 5 minutes timeout for long-running operations
});

// Request interceptor
api.interceptors.request.use(
  (config: any) => {
    // Add auth token if available
    const token = localStorage.getItem('auth_token');
    if (token && config.headers) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    
    // Add request timestamp for tracking
    if (config.data) {
      config.data.timestamp = new Date().toISOString();
    }
    
    console.log(`🚀 API Request: ${config.method?.toUpperCase()} ${config.url}`);
    return config;
  },
  (error: any) => Promise.reject(error)
);

// Response interceptor
api.interceptors.response.use(
  (response: any) => {
    console.log(`✅ API Response: ${response.status} ${response.config.url}`);
    return response;
  },
  (error: any) => {
    console.error('❌ API Error:', error.response?.data || error.message);
    return Promise.reject(error);
  }
);

// Enhanced Types for Autonomous SDLC
export interface ConnectorConfig {
  name: string;
  enabled: boolean;
  api_key: string;
  base_url?: string;
  username?: string;
  [key: string]: any;
}

export interface ConnectorConfigs {
  github?: ConnectorConfig;
  jira?: ConnectorConfig;
  slack?: ConnectorConfig;
}

export interface AutonomousStartRequest {
  project_name: string;
  fully_autonomous?: boolean;
  connector_configs?: ConnectorConfigs;
  ai_model?: string;
}

export interface AutonomousResponse {
  success: boolean;
  task_id?: string;
  state?: any;
  autonomous_insights?: {
    autonomous_recommendations: any;
    execution_summary: any;
    agent_status: any;
    connector_health: any;
  };
  error?: string;
  status?: string;
  message?: string;
  completion_percentage?: number;
  current_phase?: string;
}

export interface AgentStatus {
  agent_name: string;
  active: boolean;
  decisions_made: number;
  capabilities: string[];
  last_activity?: string;
}

export interface ConnectorStatus {
  name: string;
  type: string;
  status: 'connected' | 'disconnected' | 'error';
  last_error?: string;
  connection_time?: string;
}

export interface ExecutionSummary {
  task_id: string;
  project_name: string;
  started_at: string;
  completion_percentage: number;
  autonomous_mode: boolean;
  agent_summary: {
    total_phases_executed: number;
    total_agents_executed: number;
    success_rate: number;
    active_agents: number;
    agent_status: Record<string, AgentStatus>;
  };
  phases_completed: string[];
}

// Enhanced API Service for Autonomous SDLC
export const autonomousApiService = {
  // Health check
  async healthCheck(): Promise<any> {
    const response = await api.get('/health');
    return response.data;
  },

  // Start autonomous SDLC workflow
  async startAutonomousSDLC(request: AutonomousStartRequest): Promise<AutonomousResponse> {
    console.log('🤖 Starting autonomous SDLC workflow...', request);
    const response = await api.post<AutonomousResponse>('/api/v1/autonomous/start', request);
    return response.data;
  },

  // Continue autonomous workflow with user input
  async continueAutonomousWorkflow(taskId: string, userInput?: any): Promise<AutonomousResponse> {
    console.log('🔄 Continuing autonomous workflow...', { taskId, userInput });
    const response = await api.post<AutonomousResponse>('/api/v1/autonomous/continue', {
      task_id: taskId,
      user_input: userInput
    });
    return response.data;
  },

  // Handle feedback in autonomous workflow
  async handleAutonomousFeedback(
    taskId: string, 
    feedback: string, 
    reviewType: string
  ): Promise<AutonomousResponse> {
    console.log('💬 Handling autonomous feedback...', { taskId, reviewType });
    const response = await api.post<AutonomousResponse>('/api/v1/autonomous/feedback', {
      task_id: taskId,
      feedback,
      review_type: reviewType
    });
    return response.data;
  },

  // Approve autonomous stage
  async approveAutonomousStage(taskId: string, reviewType: string): Promise<AutonomousResponse> {
    console.log('✅ Approving autonomous stage...', { taskId, reviewType });
    const response = await api.post<AutonomousResponse>('/api/v1/autonomous/approve', {
      task_id: taskId,
      review_type: reviewType
    });
    return response.data;
  },

  // Get autonomous workflow status
  async getAutonomousStatus(taskId: string): Promise<AutonomousResponse> {
    const response = await api.get<AutonomousResponse>(`/api/v1/autonomous/status/${taskId}`);
    return response.data;
  },

  // Get execution summary
  async getExecutionSummary(taskId: string): Promise<ExecutionSummary> {
    console.log('📊 Getting execution summary...', { taskId });
    const response = await api.get<ExecutionSummary>(`/api/v1/autonomous/summary/${taskId}`);
    return response.data;
  },

  // Get agent status
  async getAgentStatus(taskId?: string): Promise<Record<string, AgentStatus>> {
    const url = taskId ? `/api/v1/agents/status/${taskId}` : '/api/v1/agents/status';
    const response = await api.get<Record<string, AgentStatus>>(url);
    return response.data;
  },

  // Get connector status
  async getConnectorStatus(): Promise<Record<string, ConnectorStatus>> {
    console.log('🔗 Getting connector status...');
    const response = await api.get<Record<string, ConnectorStatus>>('/api/v1/connectors/status');
    return response.data;
  },

  // Initialize connectors
  async initializeConnectors(connectorConfigs: ConnectorConfigs): Promise<any> {
    console.log('🔧 Initializing connectors...', connectorConfigs);
    const response = await api.post('/api/v1/connectors/initialize', connectorConfigs);
    return response.data;
  },

  // Test connectors
  async testConnectors(): Promise<any> {
    console.log('🧪 Testing connectors...');
    const response = await api.post('/api/v1/connectors/test');
    return response.data;
  },

  // Get available AI models
  async getAvailableModels(): Promise<string[]> {
    const response = await api.get<string[]>('/api/v1/models');
    return response.data;
  },

  // Stream workflow updates (Server-Sent Events)
  createWorkflowStream(taskId: string, onMessage: (data: any) => void, onError?: (error: any) => void) {
    const eventSource = new EventSource(`${API_BASE_URL}/api/v1/autonomous/stream/${taskId}`);
    
    eventSource.onmessage = (event) => {
      try {
        const data = JSON.parse(event.data);
        onMessage(data);
      } catch (error) {
        console.error('Error parsing stream data:', error);
      }
    };

    eventSource.onerror = (error) => {
      console.error('Stream error:', error);
      if (onError) onError(error);
    };

    return eventSource;
  },

  // Download artifacts
  async downloadArtifacts(taskId: string): Promise<Blob> {
    console.log('📥 Downloading artifacts...', { taskId });
    const response = await api.get(`/api/v1/autonomous/artifacts/${taskId}`, {
      responseType: 'blob'
    });
    return response.data as Blob;
  },

  // Export project data
  async exportProject(taskId: string, format: 'json' | 'zip' = 'json'): Promise<Blob> {
    console.log('📤 Exporting project...', { taskId, format });
    const response = await api.get(`/api/v1/autonomous/export/${taskId}`, {
      params: { format },
      responseType: 'blob'
    });
    return response.data as Blob;
  },

  // Get autonomous insights
  async getAutonomousInsights(taskId: string): Promise<any> {
    console.log('💡 Getting autonomous insights...', { taskId });
    const response = await api.get(`/api/v1/autonomous/insights/${taskId}`);
    return response.data;
  },

  // Restart workflow from specific phase
  async restartFromPhase(taskId: string, phase: string): Promise<AutonomousResponse> {
    console.log('🔄 Restarting from phase...', { taskId, phase });
    const response = await api.post<AutonomousResponse>('/api/v1/autonomous/restart', {
      task_id: taskId,
      phase
    });
    return response.data;
  },

  // Pause/Resume autonomous execution
  async pauseAutonomousExecution(taskId: string): Promise<AutonomousResponse> {
    console.log('⏸️ Pausing autonomous execution...', { taskId });
    const response = await api.post<AutonomousResponse>('/api/v1/autonomous/pause', {
      task_id: taskId
    });
    return response.data;
  },

  async resumeAutonomousExecution(taskId: string): Promise<AutonomousResponse> {
    console.log('▶️ Resuming autonomous execution...', { taskId });
    const response = await api.post<AutonomousResponse>('/api/v1/autonomous/resume', {
      task_id: taskId
    });
    return response.data;
  },

  // Cancel workflow
  async cancelWorkflow(taskId: string): Promise<AutonomousResponse> {
    console.log('🛑 Cancelling workflow...', { taskId });
    const response = await api.post<AutonomousResponse>('/api/v1/autonomous/cancel', {
      task_id: taskId
    });
    return response.data;
  }
};

export default autonomousApiService;
