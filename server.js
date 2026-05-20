import express from 'express';
import cors from 'cors';
import path from 'path';
import { fileURLToPath } from 'url';
import dotenv from 'dotenv';
import multer from 'multer';

dotenv.config();

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

const app = express();
const PORT = process.env.PORT || 3000;

// IMPORTANT: fallback updated to latest backend API v2
const API_BASE_URL =
  process.env.REACT_APP_API_URL || 'https://rag-system-api-v2.onrender.com';

// Multer is needed to receive file uploads from frontend
const upload = multer({ storage: multer.memoryStorage() });

// ─── MIDDLEWARE ─────────────────────────────────────────

app.use(cors());
app.use(express.json());
app.use(express.urlencoded({ extended: true }));
app.use(express.static('public'));

// ─── LOGGING MIDDLEWARE ─────────────────────────────────

app.use((req, res, next) => {
  if (
    req.method !== 'GET' ||
    req.path.startsWith('/api') ||
    req.path === '/query' ||
    req.path === '/upload'
  ) {
    console.log(`📡 ${req.method} ${req.path}`);
  }
  next();
});

// ─── API PROXY ROUTES ────────────────────────────────────

/**
 * Proxy for /query endpoint.
 *
 * Frontend can send:
 *   { query_text: "..." }
 *   { data: "..." }
 *   { query: "..." }
 *   { question: "..." }
 *
 * Backend expects:
 *   application/x-www-form-urlencoded
 *   query_text=<question>
 */
app.post('/query', async (req, res) => {
  try {
    console.log('🔍 Proxying /query to', API_BASE_URL + '/query');

    const authHeader = req.headers.authorization;

    if (!authHeader) {
      return res.status(401).json({
        detail: 'Authorization token missing in frontend request'
      });
    }

    const queryText =
      req.body.query_text ||
      req.body.data ||
      req.body.query ||
      req.body.question ||
      '';

    if (!queryText.trim()) {
      return res.status(400).json({
        detail: 'Query text is missing'
      });
    }

    const formData = new URLSearchParams();
    formData.append('query_text', queryText);

    const response = await fetch(`${API_BASE_URL}/query`, {
      method: 'POST',
      headers: {
        Authorization: authHeader,
        'Content-Type': 'application/x-www-form-urlencoded'
      },
      body: formData.toString()
    });

    const responseText = await response.text();

    if (!response.ok) {
      console.error(
        `❌ Query proxy error: Backend returned ${response.status}: ${responseText}`
      );
      return res.status(response.status).send(responseText);
    }

    try {
      const data = JSON.parse(responseText);
      console.log('✅ Query response received');
      return res.json(data);
    } catch {
      return res.send(responseText);
    }
  } catch (error) {
    console.error('❌ Query proxy error:', error.message);
    return res.status(500).json({
      error: error.message,
      details: 'Failed to proxy query to backend'
    });
  }
});

/**
 * Proxy for /upload endpoint.
 *
 * Frontend sends:
 *   multipart/form-data with file
 *
 * Backend expects:
 *   multipart/form-data with file
 */
app.post('/upload', upload.single('file'), async (req, res) => {
  try {
    console.log('📤 Proxying /upload to', API_BASE_URL + '/upload');

    const authHeader = req.headers.authorization;

    if (!authHeader) {
      return res.status(401).json({
        detail: 'Authorization token missing in upload request'
      });
    }

    if (!req.file) {
      return res.status(400).json({
        detail: 'No file received by frontend proxy'
      });
    }

    const formData = new FormData();

    const blob = new Blob([req.file.buffer], {
      type: req.file.mimetype
    });

    formData.append('file', blob, req.file.originalname);

    // Forward any additional form fields if present
    for (const [key, value] of Object.entries(req.body || {})) {
      formData.append(key, value);
    }

    const response = await fetch(`${API_BASE_URL}/upload`, {
      method: 'POST',
      headers: {
        Authorization: authHeader
      },
      body: formData
    });

    const responseText = await response.text();

    if (!response.ok) {
      console.error(
        `❌ Upload proxy error: Backend returned ${response.status}: ${responseText}`
      );
      return res.status(response.status).send(responseText);
    }

    try {
      const data = JSON.parse(responseText);
      console.log('✅ Upload successful');
      return res.json(data);
    } catch {
      return res.send(responseText);
    }
  } catch (error) {
    console.error('❌ Upload proxy error:', error.message);
    return res.status(500).json({
      error: error.message,
      details: 'Failed to proxy upload to backend'
    });
  }
});

/**
 * Proxy for /health endpoint.
 */
app.get('/health', async (req, res) => {
  try {
    const response = await fetch(`${API_BASE_URL}/health`);
    const data = await response.json();
    return res.json(data);
  } catch (error) {
    return res.status(503).json({
      status: 'offline',
      error: error.message
    });
  }
});

/**
 * Proxy for /api/* endpoints.
 *
 * Handles:
 *   /api/auth/login
 *   /api/auth/register
 *   /api/team/members
 *   etc.
 */
app.all('/api/*', async (req, res) => {
  try {
    const endpoint = req.url.replace('/api', '');
    const fullUrl = `${API_BASE_URL}/api${endpoint}`;

    console.log(`🔗 Proxying ${req.method} ${endpoint}`);

    const headers = {
      'Content-Type': 'application/json',
      ...Object.fromEntries(
        Object.entries(req.headers).filter(
          ([key]) => !['host', 'connection', 'content-length'].includes(key.toLowerCase())
        )
      )
    };

    const response = await fetch(fullUrl, {
      method: req.method,
      headers,
      body: req.method !== 'GET' ? JSON.stringify(req.body) : undefined
    });

    const responseText = await response.text();

    try {
      const data = JSON.parse(responseText);
      return res.status(response.status).json(data);
    } catch {
      return res.status(response.status).send(responseText);
    }
  } catch (error) {
    console.error('❌ API proxy error:', error.message);
    return res.status(500).json({
      error: error.message,
      details: 'Failed to proxy API request to backend'
    });
  }
});

// ─── STATIC FILE SERVING ────────────────────────────────

/**
 * Serve dashboard HTML.
 */
app.get('/', (req, res) => {
  res.sendFile(path.join(__dirname, 'public', 'index.html'));
});

/**
 * Fallback for SPA routing.
 */
app.get('*', (req, res) => {
  res.sendFile(path.join(__dirname, 'public', 'index.html'));
});

// ─── ERROR HANDLING ─────────────────────────────────────

app.use((err, req, res, next) => {
  console.error('❌ Server error:', err);
  return res.status(500).json({
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