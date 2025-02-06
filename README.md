# PDF Booklet Tool

> A web application for manipulating PDF booklets. Built with React, FastAPI, and deployed on Fly.io.

[![Tests](https://github.com/rthaut/pdf-booklet-tools/actions/workflows/tests.yml/badge.svg)](https://github.com/rthaut/pdf-booklet-tools/actions/workflows/tests.yml)
[![Deploy to Fly.io](https://github.com/rthaut/pdf-booklet-tools/actions/workflows/fly.yml/badge.svg)](https://github.com/rthaut/pdf-booklet-tools/actions/workflows/fly.yml)

## Features

- Swap PDF halves for correct booklet printing
- Scale PDF pages to portrait orientation
- Drag-and-drop interface
- Rate-limited API
- Continuous deployment

## Deployment

The application automatically deploys to [Fly.io](https://fly.io/) when changes are pushed to the main branch and all tests pass.

## Development

### Prerequisites

- Python 3.9+
- Node.js 22+
- poppler-utils
  - On Windows: <https://github.com/oschwartz10612/poppler-windows/releases/>

### Local Setup

1. Clone the repository:

    ```bash
    git clone https://github.com/rthaut/pdf-booklet-tools.git
    cd pdf-booklet-tools
    ```

1. Set up the backend:

    ```bash
    cd backend
    python -m venv venv
    source venv/bin/activate  # On Windows: .\venv\Scripts\activate
    pip install -r requirements.txt
    pip install -r requirements-test.txt
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

## License

MIT
