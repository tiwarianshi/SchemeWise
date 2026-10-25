import { useState } from 'react'
import { checkEligibility } from '../services/api'

const initialForm = {
  age: '',
  state: '',
  annual_family_income: '',
  education_level: '',
  social_category: '',
  disability_status: '',
  occupation: '',
}

const fieldLabels = {
  age: 'Age',
  state: 'State',
  annual_family_income: 'Annual family income',
  education_level: 'Education level',
  social_category: 'Social category',
  disability_status: 'Disability status',
  occupation: 'Occupation',
}

function formatStatus(status) {
  if (status === 'eligible') return 'Potentially eligible'
  if (status === 'not_eligible') return 'Does not meet verified conditions'
  return 'Insufficient information'
}

export default function EligibilityChecker() {
  const [form, setForm] = useState(initialForm)
  const [results, setResults] = useState([])
  const [summary, setSummary] = useState(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')

  function handleChange(event) {
    const { name, value } = event.target

    setForm((current) => ({
      ...current,
      [name]: value,
    }))
  }

  async function handleSubmit(event) {
    event.preventDefault()

    setLoading(true)
    setError('')
    setResults([])
    setSummary(null)

    const profile = {}

    for (const [key, value] of Object.entries(form)) {
      if (value === '') {
        profile[key] = null
      } else if (key === 'age') {
        profile[key] = Number(value)
      } else if (key === 'annual_family_income') {
        profile[key] = Number(value)
      } else if (key === 'disability_status') {
        profile[key] = value === 'yes'
      } else {
        profile[key] = value
      }
    }

    try {
      const data = await checkEligibility(profile)

      setResults(data.results ?? [])
      setSummary(data.summary ?? null)
    } catch (err) {
      setError(
        err.message || 'Unable to check eligibility. Please try again.',
      )
    } finally {
      setLoading(false)
    }
  }

  function handleReset() {
    setForm(initialForm)
    setResults([])
    setSummary(null)
    setError('')
  }

  return (
    <section id="eligibility" className="eligibility-section">
      <div className="eligibility-heading">
        <span className="eligibility-eyebrow">
          PERSONALIZED SCHEME DISCOVERY
        </span>

        <h2>
          Find schemes that match <span>your profile.</span>
        </h2>

        <p>
          Enter your details to compare your profile with the eligibility
          conditions currently recorded in SchemeWise.
        </p>
      </div>

      <form className="eligibility-form" onSubmit={handleSubmit}>
        <div className="eligibility-form-grid">
          <label>
            Age
            <input
              type="number"
              name="age"
              min="0"
              max="120"
              value={form.age}
              onChange={handleChange}
              placeholder="Enter your age"
            />
          </label>

          <label>
            State
            <select
              name="state"
              value={form.state}
              onChange={handleChange}
            >
              <option value="">Select state</option>
              <option value="Uttar Pradesh">Uttar Pradesh</option>
              <option value="Bihar">Bihar</option>
              <option value="Madhya Pradesh">Madhya Pradesh</option>
              <option value="Rajasthan">Rajasthan</option>
              <option value="Maharashtra">Maharashtra</option>
              <option value="Delhi">Delhi</option>
              <option value="Other">Other</option>
            </select>
          </label>

          <label>
            Annual family income (₹)
            <input
              type="number"
              name="annual_family_income"
              min="0"
              step="1"
              value={form.annual_family_income}
              onChange={handleChange}
              placeholder="e.g. 150000"
            />
          </label>

          <label>
            Education level
            <select
              name="education_level"
              value={form.education_level}
              onChange={handleChange}
            >
              <option value="">Select education level</option>
              <option value="School">School</option>
              <option value="Diploma">Diploma</option>
              <option value="Undergraduate">Undergraduate</option>
              <option value="Postgraduate">Postgraduate</option>
              <option value="Doctoral">Doctoral</option>
              <option value="Other">Other</option>
            </select>
          </label>

          <label>
            Social category
            <select
              name="social_category"
              value={form.social_category}
              onChange={handleChange}
            >
              <option value="">Select category</option>
              <option value="General">General</option>
              <option value="OBC">OBC</option>
              <option value="SC">SC</option>
              <option value="ST">ST</option>
              <option value="EWS">EWS</option>
              <option value="Other">Other</option>
            </select>
          </label>

          <label>
            Disability status
            <select
              name="disability_status"
              value={form.disability_status}
              onChange={handleChange}
            >
              <option value="">Prefer not to specify</option>
              <option value="yes">Yes</option>
              <option value="no">No</option>
            </select>
          </label>

          <label>
            Occupation
            <select
              name="occupation"
              value={form.occupation}
              onChange={handleChange}
            >
              <option value="">Select occupation</option>
              <option value="Student">Student</option>
              <option value="Farmer">Farmer</option>
              <option value="Self-employed">Self-employed</option>
              <option value="Employed">Employed</option>
              <option value="Unemployed">Unemployed</option>
              <option value="Other">Other</option>
            </select>
          </label>
        </div>

        <div className="eligibility-actions">
          <button type="submit" disabled={loading}>
            {loading ? 'Checking schemes...' : 'Check Eligibility'}
          </button>

          <button
            type="button"
            className="eligibility-reset"
            onClick={handleReset}
            disabled={loading}
          >
            Reset
          </button>
        </div>

        <p className="eligibility-privacy-note">
          Enter only the information needed for this check. Your profile is
          sent to the SchemeWise backend for evaluation.
        </p>
      </form>

      {error && (
        <div className="eligibility-error" role="alert">
          <p>{error}</p>
          <button type="button" onClick={handleSubmit}>
            Retry
          </button>
        </div>
      )}

      {summary && (
        <section className="eligibility-results" aria-live="polite">
          <div className="eligibility-results-heading">
            <div>
              <span className="eligibility-eyebrow">YOUR RESULTS</span>
              <h3>Eligibility assessment</h3>
            </div>

            <p>{results.length} schemes checked</p>
          </div>

          <div className="eligibility-summary">
            <div>
              <strong>{summary.eligible}</strong>
              <span>Potential matches</span>
            </div>

            <div>
              <strong>{summary.not_eligible}</strong>
              <span>Conditions not met</span>
            </div>

            <div>
              <strong>{summary.insufficient_information}</strong>
              <span>Need more information</span>
            </div>
          </div>

          <div className="eligibility-result-list">
            {results.map((result) => (
              <article
                className="eligibility-result-card"
                key={result.scheme_id}
              >
                <div className="eligibility-result-top">
                  <h4>{result.scheme_name}</h4>

                  <span
                    className={`eligibility-status status-${result.status}`}
                  >
                    {formatStatus(result.status)}
                  </span>
                </div>

                {result.reasons.length > 0 && (
                  <div>
                    <strong>Assessment details</strong>
                    <ul>
                      {result.reasons.map((reason, index) => (
                        <li key={`${result.scheme_id}-reason-${index}`}>
                          {reason}
                        </li>
                      ))}
                    </ul>
                  </div>
                )}

                {result.missing_information.length > 0 && (
                  <div>
                    <strong>Information needed</strong>
                    <ul>
                      {result.missing_information.map((item, index) => (
                        <li key={`${result.scheme_id}-missing-${index}`}>
                          {item}
                        </li>
                      ))}
                    </ul>
                  </div>
                )}

                {result.official_url && (
                  <a
                    href={result.official_url}
                    target="_blank"
                    rel="noreferrer"
                  >
                    Review official scheme information ↗
                  </a>
                )}
              </article>
            ))}
          </div>

          <p className="eligibility-disclaimer">
            These results are preliminary matches against the information
            available in SchemeWise. They are not official eligibility
            decisions or guarantees of benefits. Review the official scheme
            guidelines before applying.
          </p>
        </section>
      )}
    </section>
  )
}