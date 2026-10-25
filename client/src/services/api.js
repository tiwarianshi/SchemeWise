
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
