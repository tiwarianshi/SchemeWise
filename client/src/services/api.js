// Single place for all backend access. Base URL comes from Vite env config.
const API_BASE_URL = (import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000').replace(/\/$/, '')

async function request(path, { signal } = {}) {
  let response
  try {
    response = await fetch(`${API_BASE_URL}${path}`, { signal })
  } catch (err) {
    if (err.name === 'AbortError') throw err
    throw new Error(`Could not reach the SchemeWise API at ${API_BASE_URL}.`, { cause: err })
  }
  if (!response.ok) {
    throw new Error(`The API responded with an error (HTTP ${response.status}).`)
  }
  return response.json()
}

// GET /api/schemes -> { count, schemes: [...] }
export async function fetchSchemes(options) {
  const data = await request('/api/schemes', options)
  return Array.isArray(data?.schemes) ? data.schemes : []
}
