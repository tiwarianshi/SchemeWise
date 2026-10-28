import { useState } from 'react'
import { checkEligibility } from '../services/api'

// Reusable dropdown options

const STATE_OPTIONS = [
  'Andhra Pradesh',
  'Arunachal Pradesh',
  'Assam',
  'Bihar',
  'Chhattisgarh',
  'Goa',
  'Gujarat',
  'Haryana',
  'Himachal Pradesh',
  'Jharkhand',
  'Karnataka',
  'Kerala',
  'Madhya Pradesh',
  'Maharashtra',
  'Manipur',
  'Meghalaya',
  'Mizoram',
  'Nagaland',
  'Odisha',
  'Punjab',
  'Rajasthan',
  'Sikkim',
  'Tamil Nadu',
  'Telangana',
  'Tripura',
  'Uttar Pradesh',
  'Uttarakhand',
  'West Bengal',
  'Andaman and Nicobar Islands',
  'Chandigarh',
  'Dadra and Nagar Haveli and Daman and Diu',
  'Delhi',
  'Jammu and Kashmir',
  'Ladakh',
  'Lakshadweep',
  'Puducherry',
]

const EDUCATION_OPTIONS = [
  'School',
  'Diploma',
  'Undergraduate',
  'Postgraduate',
  'Doctoral',
  'Other',
]

const CATEGORY_OPTIONS = [
  'General',
  'OBC',
  'SC',
  'ST',
  'EWS',
  'Other',
]

const OCCUPATION_OPTIONS = [
  'Student',
  'Farmer',
  'Self-employed',
  'Employed',
  'Unemployed',
  'Other',
]

// PM-KISAN questions.
// "name" must exactly match the field name in server/eligibility.py.
// Wording follows server/data/eligibility_verification.md.
// "Not sure" is sent to the backend as null, never as false.

const PMKISAN_QUESTIONS = [
  {
    name: 'has_eligible_landholding',
    label: 'Does your family own cultivable land recorded in the State/UT land records?',
    help: 'Ownership must have been held on or before 1 February 2019, or acquired by inheritance after the owner’s death.',
  },
  {
    name: 'is_institutional_landholder',
    label: 'Is the land held by an institution rather than by a family?',
  },
  {
    name: 'has_constitutional_post_exclusion_in_family',
    label: 'Is any family member a former or present holder of a constitutional post?',
  },
  {
    name: 'has_elected_official_exclusion_in_family',
    label: 'Is any family member a former or present minister, MP, MLA, MLC, mayor of a municipal corporation or chairperson of a district panchayat?',
  },
  {
    name: 'has_excluded_government_employee_in_family',
    label: 'Is any family member a serving or retired officer or employee of the Central or State government, a government public sector enterprise or autonomous body, or a regular local-body employee?',
    help: 'Do not count Multi Tasking Staff, Class IV or Group D employees.',
  },
  {
    name: 'has_excluded_pensioner_in_family',
    label: 'Does any family member draw a pension of ₹10,000 or more per month?',
    help: 'Do not count retired Multi Tasking Staff, Class IV or Group D employees.',
  },
  {
    name: 'paid_income_tax_last_assessment_year_in_family',
    label: 'Did any family member pay income tax in the last assessment year?',
  },
  {
    name: 'has_practicing_registered_professional_in_family',
    label: 'Is any family member a doctor, engineer, lawyer, chartered accountant or architect who is registered with a professional body and practising?',
  },
  {
    name: 'is_nri_family',
    label: 'Is your family Non-Resident Indian under the Income Tax Act?',
    help: 'This applies to new applicants only.',
  },
]

// Fields answered with Yes / No / Not sure.
const BOOLEAN_FIELDS = new Set([
  'disability_status',
  ...PMKISAN_QUESTIONS.map((question) => question.name),
])

// Initial form values.
// Empty strings mean the user has not supplied that information.

const initialForm = {
  age: '',
  state: '',
  annual_family_income: '',
  education_level: '',
  social_category: '',
  disability_status: '',
  occupation: '',
  ...Object.fromEntries(
    PMKISAN_QUESTIONS.map((question) => [question.name, '']),
  ),
}

// Format the status badge.

function formatStatus(status) {
  if (status === 'eligible') return 'Potentially eligible'

  if (status === 'not_eligible') {
    return 'Does not meet verified conditions'
  }

  return 'Insufficient information'
}

// Explain what each result means.

function getStatusExplanation(status) {
  switch (status) {
    case 'eligible':
      return 'The recorded, verified eligibility rules match your profile. Confirm the current official guidelines before applying.'

    case 'not_eligible':
      return 'Your profile does not satisfy the complete, verified rules currently recorded for this scheme.'

    default:
      return 'Some required information or verified eligibility rules are missing. This result does not mean you are ineligible.'
  }
}

