
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
