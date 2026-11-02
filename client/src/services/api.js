
/* Single place for all backend access. Base URL comes from Vite env config. */
const API_BASE_URL = (
  import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000'
).replace(/\/$/, '')

async function request(path, { signal } = {}) {
  let response

  try {
    response = await fetch(`${API_BASE_URL}${path}`, { signal })
  } catch (err) {
    if (err.name === 'AbortError') throw err

    throw new Error(
      `Could not reach the SchemeWise API at ${API_BASE_URL}.`,
      { cause: err },
    )
  }

  if (!response.ok) {
    throw new Error(
      `The API responded with an error (HTTP ${response.status}).`,
    )
  }

  return response.json()
}

// GET /api/schemes?search=...&state=...&category=...&beneficiary_group=...
// Expected response: { count, schemes: [...] }
export async function fetchSchemes(options = {}) {
  const {
    signal,
    search = '',
    state = '',
    category = '',
    beneficiary_group = '',
  } = options

  const params = new URLSearchParams()

  if (search.trim()) params.set('search', search.trim())
  if (state) params.set('state', state)
  if (category) params.set('category', category)
  if (beneficiary_group) {
    params.set('beneficiary_group', beneficiary_group)
  }

  const query = params.toString()
  const path = query ? `/api/schemes?${query}` : '/api/schemes'

  const data = await request(path, { signal })

  return Array.isArray(data?.schemes) ? data.schemes : []
}

export async function checkEligibility(profile) {
  let response

  try {
    response = await fetch(
      `${API_BASE_URL}/api/eligibility/check`,
      {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ profile }),
      },
    )
  } catch (err) {
    throw new Error(
      'Could not connect to the SchemeWise backend. Check whether FastAPI is running.',
      { cause: err },
    )
  }

  const data = await response.json().catch(() => ({}))

  if (!response.ok) {
    const detail = data.detail

    const message = Array.isArray(detail)
      ? detail.map((item) => item.msg).join(', ')
      : typeof detail === 'string'
        ? detail
        : `Request failed with HTTP ${response.status}.`

    throw new Error(message)
  }

  return data
}


// POST /api/documents/upload
// Upload an official government scheme PDF.
export async function uploadDocument(file, schemeId = '') {
  const formData = new FormData()
  formData.append('file', file)

  if (schemeId) {
    formData.append('scheme_id', schemeId)
  }

  let response

  try {
    response = await fetch(
      `${API_BASE_URL}/api/documents/upload`,
      {
        method: 'POST',
        body: formData,
      },
    )
  } catch (err) {
    throw new Error(
      'Could not connect to the SchemeWise backend.',
      { cause: err },
    )
  }

  const data = await response.json().catch(() => ({}))

  if (!response.ok) {
    const detail = data.detail
    const message =
      typeof detail === 'string'
        ? detail
        : `Document upload failed (HTTP ${response.status}).`

    throw new Error(message)
  }

  return data
}


// GET /api/documents
// Fetch all indexed documents.
export async function getDocuments() {
  return request('/api/documents')
}


// GET /api/documents/{document_id}
export async function getDocument(documentId) {
  return request(
    `/api/documents/${encodeURIComponent(documentId)}`,
  )
}


// DELETE /api/documents/{document_id}
export async function deleteDocument(documentId) {
  let response

  try {
    response = await fetch(
      `${API_BASE_URL}/api/documents/${encodeURIComponent(documentId)}`,
      {
        method: 'DELETE',
      },
    )
  } catch (err) {
    throw new Error(
      'Could not connect to the SchemeWise backend.',
      { cause: err },
    )
  }

  const data = await response.json().catch(() => ({}))

  if (!response.ok) {
    throw new Error(
      typeof data.detail === 'string'
        ? data.detail
        : `Document deletion failed (HTTP ${response.status}).`,
    )
  }

  return data
}


// POST /api/chat/ask
// Ask a question using indexed government documents.
export async function askQuestion({
  question,
  scheme_id,
  document_id,
}) {
  let response

  try {
    response = await fetch(
      `${API_BASE_URL}/api/chat/ask`,
      {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          question,
          ...(scheme_id ? { scheme_id } : {}),
          ...(document_id ? { document_id } : {}),
        }),
      },
    )
  } catch (err) {
    throw new Error(
      'Could not connect to the SchemeWise backend.',
      { cause: err },
    )
  }

  const data = await response.json().catch(() => ({}))

  if (!response.ok) {
    const detail = data.detail

    throw new Error(
      typeof detail === 'string'
        ? detail
        : `Question request failed (HTTP ${response.status}).`,
    )
  }

  return data
}

