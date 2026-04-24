// ============================================================================
// RAG System Dashboard - Fixed for Babel CDN
// ============================================================================

// Wait for React to be available
setTimeout(function() {
  const React = window.React;
  const ReactDOM = window.ReactDOM;

  if (!React || !ReactDOM) {
    console.error('React or ReactDOM not loaded');
    return;
  }

  const { useState, useEffect, useRef } = React;
  const e = React.createElement;

  // ─── SIMPLE APP ─────────────────────────────────────────────
  function App() {
    const [query, setQuery] = useState('');
    const [results, setResults] = useState([]);
    const [loading, setLoading] = useState(false);
    const [activeTab, setActiveTab] = useState('search');

    const handleSearch = () => {
      if (!query.trim()) return;
      setLoading(true);
      setTimeout(() => {
        setResults([
          {
            id: 1,
            question: query,
            answer: 'This is a demo answer. Connect to your FastAPI backend to get real results.',
            sources: [
              { name: 'document.pdf', confidence: 85 },
              { name: 'readme.md', confidence: 72 }
            ]
          }
        ]);
        setLoading(false);
      }, 1000);
    };

    const handleKeyPress = (e) => {
      if (e.key === 'Enter') handleSearch();
    };

    return e('div', { style: {
      display: 'flex',
      height: '100vh',
      background: '#0A1628',
      color: '#E2E8F0',
      fontFamily: "'Inter', sans-serif"
    }},
      // Sidebar
      e('div', { style: {
        width: '240px',
        background: '#080F1E',
        borderRight: '1px solid #1E3A5F',
        padding: '20px',
        display: 'flex',
        flexDirection: 'column',
        gap: '20px'
      }},
        e('div', { style: { fontSize: '18px', fontWeight: 'bold' } }, '🚀 QualiGenAI'),
        e('div', { style: { fontSize: '12px', color: '#64748B' } }, 'RAG System v1.5'),
        e('nav', { style: { display: 'flex', flexDirection: 'column', gap: '8px' } },
          e('div', {
            onClick: () => setActiveTab('search'),
            style: {
              padding: '10px',
              background: activeTab === 'search' ? '#0F1E35' : 'transparent',
              borderLeft: activeTab === 'search' ? '3px solid #FF6B35' : '3px solid transparent',
              cursor: 'pointer',
              borderRadius: '4px'
            }
          }, '🔍 Search'),
          e('div', {
            onClick: () => setActiveTab('upload'),
            style: {
              padding: '10px',
              background: activeTab === 'upload' ? '#0F1E35' : 'transparent',
              borderLeft: activeTab === 'upload' ? '3px solid #FF6B35' : '3px solid transparent',
              cursor: 'pointer',
              borderRadius: '4px'
            }
          }, '📤 Upload'),
          e('div', {
            onClick: () => setActiveTab('settings'),
            style: {
              padding: '10px',
              background: activeTab === 'settings' ? '#0F1E35' : 'transparent',
              borderLeft: activeTab === 'settings' ? '3px solid #FF6B35' : '3px solid transparent',
              cursor: 'pointer',
              borderRadius: '4px'
            }
          }, '⚙️ Settings')
        )
      ),

      // Main Content
      e('div', { style: { flex: 1, display: 'flex', flexDirection: 'column', overflow: 'hidden' }},
        // Header
        e('div', { style: {
          background: '#080F1E',
          borderBottom: '1px solid #1E3A5F',
          padding: '20px',
          display: 'flex',
          gap: '12px',
          alignItems: 'center'
        }},
          e('input', {
            type: 'text',
            value: query,
            onChange: (e) => setQuery(e.target.value),
            onKeyPress: handleKeyPress,
            placeholder: 'Ask your documents...',
            style: {
              flex: 1,
              padding: '12px',
              background: '#0A1628',
              border: '1px solid #1E3A5F',
              borderRadius: '8px',
              color: '#E2E8F0',
              outline: 'none'
            }
          }),
          e('button', {
            onClick: handleSearch,
            disabled: loading,
            style: {
              padding: '12px 24px',
              background: loading ? '#999' : '#FF6B35',
              color: '#fff',
              border: 'none',
              borderRadius: '8px',
              cursor: loading ? 'not-allowed' : 'pointer',
              fontWeight: 'bold'
            }
          }, loading ? '⏳ Searching...' : '🔍 Search')
        ),

        // Content
        e('div', { style: {
          flex: 1,
          overflow: 'auto',
          padding: '20px'
        }},
          activeTab === 'search' ? e('div', {},
            e('div', { style: { marginBottom: '20px' } },
              e('h2', { style: { fontSize: '20px', marginBottom: '10px' } }, 'Search Documents'),
              e('p', { style: { color: '#94A3B8' } }, 'Enter a query above to search your indexed documents')
            ),
            loading ? e('div', { style: { padding: '20px', textAlign: 'center' } },
              e('div', { style: { fontSize: '14px', color: '#94A3B8' } }, '⏳ Searching...')
            ) : null,
            results.length > 0 ? e('div', { style: { display: 'flex', flexDirection: 'column', gap: '12px' } },
              results.map(result => e('div', { key: result.id, style: {
                background: '#0F1E35',
                border: '1px solid #1E3A5F',
                borderRadius: '8px',
                padding: '16px',
                cursor: 'pointer'
              }},
                e('div', { style: { fontSize: '14px', fontWeight: 'bold', marginBottom: '8px' } }, result.question),
                e('div', { style: { fontSize: '13px', color: '#CBD5E1', marginBottom: '12px' } }, result.answer),
                e('div', { style: { fontSize: '11px', color: '#64748B' } }, 'Sources:'),
                e('div', { style: { display: 'flex', gap: '8px', marginTop: '8px', flexWrap: 'wrap' } },
                  result.sources.map(src => e('div', { key: src.name, style: {
                    background: 'rgba(59,130,246,0.1)',
                    border: '1px solid rgba(59,130,246,0.2)',
                    borderRadius: '4px',
                    padding: '4px 8px',
                    fontSize: '11px'
                  }}, `${src.name} (${src.confidence}%)`)
                  )
                )
              ))
            ) : null
          ) : null,

          activeTab === 'upload' ? e('div', {},
            e('h2', { style: { fontSize: '20px', marginBottom: '10px' } }, 'Upload Documents'),
            e('div', { style: {
              border: '2px dashed #1E3A5F',
              borderRadius: '8px',
              padding: '40px',
              textAlign: 'center',
              cursor: 'pointer'
            }},
              e('div', { style: { fontSize: '24px', marginBottom: '10px' } }, '📤'),
              e('div', { style: { fontSize: '14px', marginBottom: '5px' } }, 'Drop files here or click to upload'),
              e('div', { style: { fontSize: '12px', color: '#64748B' } }, 'Supported: PDF, TXT, DOCX, CSV')
            )
          ) : null,

          activeTab === 'settings' ? e('div', {},
            e('h2', { style: { fontSize: '20px', marginBottom: '20px' } }, 'Settings'),
            e('div', { style: { background: '#0F1E35', border: '1px solid #1E3A5F', borderRadius: '8px', padding: '16px' } },
              e('div', { style: { marginBottom: '16px' } },
                e('div', { style: { fontSize: '14px', fontWeight: 'bold', marginBottom: '8px' } }, 'API Configuration'),
                e('div', { style: { fontSize: '12px', color: '#94A3B8' } }, 'API URL: http://localhost:8000')
              ),
              e('div', {
                e('div', { style: { fontSize: '14px', fontWeight: 'bold', marginBottom: '8px' } }, 'Status'),
                e('div', { style: { fontSize: '12px', color: '#22C55E' } }, '✅ Frontend running on port 3000')
              )
            )
          ) : null
        )
      )
    );
  }

  // Render the app
  ReactDOM.createRoot(document.getElementById('root')).render(React.createElement(App));

}, 1000); // Wait for all scripts to load
