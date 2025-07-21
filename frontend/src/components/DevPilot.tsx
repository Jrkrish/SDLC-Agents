import React, { useState, useEffect } from 'react';
import {
  Container,
  Typography,
  Button,
  TextField,
  Card,
  CardContent,
  CardActions,
  Alert,
  CircularProgress,
  Box,
  Stepper,
  Step,
  StepLabel,
  Paper,
  Chip,
  LinearProgress,
  IconButton,
  Tooltip,
  Accordion,
  AccordionSummary,
  AccordionDetails,
  Grid,
  Tabs,
  Tab,
  List,
  ListItem,
  ListItemIcon,
  ListItemText,
  Fade,
  Slide,
  Zoom,
} from '@mui/material';
import {
  Refresh,
  CheckCircle,
  Error as ErrorIcon,
  ExpandMore,
  PlayArrow,
  Code,
  Description,
  Security,
  BugReport,
  Publish,
  History,
  Feedback,
  Settings,
  Download,
  Cloud,
} from '@mui/icons-material';
import { apiService, SDLCResponse } from '../services/api';

interface DevPilotState {
  currentStep: number;
  projectName: string;
  taskId: string;
  requirements: string;
  feedback: string;
  loading: boolean;
  error: string | null;
  success: string | null;
  sdlcState: any;
  backendConnected: boolean;
  progress: number;
  dialogOpen: boolean;
  selectedTab: number;
  userStories: string[];
  designDocs: string;
  codeGenerated: string;
  testCases: string[];
  securityReport: string;
  deploymentConfig: any;
  projectHistory: any[];
}

const steps = [
  'Project Initialization',
  'Requirements Analysis',
  'User Stories Creation',
  'System Design',
  'Code Implementation',
  'Security Analysis',
  'Testing & QA',
  'Deployment',
  'Project Complete'
];

const stepIcons = [
  PlayArrow,
  Description,
  History,
  Description,
  Code,
  Security,
  BugReport,
  Publish,
  CheckCircle
];

