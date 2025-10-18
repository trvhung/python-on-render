# Python FastAPI on Render

A sample Python REST API built with FastAPI and SQLAlchemy, ready to deploy on Render.

## What's Included

- FastAPI web server with CRUD endpoints
- PostgreSQL database integration
- Pre-configured `render.yaml` for easy deployment

## Deploy to Render

### Option 1: Blueprint (Recommended)

1. **Fork this repository** to your GitHub account

2. **Sign up** at [render.com](https://render.com) (free)

3. **Create a new Blueprint**:
   - Click "New" → "Blueprint"
   - Connect your GitHub account
   - Select this repository
   - Click "Apply"

4. **Wait for deployment** (2-3 minutes)

5. **Access your API** at the URL Render provides (e.g., `https://your-app.onrender.com`)

### Option 2: Manual Setup

1. **Create a PostgreSQL database**:
   - Click "New" → "PostgreSQL"
   - Give it a name (e.g., `fastapi-db`)
   - Click "Create Database"
   - Once created, go to the database page and scroll down to "Connections"
   - Copy the **Internal Database URL**

2. **Create a Web Service**:
   - Click "New" → "Web Service"
   - Connect your repository
   - Build Command: `pip install uv && uv sync`
   - Start Command: `uv run uvicorn main:app --host 0.0.0.0 --port $PORT`

3. **Add the database environment variable**:
   - In your web service settings, go to "Environment"
   - Add a new variable: `DATABASE_URL`
   - Paste the Internal Database URL you copied earlier
   - Save changes and your service will redeploy

## Testing the API

Once deployed, visit your app URL to see the welcome message. Try these endpoints:

- `GET /` - Welcome message
- `POST /api/items` - Create an item
- `GET /api/items` - List all items
- `GET /api/items/{id}` - Get specific item
- `DELETE /api/items/{id}` - Delete an item

## Local Development

```bash
pip install uv
uv sync
uv run uvicorn main:app --reload
```

Visit `http://localhost:8000` to see your app.
