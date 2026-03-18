#!/bin/bash

set -e

echo "🚀 Starting RAG System v1.5..."

# Initialize database
echo "📊 Initializing database..."
python -c "from src.database.models import Base; from src.database.session import engine; Base.metadata.create_all(bind=engine)" || true

echo "✅ Database ready"

# Start backend in background
echo "🔧 Starting FastAPI backend..."
python -m uvicorn src.api.main:app --host 0.0.0.0 --port 8000 > backend.log 2>&1 &
BACKEND_PID=$!

# Wait for backend to start
sleep 3

# Check backend health
echo "🏥 Checking backend health..."
for i in {1..30}; do
  if curl -f http://localhost:8000/health > /dev/null 2>&1; then
    echo "✅ Backend is healthy"
    break
  fi
  echo "⏳ Waiting for backend... ($i/30)"
  sleep 1
done

# Start frontend
echo "🎨 Starting Streamlit frontend..."
streamlit run src/ui/main.py --server.port=8501 --server.address=0.0.0.0

# Keep script running
wait $BACKEND_PID
```

---

### **STEP 5: Create .dockerignore**

In project root, create: `.dockerignore`
```
__pycache__/
*.pyc
*.pyo
*.pyd
.Python
env/
venv/
.venv
.git
.gitignore
.env
.env.local
.DS_Store
*.log
test_reports/
htmlcov/
.coverage
.pytest_cache/
.mypy_cache/
node_modules/
.vscode/
.idea/
*.swp
*.swo
*~
.gradle/
.terraform/