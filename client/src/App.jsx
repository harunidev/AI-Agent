import { useState, useEffect } from 'react'
import './App.css'
import Prism from 'prismjs'
import 'prismjs/themes/prism-tomorrow.css'
import 'prismjs/components/prism-python'

function App() {
  const [code, setCode] = useState("")
  const [coverage, setCoverage] = useState(null)
  const [generatedTests, setGeneratedTests] = useState("")
  const [loading, setLoading] = useState(false)

  // Highlight code whenever generatedTests changes
  useEffect(() => {
    if (generatedTests) {
      Prism.highlightAll()
    }
  }, [generatedTests])

  const handleGenerate = async () => {
    if (!code.trim()) {
      alert("Please enter code first!")
      return
    }

    setLoading(true)
    setCoverage(null)
    setGeneratedTests("")

    try {
      const response = await fetch('http://localhost:8000/generate-tests', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          code_content: code,
          file_name: "dynamic_upload.py",
          language: "python"
        })
      })

      const data = await response.json()

      if (response.ok) {
        setGeneratedTests(data.test_code)
        // Ensure coverage is a number
        setCoverage(Math.round(data.coverage_estimate || 0))
      } else {
        setGeneratedTests(`# Error: ${data.detail || "Unknown Server Error"}`)
      }

    } catch (error) {
      console.error("API Error:", error)
      setGeneratedTests(`# Connectivity Error: Ensure Backend is running on port 8000\n# ${error.message}`)
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="app-container">
      <header className="header">
        <div className="container flex-between">
          <div className="logo">
            <h1>⚡ AI4SE <span style={{ fontSize: '0.5em', opacity: 0.8 }}>Test Generator</span></h1>
          </div>
          <div className="status">
            <span style={{ color: 'var(--color-text-muted)', fontSize: '0.95rem' }}>System Ready</span>
          </div>
        </div>
      </header>

      <main className="main-content">
        <div className={`grid-layout ${code.trim() || generatedTests ? 'expanded' : 'compact'}`}>

          {/* Left Panel: Input */}
          <section className="input-section">
            <div className="card">
              <div className="flex-between" style={{ marginBottom: '1rem' }}>
                <h3>Source Code</h3>
                <span className="badge">Python</span>
              </div>
              <textarea
                className="input-area"
                rows={code.trim() ? 20 : 8}
                placeholder="Paste your Python code here..."
                value={code}
                onChange={(e) => setCode(e.target.value)}
              />
              <div style={{ marginTop: '1rem', display: 'flex', gap: '1rem', flexWrap: 'wrap' }}>
                <button className="btn btn-primary" onClick={handleGenerate} disabled={loading}>
                  {loading ? '⚡ Generating...' : '🚀 Generate Tests'}
                </button>
                <button className="btn btn-glow">📁 Upload File</button>
              </div>
            </div>
          </section>

          {/* Right Panel: Output */}
          <section className={`output-section ${generatedTests || loading ? 'visible' : ''}`}>
            <div className="card">
              <div className="flex-between" style={{ marginBottom: '1rem' }}>
                <h3>Analysis Results</h3>
                {coverage !== null && (
                  <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
                    <span style={{ color: 'var(--color-text-muted)' }}>Coverage:</span>
                    <span style={{
                      color: coverage >= 90 ? 'var(--color-success)' : 'var(--color-warning)',
                      fontWeight: 'bold',
                      fontSize: '1.2rem'
                    }}>
                      {coverage}%
                    </span>
                  </div>
                )}
              </div>

              {loading ? (
                <div className="loading-container">
                  <div className="ai-loader">
                    <div className="loader-circle"></div>
                    <div className="loader-circle"></div>
                    <div className="loader-circle"></div>
                  </div>
                  <p className="loading-text">AI is analyzing your code...</p>
                  <p className="loading-subtext">Generating comprehensive tests with edge cases</p>
                </div>
              ) : generatedTests ? (
                <div className="results-view">
                  {/* Analysis Summary */}
                  <div className="analysis-summary">
                    <h4 style={{ marginTop: 0, marginBottom: '1rem', color: 'var(--color-text-main)' }}>
                      📊 Test Analysis Summary
                    </h4>

                    <div className="metrics-grid">
                      <div className="metric-card">
                        <div className="metric-icon">🎯</div>
                        <div className="metric-value">{coverage}%</div>
                        <div className="metric-label">Code Coverage</div>
                      </div>

                      <div className="metric-card">
                        <div className="metric-icon">🧪</div>
                        <div className="metric-value">{generatedTests.split('def test_').length - 1}</div>
                        <div className="metric-label">Tests Generated</div>
                      </div>

                      <div className="metric-card">
                        <div className="metric-icon">⚡</div>
                        <div className="metric-value">{generatedTests.split('# Tests for').length - 1}</div>
                        <div className="metric-label">Functions Tested</div>
                      </div>

                      <div className="metric-card">
                        <div className="metric-icon">{coverage >= 90 ? '✅' : '⚠️'}</div>
                        <div className="metric-value">{coverage >= 90 ? 'Excellent' : 'Good'}</div>
                        <div className="metric-label">Quality Rating</div>
                      </div>
                    </div>

                    {/* Test Types Breakdown */}
                    <div className="test-breakdown">
                      <h5 style={{ marginBottom: '0.75rem', color: 'var(--color-text-main)' }}>
                        🔍 Test Coverage Breakdown
                      </h5>
                      <div className="breakdown-items">
                        <div className="breakdown-item">
                          <span className="breakdown-icon">✓</span>
                          <span>Basic Functionality Tests</span>
                          <span className="breakdown-badge">{generatedTests.split('test_').filter(t => t.includes('_basic')).length}</span>
                        </div>
                        <div className="breakdown-item">
                          <span className="breakdown-icon">✓</span>
                          <span>Edge Case Tests</span>
                          <span className="breakdown-badge">{generatedTests.split('test_').filter(t => t.includes('_edge_cases')).length}</span>
                        </div>
                        <div className="breakdown-item">
                          <span className="breakdown-icon">✓</span>
                          <span>Type Validation Tests</span>
                          <span className="breakdown-badge">{generatedTests.split('test_').filter(t => t.includes('_type_validation')).length}</span>
                        </div>
                        <div className="breakdown-item">
                          <span className="breakdown-icon">✓</span>
                          <span>Branch Coverage Tests</span>
                          <span className="breakdown-badge">{generatedTests.split('test_').filter(t => t.includes('_branches')).length}</span>
                        </div>
                        <div className="breakdown-item">
                          <span className="breakdown-icon">✓</span>
                          <span>Error Handling Tests</span>
                          <span className="breakdown-badge">{generatedTests.split('test_').filter(t => t.includes('_error_handling')).length}</span>
                        </div>
                      </div>
                    </div>
                  </div>

                  {/* Collapsible Test Code */}
                  <details className="test-code-details" open>
                    <summary className="test-code-summary">
                      <span>📝 View Generated Test Code</span>
                      <span className="toggle-icon">▼</span>
                    </summary>
                    <pre className="code-block">
                      <code className="language-python">{generatedTests}</code>
                    </pre>
                  </details>

                  {coverage && coverage < 90 && (
                    <div style={{
                      marginTop: '1rem',
                      padding: '1rem',
                      background: 'rgba(245, 158, 11, 0.1)',
                      borderLeft: '4px solid var(--color-warning)',
                      borderRadius: '8px'
                    }}>
                      <strong>⚠️ Warning:</strong> Coverage is under 90%. Consider adding more edge case tests.
                    </div>
                  )}
                </div>
              ) : (
                <div className="empty-state">
                  <div className="empty-icon">🤖</div>
                  <p className="empty-text">AI Waiting for Input...</p>
                  <p className="empty-subtext">Paste your code and click "Generate Tests"</p>
                </div>
              )}
            </div>
          </section>

        </div>
      </main>
    </div>
  )
}

export default App
