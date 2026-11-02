
import { useCallback, useEffect, useState } from 'react'
import { fetchSchemes } from '../services/api'

export function useSchemes(filters = {}) {
  const {
    search = '',
    state: stateFilter = '',
    category: categoryFilter = '',
    beneficiary_group: groupFilter = '',
  } = filters

  const [state, setState] = useState({
    status: 'loading',
    schemes: [],
    error: '',
  })

  const [attempt, setAttempt] = useState(0)

  useEffect(() => {
    const controller = new AbortController()

    const params = {
      search,
      state: stateFilter,
      category: categoryFilter,
      beneficiary_group: groupFilter,
    }

    fetchSchemes({
      ...params,
      signal: controller.signal,
    })
      .then((schemes) => {
        setState({
          status: schemes.length ? 'success' : 'empty',
          schemes,
          error: '',
        })
      })
      .catch((err) => {
        if (err.name === 'AbortError') return

        setState({
          status: 'error',
          schemes: [],
          error: err.message || 'Something went wrong.',
        })
      })

    return () => controller.abort()
  }, [search, stateFilter, categoryFilter, groupFilter, attempt])

  const retry = useCallback(() => {
    setState((s) => ({ ...s, status: 'loading', error: '' }))
    setAttempt((n) => n + 1)
  }, [])

  return { ...state, retry }
}
