# Deployment Guide

## Backend Deployment

### Environment Variables Required

When deploying the backend, you need to set the following environment variables:

#### Database Configuration
- `DATABASE_URL`: Full PostgreSQL connection string
- `DB_USER`: Database user
- `DB_PASSWORD`: Database password
- `DB_HOST`: Database host
- `DB_PORT`: Database port (default: 5432)
- `DB_NAME`: Database name
- `DB_ECHO`: Enable/disable SQL logging (default: False)

#### JWT Configuration
- `SECRET_KEY`: Secret key for JWT tokens (use a strong, random string)
- `ALGORITHM`: Algorithm for JWT (default: HS256)
- `ACCESS_TOKEN_EXPIRE_MINUTES`: Token expiration time (default: 30)

#### AI Service Configuration
- `OPENAI_API_KEY`: Your OpenAI API key (optional if using OpenRouter)
- `OPENROUTER_API_KEY`: Your OpenRouter API key (optional if using OpenAI)
- `OPENAI_BASE_URL`: Custom OpenAI-compatible API URL (optional)
- `OPENROUTER_BASE_URL`: Custom OpenRouter API URL (optional)
- `OPENAI_MODEL`: Model to use with OpenAI (default: gpt-3.5-turbo)
- `OPENROUTER_MODEL`: Model to use with OpenRouter (default: openai/gpt-3.5-turbo)

## Frontend Deployment

### Environment Variables Required

When deploying the frontend, you need to set:

- `NEXT_PUBLIC_API_URL`: The URL of your deployed backend API

Example:
```
NEXT_PUBLIC_API_URL=https://your-backend-deployment-url.com
```

## Deployment Steps

### 1. Deploy Backend First

Deploy the backend to your preferred platform (Heroku, Railway, Render, etc.) and make sure to set all required environment variables.

### 2. Update Frontend Configuration

After deploying the backend, update the frontend's `NEXT_PUBLIC_API_URL` to point to your deployed backend URL.

### 3. Deploy Frontend

Deploy the frontend to Vercel, Netlify, or your preferred platform.

## Common Issues and Solutions

### CORS Errors
If you're experiencing CORS errors, make sure your backend allows requests from your frontend's domain. The backend's CORS configuration allows:
- Local development: `http://localhost:3000`, `http://127.0.0.1:3000`, etc.
- Vercel deployments: `https://*.vercel.app`
- Hugging Face Spaces: `https://*.huggingface.co`, `https://*.hf.space`

### API Connection Failures
- Verify that your `NEXT_PUBLIC_API_URL` points to the correct backend URL
- Ensure your backend is deployed and accessible
- Check that SSL certificates are properly configured if using HTTPS

### Authentication Issues
- Make sure JWT configuration is consistent between frontend and backend
- Verify that the `SECRET_KEY` is the same in both environments

## Platform-Specific Instructions

### Vercel (Frontend)
1. Fork this repository
2. Connect to Vercel
3. Set environment variable: `NEXT_PUBLIC_API_URL`
4. Deploy

### Heroku/Railway/Render (Backend)
1. Fork this repository
2. Connect to your platform
3. Set all required environment variables
4. Deploy

### Hugging Face Spaces (Backend Alternative)
1. Create a Space with Docker or Gradio runner
2. Add your API keys to Space Secrets
3. Configure the app to run the backend server