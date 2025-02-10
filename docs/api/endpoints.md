# API Documentation

## Version
2.0.0

## Last Updated
2025-02-09

## Overview
This document details the API endpoints, request/response formats, and authentication requirements for the Hello World Project.

## Table of Contents
1. [Authentication](#authentication)
2. [Users API](#users-api)
3. [Metrics API](#metrics-api)
4. [Health API](#health-api)
5. [Rate Limits](#rate-limits)

## Authentication

### Login
```http
POST /api/v1/token
Content-Type: application/x-www-form-urlencoded

username=user@example.com&password=secretpassword
```

Response:
```json
{
    "access_token": "eyJ0eXAiOiJKV1QiLCJhbGc...",
    "token_type": "bearer"
}
```

### Using Authentication
```http
GET /api/v1/users/me
Authorization: Bearer eyJ0eXAiOiJKV1QiLCJhbGc...
```

## Users API

### Create User
```http
POST /api/v1/users
Content-Type: application/json

{
    "email": "user@example.com",
    "password": "securepassword123"
}
```

Response:
```json
{
    "id": 1,
    "email": "user@example.com"
}
```

### Get User
```http
GET /api/v1/users/{user_id}
Authorization: Bearer eyJ0eXAiOiJKV1QiLCJhbGc...
```

Response:
```json
{
    "id": 1,
    "email": "user@example.com"
}
```

## Metrics API

### Get Metrics
```http
GET /api/v1/metrics
```

Response:
```text
# HELP http_requests_total Total HTTP requests
# TYPE http_requests_total counter
http_requests_total{method="GET",endpoint="/api/v1/users",status="200"} 24
```

## Health API

### Check Health
```http
GET /health
```

Response:
```json
{
    "status": "healthy",
    "database": "healthy",
    "version": "v1"
}
```

## Rate Limits
- Authentication endpoints: 5 requests per minute
- User endpoints: 60 requests per minute
- Health check: 120 requests per minute

## Error Responses

### 400 Bad Request
```json
{
    "detail": "Invalid request parameters"
}
```

### 401 Unauthorized
```json
{
    "detail": "Invalid authentication credentials"
}
```

### 403 Forbidden
```json
{
    "detail": "Not enough permissions"
}
```

### 404 Not Found
```json
{
    "detail": "Resource not found"
}
```

### 429 Too Many Requests
```json
{
    "detail": "Rate limit exceeded"
}
``` 