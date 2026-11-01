
import { useEffect, useState } from 'react'
import {
  uploadDocument,
  getDocuments,
  deleteDocument,
  askQuestion,
} from '../services/api'

export default function DocumentAssistant() {
  const [documents, setDocuments] = useState([])
  const [selectedFile, setSelectedFile] = useState(null)
  const [schemeId, setSchemeId] = useState('')
  const [selectedDocument, setSelectedDocument] = useState('')
  const [question, setQuestion] = useState('')
  const [answerData, setAnswerData] = useState(null)

  const [loadingDocuments, setLoadingDocuments] = useState(true)
  const [uploading, setUploading] = useState(false)
  const [asking, setAsking] = useState(false)
  const [deletingId, setDeletingId] = useState(null)

  const [error, setError] = useState('')
  const [success, setSuccess] = useState('')

  async function loadDocuments() {
    setLoadingDocuments(true)

    try {
      const data = await getDocuments()

      const items = Array.isArray(data)
        ? data
        : data?.documents || data?.items || []

      setDocuments(items)
    } catch (err) {
      setError(err.message || 'Could not load documents.')
    } finally {
      setLoadingDocuments(false)
    }
  }

  useEffect(() => {
    loadDocuments()
  }, [])

  function handleFileChange(event) {
    const file = event.target.files?.[0]

    setError('')
    setSuccess('')
    setSelectedFile(null)

    if (!file) return

    const isPdf =
      file.type === 'application/pdf' ||
      file.name.toLowerCase().endsWith('.pdf')

    if (!isPdf) {
      setError('Please select a PDF file.')
      event.target.value = ''
      return
    }

    if (file.size > 15 * 1024 * 1024) {
      setError('PDF size must not exceed 15 MB.')
      event.target.value = ''
      return
    }

    setSelectedFile(file)
  }

  async function handleUpload(event) {
    event.preventDefault()

    if (!selectedFile) {
      setError('Please choose a PDF file first.')
      return
    }

    setUploading(true)
    setError('')
    setSuccess('')

    try {
      await uploadDocument(selectedFile, schemeId.trim())

      setSuccess('Document uploaded and indexed successfully.')
      setSelectedFile(null)
      setSchemeId('')

      const fileInput = document.getElementById('scheme-pdf')
      if (fileInput) fileInput.value = ''

      await loadDocuments()
    } catch (err) {
      setError(err.message || 'Document upload failed.')
    } finally {
      setUploading(false)
    }
  }

  async function handleDelete(documentId) {
    const confirmed = window.confirm(
      'Are you sure you want to delete this document?',
    )

    if (!confirmed) return

    setDeletingId(documentId)
    setError('')
    setSuccess('')

    try {
      await deleteDocument(documentId)

      setDocuments((current) =>
        current.filter((item) => item.document_id !== documentId),
      )

      if (selectedDocument === documentId) {
        setSelectedDocument('')
      }

      setSuccess('Document deleted successfully.')
    } catch (err) {
      setError(err.message || 'Could not delete document.')
    } finally {
      setDeletingId(null)
    }
  }

  async function handleAskQuestion(event) {
    event.preventDefault()

    if (!question.trim()) {
      setError('Please enter a question.')
      return
    }

    setAsking(true)
    setError('')
    setSuccess('')
    setAnswerData(null)

    try {
      const result = await askQuestion({
        question: question.trim(),
        document_id: selectedDocument || undefined,
      })

      setAnswerData(result)
    } catch (err) {
      setError(err.message || 'Could not get an answer.')
    } finally {
      setAsking(false)
    }
  }

  function getDocumentName(item) {
    return (
      item.document_name ||
      item.original_filename ||
      item.document_id ||
      'Untitled document'
    )
  }

  function getStatusClass(status) {
    if (status === 'complete') return 'da-status--complete'
    if (status === 'partial') return 'da-status--partial'
    return 'da-status--insufficient'
  }

  return (
    <section className="document-assistant section--alt" id="document-assistant">
      <div className="container">

        <div className="da-heading">
          <span className="da-eyebrow">AI-POWERED DOCUMENT ASSISTANT</span>
          <h2>
            Understand Government Schemes with{' '}
            <span className="grad">AI Assistance</span>
          </h2>
          <p>
            Upload official government scheme guidelines, ask questions,
            and get answers supported by document references and page numbers.
          </p>
        </div>

        {error && (
          <div className="da-alert da-alert--error" role="alert">
            {error}
          </div>
        )}

        {success && (
          <div className="da-alert da-alert--success" role="status">
            {success}
          </div>
        )}

        <div className="da-grid">

          {/* PDF Upload */}
          <div className="da-panel">
            <div className="da-panel-heading">
              <span className="da-icon">↑</span>
              <div>
                <h3>Upload Government PDF</h3>
                <p>Add an official scheme guideline document.</p>
              </div>
            </div>

            <form onSubmit={handleUpload}>
              <label className="da-field">
                Scheme ID
                <input
                  type="text"
                  value={schemeId}
                  onChange={(event) => setSchemeId(event.target.value)}
                  placeholder="Optional scheme ID"
                />
              </label>

              <label className="da-upload-box" htmlFor="scheme-pdf">
                <span className="da-upload-icon">⇧</span>
                <strong>
                  {selectedFile
                    ? selectedFile.name
                    : 'Choose a PDF document'}
                </strong>
                <span>PDF format · Maximum 15 MB</span>
                <input
                  id="scheme-pdf"
                  type="file"
                  accept=".pdf,application/pdf"
                  onChange={handleFileChange}
                />
              </label>

              {selectedFile && (
                <p className="da-file-info">
                  Selected size: {(selectedFile.size / (1024 * 1024)).toFixed(2)} MB
                </p>
              )}

              <button
                className="btn btn--primary da-full-button"
                type="submit"
                disabled={uploading || !selectedFile}
              >
                {uploading ? 'Uploading and indexing...' : 'Upload Document'}
              </button>
            </form>

            <p className="da-note">
              Only upload official documents that you are authorized to use.
              Scanned PDFs may not be supported yet.
            </p>
          </div>

          {/* Document Library */}
          <div className="da-panel">
            <div className="da-panel-heading">
              <span className="da-icon">▤</span>
              <div>
                <h3>Document Library</h3>
                <p>Your uploaded and indexed documents.</p>
              </div>
              <button
                type="button"
                className="da-refresh"
                onClick={loadDocuments}
                disabled={loadingDocuments}
                aria-label="Refresh document list"
              >
                ↻
              </button>
            </div>

            {loadingDocuments ? (
              <p className="da-empty">Loading documents...</p>
            ) : documents.length === 0 ? (
              <div className="da-empty">
                <span>▤</span>
                <strong>No documents uploaded yet</strong>
                <p>Upload a government PDF to get started.</p>
              </div>
            ) : (
              <div className="da-document-list">
                {documents.map((item) => {
                  const id = item.document_id

                  return (
                    <div className="da-document" key={id}>
                      <div className="da-document-info">
                        <strong>{getDocumentName(item)}</strong>
                        <span>
                          {item.total_pages ?? '—'} pages
                          {' · '}
                          {item.total_chunks ?? '—'} chunks
                        </span>
                        <span className="da-index-status">
                          {item.status || 'indexed'}
                        </span>
                      </div>

                      <button
                        type="button"
                        className="da-delete"
                        onClick={() => handleDelete(id)}
                        disabled={deletingId === id}
                        aria-label={`Delete ${getDocumentName(item)}`}
                      >
                        {deletingId === id ? 'Deleting...' : 'Delete'}
                      </button>
                    </div>
                  )
                })}
              </div>
            )}
          </div>
        </div>

        {/* Question and Answer */}
        <div className="da-chat-panel">
          <div className="da-panel-heading">
            <span className="da-icon da-icon--rose">✦</span>
            <div>
              <h3>Ask Your Scheme Question</h3>
              <p>Get answers based on your indexed documents.</p>
            </div>
          </div>

          <form onSubmit={handleAskQuestion} className="da-question-form">
            <label className="da-field">
              Search within
              <select
                value={selectedDocument}
                onChange={(event) => setSelectedDocument(event.target.value)}
              >
                <option value="">All uploaded documents</option>
                {documents.map((item) => (
                  <option
                    key={item.document_id}
                    value={item.document_id}
                  >
                    {getDocumentName(item)}
                  </option>
                ))}
              </select>
            </label>

            <label className="da-field">
              Your question
              <textarea
                value={question}
                onChange={(event) => setQuestion(event.target.value)}
                placeholder="Example: What documents are required to apply for this scheme?"
                rows={3}
              />
            </label>

            <button
              type="submit"
              className="btn btn--primary"
              disabled={asking || !question.trim()}
            >
              {asking ? 'Finding an answer...' : 'Ask Question'}
            </button>
          </form>

          {answerData && (
            <div className="da-answer" aria-live="polite">
              <div className="da-answer-heading">
                <h4>Assistant Response</h4>
                <span
                  className={`da-status ${getStatusClass(answerData.answer_status)}`}
                >
                  {answerData.answer_status || 'insufficient'}
                </span>
              </div>

              <p className="da-answer-text">{answerData.answer}</p>

              {answerData.insufficient_information && (
                <p className="da-warning">
                  The available documents do not provide enough evidence
                  for a complete answer. Please verify with the official
                  scheme authority.
                </p>
              )}

              {answerData.sources?.length > 0 && (
                <div className="da-sources">
                  <h4>Sources and References</h4>

                  {answerData.sources.map((source, index) => (
                    <div
                      className="da-source"
                      key={`${source.document_id || index}-${source.page_number || index}`}
                    >
                      <strong>
                        {source.document_name || 'Government document'}
                      </strong>
                      <span>Page {source.page_number ?? 'Not specified'}</span>

                      {(source.excerpt || source.text) && (
                        <p>{source.excerpt || source.text}</p>
                      )}

                      {source.source_url && (
                        <a
                          href={source.source_url}
                          target="_blank"
                          rel="noreferrer"
                        >
                          View original document ↗
                        </a>
                      )}
                    </div>
                  ))}
                </div>
              )}
            </div>
          )}
        </div>

        <p className="da-disclaimer">
          This assistant explains information found in uploaded documents.
          It does not determine scheme eligibility or replace official
          government guidance.
        </p>

      </div>
    </section>
  )
}
