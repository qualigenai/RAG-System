import express from 'express';
import cors from 'cors';
import path from 'path';
import { fileURLToPath } from 'url';
import dotenv from 'dotenv';

dotenv.config();

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

const app = express();
const PORT = process.env.PORT || 3000;
const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000';

// ─── MIDDLEWARE ─────────────────────────────────────────

app.use(cors());
app.use(express.json());
app.use(express.urlencoded({ extended: true }));
app.use(express.static('public'));

// ─── LOGGING MIDDLEWARE ─────────────────────────────────

app.use((req, res, next) => {
  if (req.method !== 'GET' || req.path.startsWith('/api') || req.path === '/query' || req.path === '/upload') {
    console.log(`📡 ${req.method} ${req.path}`);
  }
  next();
});

// ─── API PROXY ROUTES ────────────────────────────────────

/**
 * Proxy for /query endpoint (RAG queries)
 * Frontend sends: POST /query with { data: "query text" }
 * Backend expects: POST /query with form data or JSON
 */
app.post('/query', async (req, res) => {
  try {
    console.log('🔍 Proxying /query to', API_BASE_URL + '/query');

    // Backend expects form-data with 'data' field
    const formData = new URLSearchParams();
    formData.append('data', req.body.data || req.body.query || '');

    const response = await fetch(`${API_BASE_URL}/query`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/x-www-form-urlencoded',
      },
      body: formData.toString()
    });

    if (!response.ok) {
      throw new Error(`Backend returned ${response.status}: ${response.statusText}`);
    }

    const data = await response.json();
    console.log('✅ Query response received');
    res.json(data);
  } catch (error) {
    console.error('❌ Query proxy error:', error.message);
    res.status(500).json({
      error: error.message,
      details: 'Failed to proxy query to backend'
    });
  }
});

/**
 * Proxy for /upload endpoint (file uploads)
 * Frontend sends: POST /upload with FormData containing file
 * Backend expects: POST /upload with multipart/form-data
 */
app.post('/upload', async (req, res) => {
  try {
    console.log('📤 Proxying /upload to', API_BASE_URL + '/upload');

    const response = await fetch(`${API_BASE_URL}/upload`, {
      method: 'POST',
      headers: req.headers,
      body: req.body
    });

    if (!response.ok) {
      throw new Error(`Backend returned ${response.status}: ${response.statusText}`);
    }

    const data = await response.json();
    console.log('✅ Upload successful');
    res.json(data);
  } catch (error) {
    console.error('❌ Upload proxy error:', error.message);
    res.status(500).json({
      error: error.message,
      details: 'Failed to proxy upload to backend'
    });
  }
});

/**
 * Proxy for /health endpoint (backend health check)
 */
app.get('/health', async (req, res) => {
  try {
    const response = await fetch(`${API_BASE_URL}/health`);
    const data = await response.json();
    res.json(data);
  } catch (error) {
    res.status(503).json({ status: 'offline', error: error.message });
  }
});

/**
 * Proxy for /api/* endpoints (auth, team, settings, etc.)
 * Handles: /api/auth/login, /api/auth/register, /api/team/members, etc.
 */
app.all('/api/*', async (req, res) => {
  try {
    const endpoint = req.url.replace('/api', '');
    const fullUrl = `${API_BASE_URL}/api${endpoint}`;

    console.log(`🔗 Proxying ${req.method} ${endpoint}`);

    const response = await fetch(fullUrl, {
      method: req.method,
      headers: {
        'Content-Type': 'application/json',
        ...Object.fromEntries(
          Object.entries(req.headers).filter(([key]) =>
            !['host', 'connection'].includes(key.toLowerCase())
          )
        )
      },
      body: req.method !== 'GET' ? JSON.stringify(req.body) : undefined
    });

    if (!response.ok && response.status !== 401 && response.status !== 403) {
      throw new Error(`Backend returned ${response.status}`);
    }

    const data = await response.json();
    res.status(response.status).json(data);
  } catch (error) {
    console.error('❌ API proxy error:', error.message);
    res.status(500).json({
      error: error.message,
      details: 'Failed to proxy API request to backend'
    });
  }
});

// ─── STATIC FILE SERVING ────────────────────────────────

/**
 * Serve dashboard HTML
 */
app.get('/', (req, res) => {
  res.sendFile(path.join(__dirname, 'public', 'index.html'));
});

/**
 * Fallback for SPA routing
 * All unknown routes serve index.html (for client-side routing)
 */
app.get('*', (req, res) => {
  res.sendFile(path.join(__dirname, 'public', 'index.html'));
});

// ─── ERROR HANDLING ─────────────────────────────────────

app.use((err, req, res, next) => {
  console.error('❌ Server error:', err);
  res.status(500).json({
    error: 'Internal server error',
    details: err.message
  });
});

// ─── START SERVER ───────────────────────────────────────

const server = app.listen(PORT, '0.0.0.0', () => {
  console.log('\n');
  console.log('╔═══════════════════════════════════════════════════════════╗');
  console.log('║         🚀 QualiGenAI RAG System - Frontend Server         ║');
  console.log('╚═══════════════════════════════════════════════════════════╝');
  console.log('\n');
  console.log(`✅ Frontend server running on http://localhost:${PORT}`);
  console.log(`🔗 Backend API endpoint: ${API_BASE_URL}`);
  console.log('\n');
  console.log('📡 Available proxy routes:');
  console.log(`   POST /query          → ${API_BASE_URL}/query`);
  console.log(`   POST /upload         → ${API_BASE_URL}/upload`);
  console.log(`   GET  /health         → ${API_BASE_URL}/health`);
  console.log(`   ALL  /api/*          → ${API_BASE_URL}/api/*`);
  console.log('\n');
  console.log('🌐 Open in browser: http://localhost:3000');
  console.log('\n');
});

// Handle graceful shutdown
process.on('SIGTERM', () => {
  console.log('\n📴 Shutting down gracefully...');
  server.close(() => {
    console.log('✅ Server closed');
    process.exit(0);
  });
});

process.on('SIGINT', () => {
  console.log('\n📴 Shutting down gracefully...');
  server.close(() => {
    console.log('✅ Server closed');
    process.exit(0);
  });
});