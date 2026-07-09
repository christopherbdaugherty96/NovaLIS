# UI-Backend Contract Documentation

> **Deprecated placeholder — not a real contract.** This file is boilerplate `/api/example`
> content, not Nova's actual UI/backend interface. It is retained only to avoid a dangling link.
> For the real runtime surface see [`../CANONICAL/05_FRONTEND_BACKEND_TRUTH.md`](../CANONICAL/05_FRONTEND_BACKEND_TRUTH.md)
> and `REPO_MAP.md`; the served UI is the modular bundle under `nova_backend/static/`.

## Overview
This document outlines the contract between the UI and backend services.
### API Endpoints
- **GET /api/example**
  - **Response**: {
      "data": {...},
      "error": null
    }

- **POST /api/example**
  - **Request**: {
      "name": "example"
    }
  - **Response**: {
      "data": {...},
      "error": null
    }

### Error Handling
The backend will respond with appropriate HTTP status codes and error messages as per the contract.