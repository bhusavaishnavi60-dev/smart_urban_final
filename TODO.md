# Vercel Deployment TODO List

- [x] Create `vercel.json` - Vercel configuration
- [x] Create `api/index.py` - Vercel serverless function entry point
- [x] Create `api/db.py` - JSON-based database helper
- [x] Update `requirements.txt` - Removed gunicorn, added vercel
- [x] Delete `Procfile` - Not needed for Vercel

Note: This implementation uses JSON file storage instead of SQLite for Vercel compatibility.
