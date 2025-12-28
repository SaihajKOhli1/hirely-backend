# How to Push to GitHub

Follow these steps to export your project to GitHub:

## Step 1: Create a GitHub Repository

1. Go to https://github.com and sign in
2. Click the "+" icon in the top right → "New repository"
3. Name it (e.g., "hirely" or "hirely-resume-critiques")
4. **Don't** initialize with README, .gitignore, or license (we already have these)
5. Click "Create repository"

## Step 2: Initialize Git in Your Project

Open terminal in your project directory and run:

```bash
# Navigate to project root
cd /Users/ahmad_afzal/Downloads/hirely-main

# Initialize git repository
git init

# Add all files (except those in .gitignore)
git add .

# Make your first commit
git commit -m "Initial commit: FastAPI backend with MongoDB integration"
```

## Step 3: Connect to GitHub

```bash
# Add your GitHub repository as remote (replace YOUR_USERNAME and REPO_NAME)
git remote add origin https://github.com/YOUR_USERNAME/REPO_NAME.git

# Rename main branch (if needed)
git branch -M main

# Push to GitHub
git push -u origin main
```

**Example:**
```bash
git remote add origin https://github.com/ahmad_afzal/hirely.git
git branch -M main
git push -u origin main
```

## Step 4: Verify on GitHub

1. Go to your repository on GitHub
2. You should see all your files
3. Make sure `.env` is **NOT** visible (it should be in .gitignore)

## Important Notes

### ✅ What Gets Pushed:
- All Python code (`app.py`, `db.py`, etc.)
- `requirements.txt`
- Frontend files (`index.html`, etc.)
- Documentation files
- `.gitignore`

### ❌ What Should NOT Be Pushed:
- `.env` file (contains sensitive MongoDB credentials)
- `venv/` directory (virtual environment)
- `__pycache__/` directories
- `.DS_Store` files

These are already in `.gitignore`, so they won't be committed.

## Updating Your Repository

After making changes:

```bash
# Stage changes
git add .

# Commit changes
git commit -m "Description of your changes"

# Push to GitHub
git push
```

## Cloning on Another Machine

If you want to work on this project from another computer:

```bash
# Clone the repository
git clone https://github.com/YOUR_USERNAME/REPO_NAME.git
cd REPO_NAME

# Set up backend
cd backend
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt

# Create .env file (you'll need to add your MongoDB credentials)
cp .env.example .env
# Then edit .env with your actual credentials

# Run the server
uvicorn app:app --reload
```

## Troubleshooting

### Authentication Issues

If you get authentication errors, you may need to:

1. **Use Personal Access Token** (recommended):
   - Go to GitHub Settings → Developer settings → Personal access tokens
   - Generate a new token with `repo` permissions
   - Use it as password when pushing

2. **Or use SSH**:
   ```bash
   git remote set-url origin git@github.com:YOUR_USERNAME/REPO_NAME.git
   ```

### Large Files

If you accidentally committed large files:
```bash
# Remove from git (but keep locally)
git rm --cached backend/venv/ -r

# Commit the removal
git commit -m "Remove venv from git"

# Push
git push
```

