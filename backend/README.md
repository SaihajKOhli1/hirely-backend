# Hirely Backend

FastAPI backend for the Hirely application.

## Setup

1. **Create a virtual environment:**
   ```bash
   python3 -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

2. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Run the server:**
   ```bash
   uvicorn app:app --reload
   ```

4. **Access the health endpoint:**
   - Open your browser or use curl: `http://localhost:8000/health`
   - The endpoint will return the MongoDB connection status and list of collections

## Environment Variables

The `.env` file contains MongoDB connection credentials. Make sure it's configured before running the application.