export default function EligibilityChecker() {
  const [form, setForm] = useState(initialForm)
  const [results, setResults] = useState([])
  const [summary, setSummary] = useState(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')

  // Update the corresponding form field whenever the user changes it.

  function handleChange(event) {
    const { name, value } = event.target

    setForm((current) => ({
      ...current,
      [name]: value,
    }))
  }

  // Convert form values to the data types expected by the backend.

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
      } else if (
        key === 'age' ||
        key === 'annual_family_income'
      ) {
        profile[key] = Number(value)
      } else if (BOOLEAN_FIELDS.has(key)) {
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
        err.message ||
          'Unable to check eligibility. Please try again.',
      )
    } finally {
      setLoading(false)
    }
  }

  // Reset the form and clear previously displayed results.

  function handleReset() {
    setForm(initialForm)
    setResults([])
    setSummary(null)
    setError('')
  }

  return (
    <section id="eligibility" className="eligibility-section">
      {/* Heading */}

      <div className="eligibility-heading">
        <span className="eligibility-eyebrow">
          PERSONALIZED SCHEME DISCOVERY
        </span>

        <h2>
          Find schemes that match <span>your profile.</span>
        </h2>

        <p>
          Enter your details to compare your profile with the
          eligibility conditions currently recorded in SchemeWise.
        </p>
      </div>

      {/* Eligibility form */}

      <form
        className="eligibility-form"
        onSubmit={handleSubmit}
      >
        <div className="eligibility-form-grid">
          {/* Age */}

          <label>
            Age

            <input
              type="number"
              name="age"
              min="0"
              max="120"
              step="1"
              value={form.age}
              onChange={handleChange}
              placeholder="Enter your age"
              aria-describedby="age-help"
            />

            <small id="age-help">
              Enter a whole number between 0 and 120, or leave
              blank if unknown.
            </small>
          </label>

          {/* State */}

          <label>
            State

            <select
              name="state"
              value={form.state}
              onChange={handleChange}
            >
              <option value="">
                Select state or union territory
              </option>

              {STATE_OPTIONS.map((state) => (
                <option key={state} value={state}>
                  {state}
                </option>
              ))}
            </select>
          </label>

          {/* Annual family income */}

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
              aria-describedby="income-help"
            />

            <small id="income-help">
              Enter the annual amount in Indian rupees. Leave
              blank if unknown.
            </small>
          </label>

          {/* Education */}

          <label>
            Education level

            <select
              name="education_level"
              value={form.education_level}
              onChange={handleChange}
            >
              <option value="">
                Select education level
              </option>

              {EDUCATION_OPTIONS.map((education) => (
                <option key={education} value={education}>
                  {education}
                </option>
              ))}
            </select>
          </label>

          {/* Social category */}

          <label>
            Social category

            <select
              name="social_category"
              value={form.social_category}
              onChange={handleChange}
            >
              <option value="">Select category</option>

              {CATEGORY_OPTIONS.map((category) => (
                <option key={category} value={category}>
                  {category}
                </option>
              ))}
            </select>
          </label>

          {/* Disability status */}

          <label>
            Disability status

            <select
              name="disability_status"
              value={form.disability_status}
              onChange={handleChange}
            >
              <option value="">
                Prefer not to specify
              </option>

              <option value="yes">Yes</option>
              <option value="no">No</option>
            </select>
          </label>

          {/* Occupation */}

          <label>
            Occupation

            <select
              name="occupation"
              value={form.occupation}
              onChange={handleChange}
            >
              <option value="">Select occupation</option>

              {OCCUPATION_OPTIONS.map((occupation) => (
                <option key={occupation} value={occupation}>
                  {occupation}
                </option>
              ))}
            </select>
          </label>
        </div>

        {/* PM-KISAN questions */}

        <fieldset className="eligibility-fieldset">
          <legend>PM-KISAN questions (farmer families)</legend>

          <p className="eligibility-fieldset-note">
            In these questions, “family” means husband, wife and
            minor children. Choose “Not sure” if you do not know —
            it is not treated as “No”.
          </p>

          <div className="eligibility-form-grid">
            {PMKISAN_QUESTIONS.map((question) => (
              <label key={question.name}>
                {question.label}

                <select
                  name={question.name}
                  value={form[question.name]}
                  onChange={handleChange}
                  aria-describedby={
                    question.help
                      ? `${question.name}-help`
                      : undefined
                  }
                >
                  <option value="">Not sure</option>
                  <option value="yes">Yes</option>
                  <option value="no">No</option>
                </select>

                {question.help && (
                  <small id={`${question.name}-help`}>
                    {question.help}
                  </small>
                )}
              </label>
            ))}
          </div>
        </fieldset>

        {/* Form actions */}

        <div className="eligibility-actions">
          <button type="submit" disabled={loading}>
            {loading
              ? 'Checking schemes...'
              : 'Check Eligibility'}
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
          Enter only the information needed for this check. Your
          profile is sent to the SchemeWise backend for evaluation.
        </p>
      </form>

      {/* API error */}

      {error && (
        <div className="eligibility-error" role="alert">
          <p>{error}</p>

          <button
            type="button"
            onClick={handleSubmit}
            disabled={loading}
          >
            Retry
          </button>
        </div>
      )}

      {/* Eligibility results */}

      {summary && (
        <section
          className="eligibility-results"
          aria-live="polite"
        >
          <div className="eligibility-results-heading">
            <div>
              <span className="eligibility-eyebrow">
                YOUR RESULTS
              </span>

              <h3>Eligibility assessment</h3>
            </div>

            <p>{results.length} schemes checked</p>
          </div>

          {/* Summary counts */}

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
              <strong>
                {summary.insufficient_information}
              </strong>

              <span>Need more information</span>
            </div>
          </div>

          {/* Individual scheme cards */}

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

                <p className="eligibility-status-explanation">
                  {getStatusExplanation(result.status)}
                </p>

                {result.reasons.length > 0 && (
                  <div>
                    <strong>Assessment details</strong>

                    <ul>
                      {result.reasons.map((reason, index) => (
                        <li
                          key={`${result.scheme_id}-reason-${index}`}
                        >
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
                      {result.missing_information.map(
                        (item, index) => (
                          <li
                            key={`${result.scheme_id}-missing-${index}`}
                          >
                            {item}
                          </li>
                        ),
                      )}
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

          {/* Disclaimer */}

          <p className="eligibility-disclaimer">
            These results are preliminary matches against the
            information available in SchemeWise. They are not
            official eligibility decisions or guarantees of
            benefits. Review the official scheme guidelines before
            applying.
          </p>
        </section>
      )}
    </section>
  )
}