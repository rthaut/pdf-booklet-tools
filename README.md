# PDF Booklet Tool

A web application for manipulating PDF booklets. Built with React, FastAPI, and deployed on Fly.io.

## Features

- Swap PDF halves for correct booklet printing
- Scale PDF pages to portrait orientation
- Drag-and-drop interface
- Rate-limited API
- Continuous deployment

## Development

### Prerequisites

- Python 3.9+
- Node.js 22+
- poppler-utils

### Local Setup

1. Clone the repository:

    ```bash
    git clone https://github.com/YOUR_USERNAME/YOUR_REPO_NAME.git
    cd YOUR_REPO_NAME
    ```

1. Set up the backend:

    ```bash
    cd backend
    python -m venv venv
    source venv/bin/activate  # On Windows: .\venv\Scripts\activate
    pip install -r requirements.txt
    ```

1. Set up the frontend:

    ```bash
    cd frontend
    npm install
    ```

1. Start the development servers:

    ```bash
    # In one terminal (backend)
    cd backend
    python -m uvicorn app.main:app --reload --port 8000

    # In another terminal (frontend)
    cd frontend
    npm run dev
    ```

### Testing

```bash
# Backend tests
cd backend
pytest

# Frontend tests
cd frontend
npm test
```

## Deployment

The application automatically deploys to Fly.io when changes are pushed to the main branch.

## License

MIT
