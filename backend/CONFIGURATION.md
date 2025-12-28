# Configuration Guide

## FastAPI - No API Keys Needed! ✅

**Good news:** FastAPI doesn't require any API keys or authentication tokens. The API is ready to use as-is. 

> ⚠️ **Note:** If you want to add authentication later (API keys, JWT tokens, etc.), that can be added, but it's not required for the basic functionality.

---

## MongoDB - Connection Configuration

You need to create a `.env` file in the `backend/` directory with your MongoDB connection details.

### Option 1: Local MongoDB (No Authentication)

If you're running MongoDB locally without a password:

```env
MONGO_URI=mongodb://localhost:27017/
DB_NAME=hirely
```

**Replace:** Nothing! This is the default. Just make sure MongoDB is running locally.

---

### Option 2: Local MongoDB (With Authentication)

If your local MongoDB has a username and password:

```env
MONGO_URI=mongodb://YOUR_USERNAME:YOUR_PASSWORD@localhost:27017/
DB_NAME=hirely
```

**Replace:**
- `YOUR_USERNAME` → Your MongoDB username
- `YOUR_PASSWORD` → Your MongoDB password

**Example:**
```env
MONGO_URI=mongodb://admin:mypassword123@localhost:27017/
DB_NAME=hirely
```

---

### Option 3: MongoDB Atlas (Cloud) - Recommended for Production

If you're using MongoDB Atlas (free cloud database):

1. Go to https://www.mongodb.com/cloud/atlas
2. Create a free account and cluster
3. Get your connection string from Atlas:
   - Click "Connect" on your cluster
   - Choose "Connect your application"
   - Copy the connection string

```env
MONGO_URI=mongodb+srv://YOUR_USERNAME:YOUR_PASSWORD@cluster0.xxxxx.mongodb.net/
DB_NAME=hirely
```

**Replace:**
- `YOUR_USERNAME` → Your Atlas database username
- `YOUR_PASSWORD` → Your Atlas database password
- `cluster0.xxxxx.mongodb.net` → Your actual cluster URL (from Atlas)

**Example:**
```env
MONGO_URI=mongodb+srv://myuser:mypass123@cluster0.abc123.mongodb.net/
DB_NAME=hirely
```

> ⚠️ **Important:** Make sure to:
> - Replace `<password>` in the Atlas connection string with your actual password
> - Add your IP address to the Atlas whitelist (Network Access)
> - The database name (`hirely`) can be changed if you want a different name

---

## Quick Setup Steps

1. **Create the `.env` file:**
   ```bash
   cd backend
   touch .env
   ```

2. **Add your MongoDB connection string** (choose one option above)

3. **Test the connection:**
   ```bash
   uvicorn app:app --reload
   # Then visit: http://localhost:8000/health
   ```

---

## Summary

- **FastAPI:** No keys needed ✅
- **MongoDB:** Replace connection string in `.env` file based on your setup:
  - Local (no auth): `mongodb://localhost:27017/`
  - Local (with auth): `mongodb://username:password@localhost:27017/`
  - Atlas (cloud): `mongodb+srv://username:password@cluster.mongodb.net/`

