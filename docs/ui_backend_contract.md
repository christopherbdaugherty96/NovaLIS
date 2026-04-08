# UI-Backend Contract Documentation

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