const DevPilot: React.FC = () => {
  const [state, setState] = useState<DevPilotState>({
    currentStep: 0,
    projectName: '',
    taskId: '',
    requirements: '',
    feedback: '',
    loading: false,
    error: null,
    success: null,
    sdlcState: null,
    backendConnected: false,
    progress: 0,
    dialogOpen: false,
    selectedTab: 0,
    userStories: [],
    designDocs: '',
    codeGenerated: '',
    testCases: [],
    securityReport: '',
    deploymentConfig: null,
    projectHistory: [],
  });

  useEffect(() => {
    // Check if backend is available
    checkBackendHealth();
  }, []);

  const checkBackendHealth = async () => {
    try {
      await apiService.healthCheck();
      setState(prev => ({ 
        ...prev, 
        backendConnected: true,
        success: 'Backend is connected successfully!',
        error: null
      }));
    } catch (error) {
      setState(prev => ({ 
        ...prev, 
        backendConnected: false,
        error: 'Backend is not available. Please make sure FastAPI server is running on localhost:8000',
        success: null
      }));
    }
  };

  const handleStartSDLC = async () => {
    if (!state.projectName.trim()) {
      setState(prev => ({ ...prev, error: 'Project name is required' }));
      return;
    }

    setState(prev => ({ ...prev, loading: true, error: null }));

    try {
      const response: SDLCResponse = await apiService.startSDLC(state.projectName);
      
      if (response.status === 'success') {
        setState(prev => ({
          ...prev,
          loading: false,
          success: response.message,
          taskId: response.task_id || '',
          sdlcState: response.state,
          currentStep: 1,
        }));
      } else {
        setState(prev => ({
          ...prev,
          loading: false,
          error: response.error || 'Failed to start SDLC process',
        }));
      }
    } catch (error: any) {
      let errorMessage = 'An error occurred';
      if (error.response?.data?.detail) {
        errorMessage = error.response.data.detail;
      } else if (error.response?.data?.error) {
        errorMessage = error.response.data.error;
      } else if (error.message) {
        errorMessage = error.message;
      }
      setState(prev => ({
        ...prev,
        loading: false,
        error: errorMessage,
      }));
    }
  };

  const handleGenerateUserStories = async () => {
    if (!state.requirements.trim()) {
      setState(prev => ({ ...prev, error: 'Requirements are required' }));
      return;
    }

    setState(prev => ({ ...prev, loading: true, error: null }));

    try {
      const response: SDLCResponse = await apiService.generateUserStories(
        state.taskId,
        state.requirements
      );

      if (response.status === 'success') {
        setState(prev => ({
          ...prev,
          loading: false,
          success: response.message,
          sdlcState: response.state,
          currentStep: 2,
        }));
      } else {
        setState(prev => ({
          ...prev,
          loading: false,
          error: response.error || 'Failed to generate user stories',
        }));
      }
    } catch (error: any) {
      let errorMessage = 'An error occurred';
      if (error.response?.data?.detail) {
        errorMessage = error.response.data.detail;
      } else if (error.response?.data?.error) {
        errorMessage = error.response.data.error;
      } else if (error.message) {
        errorMessage = error.message;
      }
      setState(prev => ({
        ...prev,
        loading: false,
        error: errorMessage,
      }));
    }
  };

  const handleProgressFlow = async (nextNode: string) => {
    setState(prev => ({ ...prev, loading: true, error: null }));

    try {
      const response: SDLCResponse = await apiService.progressFlow(
        state.taskId,
        'approved',
        state.feedback || 'Proceeding to next step',
        nextNode
      );

      if (response.status === 'success') {
        setState(prev => ({
          ...prev,
          loading: false,
          success: response.message,
          sdlcState: response.state,
          currentStep: Math.min(prev.currentStep + 1, steps.length - 1),
          feedback: '',
        }));
      } else {
        setState(prev => ({
          ...prev,
          loading: false,
          error: response.error || 'Failed to progress flow',
        }));
      }
    } catch (error: any) {
      let errorMessage = 'An error occurred';
      if (error.response?.data?.detail) {
        errorMessage = error.response.data.detail;
      } else if (error.response?.data?.error) {
        errorMessage = error.response.data.error;
      } else if (error.message) {
        errorMessage = error.message;
      }
      setState(prev => ({
        ...prev,
        loading: false,
        error: errorMessage,
      }));
    }
  };

  const renderCurrentStepContent = () => {
    switch (state.currentStep) {
      case 0:
        return (
          <Fade in={true}>
            <Card elevation={3} sx={{ background: 'linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%)' }}>
              <CardContent>
                <Box display="flex" alignItems="center" mb={2}>
                  <PlayArrow sx={{ mr: 2, color: 'primary.main', fontSize: 32 }} />
                  <Typography variant="h5" fontWeight="bold">
                    Start New SDLC Project
                  </Typography>
                </Box>
                <TextField
                  fullWidth
                  label="Project Name"
                  value={state.projectName}
                  onChange={(e) => setState(prev => ({ ...prev, projectName: e.target.value }))}
                  margin="normal"
                  placeholder="Enter your project name (e.g., E-commerce Platform)"
                  variant="outlined"
                  sx={{ mb: 2 }}
                />
                <Typography variant="body2" color="text.secondary">
                  💡 Tip: Choose a descriptive name that reflects your project's main purpose
                </Typography>
              </CardContent>
              <CardActions sx={{ p: 3, pt: 0 }}>
                <Button
                  variant="contained"
                  size="large"
                  onClick={handleStartSDLC}
                  disabled={state.loading || !state.projectName.trim()}
                  startIcon={state.loading ? <CircularProgress size={20} /> : <PlayArrow />}
                  sx={{ minWidth: 200 }}
                >
                  {state.loading ? 'Initializing...' : 'Start SDLC Process'}
                </Button>
              </CardActions>
            </Card>
          </Fade>
        );

      case 1:
        return (
          <Slide direction="up" in={true}>
            <Card elevation={3} sx={{ background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)', color: 'white' }}>
              <CardContent>
                <Box display="flex" alignItems="center" mb={2}>
                  <Description sx={{ mr: 2, fontSize: 32 }} />
                  <Typography variant="h5" fontWeight="bold">
                    Project Requirements
                  </Typography>
                </Box>
                <TextField
                  fullWidth
                  multiline
                  rows={6}
                  label="Requirements"
                  value={state.requirements}
                  onChange={(e) => setState(prev => ({ ...prev, requirements: e.target.value }))}
                  margin="normal"
                  placeholder="Describe your project requirements in detail...\n\nExample:\n• Users should be able to register and login\n• Product catalog with search functionality\n• Shopping cart and checkout process\n• Order management system\n• Admin dashboard for inventory management"
                  variant="outlined"
                  sx={{ 
                    mb: 2,
                    '& .MuiOutlinedInput-root': {
                      backgroundColor: 'rgba(255,255,255,0.1)',
                      '& fieldset': { borderColor: 'rgba(255,255,255,0.3)' },
                      '&:hover fieldset': { borderColor: 'rgba(255,255,255,0.5)' },
                      '&.Mui-focused fieldset': { borderColor: 'white' }
                    },
                    '& .MuiInputLabel-root': { color: 'rgba(255,255,255,0.8)' },
                    '& .MuiInputBase-input': { color: 'white' },
                    '& .MuiInputBase-input::placeholder': { color: 'rgba(255,255,255,0.6)' }
                  }}
                />
                <Typography variant="body2" sx={{ opacity: 0.9 }}>
                  📝 Be as detailed as possible - this will help generate better user stories
                </Typography>
              </CardContent>
              <CardActions sx={{ p: 3, pt: 0 }}>
                <Button
                  variant="contained"
                  size="large"
                  onClick={handleGenerateUserStories}
                  disabled={state.loading || !state.requirements.trim()}
                  startIcon={state.loading ? <CircularProgress size={20} /> : <History />}
                  sx={{ 
                    minWidth: 220,
                    backgroundColor: 'rgba(255,255,255,0.2)',
                    '&:hover': { backgroundColor: 'rgba(255,255,255,0.3)' }
                  }}
                >
                  {state.loading ? 'Generating Stories...' : 'Generate User Stories'}
                </Button>
              </CardActions>
            </Card>
          </Slide>
        );

      default:
        return (
          <Zoom in={true}>
            <Card elevation={3}>
              <CardContent>
                <Box display="flex" alignItems="center" mb={2}>
                  {React.createElement(stepIcons[state.currentStep] || Code, { 
                    sx: { mr: 2, color: 'primary.main', fontSize: 32 } 
                  })}
                  <Typography variant="h5" fontWeight="bold">
                    {steps[state.currentStep]}
                  </Typography>
                </Box>
                
                {state.sdlcState && (
                  <Box mb={3}>
                    <Tabs 
                      value={state.selectedTab} 
                      onChange={(_, newValue) => setState(prev => ({ ...prev, selectedTab: newValue }))}
                      variant="scrollable"
                      scrollButtons="auto"
                    >
                      <Tab label="Current Output" />
                      <Tab label="Progress Details" />
                      <Tab label="History" />
                    </Tabs>
                    
                    <Box mt={2}>
                      {state.selectedTab === 0 && (
                        <Paper elevation={1} sx={{ p: 2, bgcolor: '#f8f9fa' }}>
                          <pre style={{ whiteSpace: 'pre-wrap', fontSize: '0.875rem' }}>
                            {JSON.stringify(state.sdlcState, null, 2)}
                          </pre>
                        </Paper>
                      )}
                      {state.selectedTab === 1 && (
                        <List>
                          {steps.map((step, index) => (
                            <ListItem key={index}>
                              <ListItemIcon>
                                {index < state.currentStep ? <CheckCircle color="success" /> : 
                                 index === state.currentStep ? <CircularProgress size={20} /> : 
                                 React.createElement(stepIcons[index], { color: 'disabled' })}
                              </ListItemIcon>
                              <ListItemText 
                                primary={step} 
                                secondary={index < state.currentStep ? 'Completed' : 
                                          index === state.currentStep ? 'In Progress' : 'Pending'}
                              />
                            </ListItem>
                          ))}
                        </List>
                      )}
                      {state.selectedTab === 2 && (
                        <Typography variant="body2" color="text.secondary">
                          Project history will be displayed here...
                        </Typography>
                      )}
                    </Box>
                  </Box>
                )}
                
                <TextField
                  fullWidth
                  multiline
                  rows={3}
                  label="Feedback (Optional)"
                  value={state.feedback}
                  onChange={(e) => setState(prev => ({ ...prev, feedback: e.target.value }))}
                  margin="normal"
                  placeholder="Add any feedback or modifications for this step..."
                  variant="outlined"
                />
              </CardContent>
              <CardActions sx={{ p: 3, pt: 0, justifyContent: 'space-between' }}>
                <Button
                  variant="outlined"
                  onClick={() => setState(prev => ({ ...prev, currentStep: Math.max(0, prev.currentStep - 1) }))}
                  disabled={state.currentStep === 0}
                >
                  Previous Step
                </Button>
                <Button
                  variant="contained"
                  size="large"
                  onClick={() => handleProgressFlow('next')}
                  disabled={state.loading}
                  startIcon={state.loading ? <CircularProgress size={20} /> : 
                           state.currentStep === steps.length - 1 ? <Publish /> : <PlayArrow />}
                >
                  {state.loading ? 'Processing...' : 
                   state.currentStep === steps.length - 1 ? 'Deploy Project' : 'Continue to Next Step'}
                </Button>
              </CardActions>
            </Card>
          </Zoom>
        );
    }
  };

  return (
    <Container maxWidth="xl" sx={{ mt: 2, mb: 4 }}>
      {/* Enhanced Header */}
      <Paper elevation={6} sx={{ 
        p: 4, 
        mb: 4, 
        background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
        borderRadius: 3,
        position: 'relative',
        overflow: 'hidden'
      }}>
        <Box 
          sx={{
            position: 'absolute',
            top: 0,
            right: 0,
            width: '300px',
            height: '300px',
            background: 'rgba(255,255,255,0.1)',
            borderRadius: '50%',
            transform: 'translate(100px, -100px)'
          }}
        />
        <Grid container alignItems="center" justifyContent="space-between" spacing={3}>
          <Grid size={{ xs: 12, md: 8 }}>
            <Box display="flex" alignItems="center" mb={2}>
              <Settings sx={{ mr: 2, color: 'white', fontSize: 40 }} />
              <Box>
                <Typography variant="h3" component="h1" sx={{ color: 'white', fontWeight: 'bold', mb: 1 }}>
                  DevPilot - AI SDLC Assistant
                </Typography>
                <Typography variant="h6" sx={{ color: 'rgba(255,255,255,0.9)' }}>
                  Complete Software Development Lifecycle with AI-Powered Automation
                </Typography>
              </Box>
            </Box>
            <Box display="flex" gap={1} flexWrap="wrap">
              <Chip label="AI-Powered" size="small" sx={{ backgroundColor: 'rgba(255,255,255,0.2)', color: 'white' }} />
              <Chip label="Full Pipeline" size="small" sx={{ backgroundColor: 'rgba(255,255,255,0.2)', color: 'white' }} />
              <Chip label="Automated" size="small" sx={{ backgroundColor: 'rgba(255,255,255,0.2)', color: 'white' }} />
            </Box>
          </Grid>
          <Grid size={{ xs: 12, md: 4 }}>
            <Box display="flex" flexDirection="column" alignItems="end" gap={2}>
              <Box display="flex" alignItems="center" gap={1}>
                <Chip 
                  icon={state.backendConnected ? <CheckCircle /> : <ErrorIcon />}
                  label={state.backendConnected ? "API Connected" : "API Offline"}
                  color={state.backendConnected ? "success" : "error"}
                  variant="filled"
                  size="small"
                />
                <Tooltip title="Refresh Backend Connection">
                  <IconButton onClick={checkBackendHealth} sx={{ color: 'white' }}>
                    <Refresh />
                  </IconButton>
                </Tooltip>
              </Box>
              {state.taskId && (
                <Box textAlign="right">
                  <Typography variant="caption" sx={{ color: 'rgba(255,255,255,0.7)' }}>Task ID:</Typography>
                  <Typography variant="body2" sx={{ color: 'white', fontFamily: 'monospace' }}>{state.taskId}</Typography>
                </Box>
              )}
            </Box>
          </Grid>
        </Grid>
      </Paper>

      {/* Enhanced Progress Indicator */}
      {state.loading && (
        <Fade in={state.loading}>
          <Paper elevation={2} sx={{ mb: 3, p: 2, bgcolor: 'primary.light', color: 'white' }}>
            <Box display="flex" alignItems="center" gap={2}>
              <CircularProgress size={24} sx={{ color: 'white' }} />
              <Typography variant="h6">Processing... Please wait</Typography>
            </Box>
            <LinearProgress sx={{ mt: 1, bgcolor: 'rgba(255,255,255,0.3)' }} />
          </Paper>
        </Fade>
      )}

      {/* Enhanced Error Display */}
      {state.error && typeof state.error === 'string' && (
        <Slide direction="down" in={true}>
          <Alert 
            severity="error" 
            sx={{ mb: 3, borderRadius: 2 }}
            action={
              <IconButton
                color="inherit"
                size="small"
                onClick={() => setState(prev => ({ ...prev, error: null }))}
              >
                ×
              </IconButton>
            }
          >
            <Typography variant="subtitle1" fontWeight="bold">Error Occurred</Typography>
            <Typography variant="body2">{state.error}</Typography>
          </Alert>
        </Slide>
      )}

      {/* Enhanced Success Display */}
      {state.success && (
        <Slide direction="down" in={true}>
          <Alert 
            severity="success" 
            sx={{ mb: 3, borderRadius: 2 }}
            action={
              <IconButton
                color="inherit"
                size="small"
                onClick={() => setState(prev => ({ ...prev, success: null }))}
              >
                ×
              </IconButton>
            }
          >
            <Typography variant="subtitle1" fontWeight="bold">Success!</Typography>
            <Typography variant="body2">{state.success}</Typography>
          </Alert>
        </Slide>
      )}

      {/* Enhanced Stepper */}
      <Paper elevation={2} sx={{ p: 3, mb: 4, borderRadius: 3 }}>
        <Typography variant="h5" gutterBottom fontWeight="bold" textAlign="center" mb={3}>
          SDLC Pipeline Progress
        </Typography>
        <Stepper activeStep={state.currentStep} alternativeLabel>
          {steps.map((label, index) => {
            const StepIconComponent = stepIcons[index];
            return (
              <Step key={label}>
                <StepLabel 
                  StepIconComponent={() => (
                    <Box
                      sx={{
                        width: 40,
                        height: 40,
                        borderRadius: '50%',
                        display: 'flex',
                        alignItems: 'center',
                        justifyContent: 'center',
                        backgroundColor: index < state.currentStep ? 'success.main' : 
                                       index === state.currentStep ? 'primary.main' : 'grey.300',
                        color: 'white'
                      }}
                    >
                      {index < state.currentStep ? 
                        <CheckCircle /> : 
                        <StepIconComponent />}
                    </Box>
                  )}
                >
                  <Typography variant="body2" fontWeight={index <= state.currentStep ? 'bold' : 'normal'}>
                    {label}
                  </Typography>
                </StepLabel>
              </Step>
            );
          })}
        </Stepper>
      </Paper>

      {/* Main Content Area */}
      <Box sx={{ mb: 4 }}>
        {renderCurrentStepContent()}
      </Box>

      {/* Quick Actions Panel */}
      {state.currentStep > 0 && (
        <Paper elevation={2} sx={{ p: 3, mb: 3, borderRadius: 3 }}>
          <Typography variant="h6" gutterBottom>Quick Actions</Typography>
          <Box display="flex" gap={2} flexWrap="wrap">
            <Button startIcon={<Download />} variant="outlined" size="small">
              Export Progress
            </Button>
            <Button startIcon={<History />} variant="outlined" size="small">
              View History
            </Button>
            <Button startIcon={<Cloud />} variant="outlined" size="small">
              Save to Cloud
            </Button>
            <Button startIcon={<Feedback />} variant="outlined" size="small">
              Send Feedback
            </Button>
          </Box>
        </Paper>
      )}

      {/* Enhanced SDLC State Display */}
      {state.sdlcState && (
        <Paper elevation={2} sx={{ borderRadius: 3, overflow: 'hidden' }}>
          <Accordion>
            <AccordionSummary 
              expandIcon={<ExpandMore />}
              sx={{ 
                backgroundColor: 'primary.main', 
                color: 'white',
                '& .MuiAccordionSummary-expandIconWrapper': { color: 'white' }
              }}
            >
              <Box display="flex" alignItems="center" gap={1}>
                <Code />
                <Typography variant="h6" fontWeight="bold">
                  Detailed SDLC State & Output
                </Typography>
              </Box>
            </AccordionSummary>
            <AccordionDetails sx={{ p: 0 }}>
              <Box sx={{ 
                bgcolor: '#1e1e1e', 
                color: '#f8f8f2',
                p: 3,
                maxHeight: '500px', 
                overflow: 'auto',
                fontFamily: 'monospace'
              }}>
                <pre style={{ 
                  whiteSpace: 'pre-wrap', 
                  fontSize: '0.875rem', 
                  margin: 0,
                  lineHeight: 1.5
                }}>
                  {JSON.stringify(state.sdlcState, null, 2)}
                </pre>
              </Box>
            </AccordionDetails>
          </Accordion>
        </Paper>
      )}
    </Container>
  );
};

export default DevPilot;
