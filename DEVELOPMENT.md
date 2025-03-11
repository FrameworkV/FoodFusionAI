## Overview
This guide will help you locally run the React frontend of the Azure-hosted backend.

## Prerequisites
- Node.js (v16.x or later recommended)
- npm (v8.x or later)
- Git

## Getting Started

### 1. Clone the Repository
```bash
git clone https://github.com/FrameworkV/FoodFusionAI-Website.git
```

### 2. Switch Branch
Switch to the branch with the most recent changes, probably `dev`:
```bash
git checkout dev
```

### 3. Install Dependencies
Using npm:
```bash
npm install
```

### 4. Environment Configuration
If not already configured, change the url in the `.env` file to:
```
VITE_PYTHON_ENDPOINT="https://foodfusion.azurewebsites.net"
```

This configures your local frontend to communicate with the hosted backend API.

### 5. Start the Development Server
Using npm:
```bash
npm run dev
```

This will start the application on [http://localhost:5173](http://localhost:5173).

## Development Notes

### API Communication
- The application is configured to communicate with the hosted backend API
- API base URL is defined in the `.env` file
- All API requests will be sent to the actual backend service

### Building for Production
To create a production build:
```bash
npm run build
```