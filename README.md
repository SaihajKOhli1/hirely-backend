# Hirely - Company-Specific Resume Critiques

A full-stack application for uploading resumes and getting AI-powered feedback tailored to specific companies (Google, Meta, Amazon, Microsoft, NVIDIA, etc.).

## Project Structure

```
hirely-main/
├── backend/          # FastAPI backend server
│   ├── app.py       # Main FastAPI application
│   ├── db.py        # MongoDB connection handler
│   ├── requirements.txt
│   └── .env         # MongoDB credentials (not in git)
├── index.html       # Frontend landing page
├── indexdropbox.html # Frontend with file upload
└── images/          # Company logos
```

## Prerequisites

- Python 3.8 or higher
- MongoDB Atlas account (or local MongoDB)
- Git (for version control)

## Quick Start

### 1. Clone the Repository

```bash
git clone <your-repo-url>
cd hirely-main
```

### 2. Backend Setup

```bash
# Navigate to backend directory
cd backend

# Create virtual environment
python3 -m venv venv

# Activate virtual environment
# On macOS/Linux:
source venv/bin/activate
# On Windows:
# venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Create .env file with your MongoDB credentials
# Copy the example and fill in your details:
cat > .env << EOF
MONGO_URI=mongodb+srv://your_username:your_password@your-cluster.mongodb.net/?retryWrites=true&w=majority&appName=Hirely
DB_NAME=hirely
EOF

# Run the server
uvicorn app:app --reload
```

The backend will be available at: **http://localhost:8000**

- API Docs: http://localhost:8000/docs
- Health Check: http://localhost:8000/health

### 3. Frontend Setup

The frontend is a simple HTML/CSS/JavaScript application. You can run it in several ways:

#### Option A: Using Python's HTTP Server (Easiest)

```bash
# From the project root directory
python3 -m http.server 3000
```

Then open: **http://localhost:3000**

#### Option B: Using Node.js (if you have it installed)

```bash
# Install a simple HTTP server
npx http-server -p 3000
```

#### Option C: Open Directly in Browser

Simply open `index.html` or `indexdropbox.html` in your browser.

**Note:** If you need to connect the frontend to the backend API, make sure:
1. Backend is running on `http://localhost:8000`
2. Update frontend API calls to point to `http://localhost:8000`

## Testing the Backend

### Test Health Endpoint

```bash
curl http://localhost:8000/health
```

Expected response:
```json
{
  "status": "ok",
  "collections": []
}
```

### Test via Browser

1. Open http://localhost:8000/docs
2. Click on `/health` endpoint
3. Click "Try it out" → "Execute"
4. View the response

## Environment Variables

Create a `.env` file in the `backend/` directory:

```env
MONGO_URI=mongodb+srv://username:password@cluster.mongodb.net/?retryWrites=true&w=majority&appName=Hirely
DB_NAME=hirely
```

**Important:** Never commit the `.env` file to Git! It contains sensitive credentials.

## API Endpoints

- `GET /` - Root endpoint
- `GET /health` - Health check and MongoDB connection status
- `GET /docs` - Interactive API documentation (Swagger UI)
- `GET /redoc` - Alternative API documentation (ReDoc)

## Development

### Backend Development

```bash
cd backend
source venv/bin/activate
uvicorn app:app --reload  # Auto-reloads on code changes
```

### Adding New Endpoints

1. Edit `backend/app.py`
2. Add your route handler
3. The server will auto-reload (if using `--reload` flag)

## Deployment

### Backend Deployment

The backend can be deployed to:
- **Heroku**: Add `Procfile` with `web: uvicorn app:app --host 0.0.0.0 --port $PORT`
- **Railway**: Automatically detects Python and FastAPI
- **Render**: Add build command and start command
- **AWS/GCP/Azure**: Use container services

### Frontend Deployment

- **Netlify**: Drag and drop the HTML files
- **Vercel**: Deploy static files
- **GitHub Pages**: Push to `gh-pages` branch

## Troubleshooting

### MongoDB Connection Issues

- Verify your `.env` file has correct credentials
- Check MongoDB Atlas network access (whitelist your IP)
- Ensure SSL/TLS is enabled for Atlas connections

### Port Already in Use

If port 8000 is busy:
```bash
uvicorn app:app --reload --port 8001
```

### Python Import Errors

Make sure you're in the virtual environment:
```bash
source venv/bin/activate
```

## License

MIT License - feel free to use this project for learning and development.

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request

