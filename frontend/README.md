# DevPilot React Frontend

This is the React frontend for the DevPilot AI SDLC Assistant application.

## Features

- Modern React with TypeScript
- Material-UI for beautiful, responsive UI
- Integration with FastAPI backend
- Step-by-step SDLC workflow
- Real-time feedback and status updates

## Prerequisites

- Node.js (v14 or higher)
- npm or yarn
- DevPilot FastAPI backend running on localhost:8000

## Installation

1. Install dependencies:
```bash
npm install
```

2. Start the development server:
```bash
npm start
```

The application will be available at `http://localhost:3000`.

## API Integration

The frontend connects to the FastAPI backend at `http://localhost:8000`. Make sure the backend is running before using the frontend.

### Available API Endpoints

- `GET /` - Health check
- `POST /api/v1/sdlc/start` - Start SDLC process
- `POST /api/v1/sdlc/user_stories` - Generate user stories
- `POST /api/v1/sdlc/progress_flow` - Progress to next step

## Environment Configuration

The API base URL can be configured in `src/services/api.ts`. By default, it points to `http://localhost:8000`.

## Development

### Project Structure

```
src/
  components/          # React components
    DevPilot.tsx      # Main application component
  services/           # API integration
    api.ts           # API service functions
  App.tsx            # Root component with theme
  index.tsx          # Application entry point
```

### Key Components

- **DevPilot**: Main component handling the SDLC workflow
- **API Service**: Handles all backend communication
- **Material-UI Theme**: Provides consistent styling

## Available Scripts

### `npm start`

Runs the app in the development mode.
Open [http://localhost:3000](http://localhost:3000) to view it in the browser.

### `npm run build`

Builds the app for production to the `build` folder.
Optimizes the build for the best performance.

### `npm test`

Launches the test runner in the interactive watch mode.

## Troubleshooting

1. **Backend Connection Issues**: Ensure the FastAPI server is running on localhost:8000
2. **CORS Errors**: The backend already has CORS configured for localhost:3000
3. **API Key Issues**: Set required environment variables (GROQ_API_KEY or GEMINI_API_KEY) before starting the backend

## Building for Production

```bash
npm run build
```

This creates a `build` folder with optimized production files.
