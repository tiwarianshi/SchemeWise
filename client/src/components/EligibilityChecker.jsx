import { useState } from 'react'
import { checkEligibility } from '../services/api'

// ---------------------------------------------------------------------
// Dropdown options (keep in sync with the lists in server/eligibility.py)
// ---------------------------------------------------------------------

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

const SCHOOL_TYPE_OPTIONS = [
  'Government school',
  'Government-aided school',
  'Local body school',
  'Kendriya Vidyalaya or Jawahar Navodaya Vidyalaya',
  'Residential school run by Centre/State (with boarding and lodging)',
  'Private school',
  'Other',
]

// ---------------------------------------------------------------------
// Scheme-specific Yes / No questions.
// "name" must exactly match the field name in server/eligibility.py.
// Wording follows server/data/eligibility_verification.md.
// "Not sure" is sent to the backend as null, never as false.
// ---------------------------------------------------------------------

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

const NMMSS_QUESTIONS = [
  {
    name: 'selected_in_nmmss_state_test',
    label: 'Were you selected for the NMMSS scholarship through your State/UT Class VIII selection test?',
  },
  {
    name: 'promoted_from_class_8_to_9',
    label: 'Were you promoted from Class VIII to Class IX without being held back?',
  },
]

const DISABILITY_SCHOLARSHIP_QUESTIONS = [
  {
    name: 'is_indian_national',
    label: 'Are you an Indian national?',
  },
  {
    name: 'has_valid_disability_certificate',
    label: 'Do you have a valid disability certificate issued by the competent authority?',
  },
  {
    name: 'studying_in_notified_institute',
    label: 'Is your institute on the list of Institutes of Excellence notified by DEPwD for the Top Class Education scholarship?',
    help: 'Check the list on the National Scholarship Portal or the DEPwD website.',
  },
  {
    name: 'is_regular_full_time_course',
    label: 'Is your course regular and full-time (not distance, part-time or week-end)?',
  },
  {
    name: 'has_received_top_class_award_before',
    label: 'Have you already received the Top Class Education scholarship before?',
  },
  {
    name: 'exceeds_disabled_children_limit_per_parents',
    label: 'Do two or more of your brothers or sisters with disabilities (same parents) already receive benefits under the Scholarships for Students with Disabilities scheme?',
    help: 'If you are a twin of the second such child, answer No.',
  },
  {
    name: 'is_repeating_class',
    label: 'Are you repeating a class or year that you have already studied?',
  },
]

// ---------------------------------------------------------------------
// Which fields belong to which scheme
// ---------------------------------------------------------------------

// Always shown, and always sent, whichever scheme is selected.
const COMMON_FIELDS = [
  'age',
  'state',
  'annual_family_income',
  'education_level',
  'social_category',
  'disability_status',
  'occupation',
]

const names = (questions) => questions.map((question) => question.name)

// To add a scheme: add an entry here, a questions panel below, and one line in the form.
const SCHEMES = [
  {
    key: 'pmkisan',
    label: 'PM-KISAN',
    schemeId: 'scheme-009',
    hint: 'Income support for landholding farmer families.',
    fields: names(PMKISAN_QUESTIONS),
  },
  {
    key: 'nmmss',
    label: 'NMMSS Scholarship',
    schemeId: 'scheme-008',
    hint: 'For students selected through the State Class VIII test and starting Class IX.',
    fields: [
      'school_type',
      'class_7_marks_percentage',
      'class_8_marks_percentage',
      ...names(NMMSS_QUESTIONS),
    ],
  },
  {
    key: 'top-class',
    label: 'Top Class Education Scholarship',
    schemeId: 'scheme-007',
    hint: 'For students with disabilities in graduate, post-graduate or diploma courses at notified institutes.',
    fields: ['disability_percentage', ...names(DISABILITY_SCHOLARSHIP_QUESTIONS)],
  },
]

// Fields answered with Yes / No / Not sure.
const BOOLEAN_FIELDS = new Set([
  'disability_status',
  ...names(PMKISAN_QUESTIONS),
  ...names(NMMSS_QUESTIONS),
  ...names(DISABILITY_SCHOLARSHIP_QUESTIONS),
])

// Fields sent as numbers.
const NUMBER_FIELDS = new Set([
  'age',
  'annual_family_income',
  'class_7_marks_percentage',
  'class_8_marks_percentage',
  'disability_percentage',
])

// Empty strings mean the user has not supplied that information.
const initialForm = Object.fromEntries(
  [...COMMON_FIELDS, ...SCHEMES.flatMap((scheme) => scheme.fields)].map(
    (field) => [field, ''],
  ),
)

// ---------------------------------------------------------------------
// Result text
// ---------------------------------------------------------------------

function formatStatus(status) {
  if (status === 'eligible') return 'Potentially eligible'

  if (status === 'not_eligible') {
    return 'Does not meet verified conditions'
  }

  return 'Insufficient information'
}

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

// ---------------------------------------------------------------------
// Small building blocks
// ---------------------------------------------------------------------

function YesNoQuestion({ question, value, onChange }) {
  const helpId = question.help ? `${question.name}-help` : undefined

  return (
    <label>
      {question.label}

      <select
        name={question.name}
        value={value}
        onChange={onChange}
        aria-describedby={helpId}
      >
        <option value="">Not sure</option>
        <option value="yes">Yes</option>
        <option value="no">No</option>
      </select>

      {question.help && <small id={helpId}>{question.help}</small>}
    </label>
  )
}

function PmKisanQuestions({ form, onChange }) {
  return (
    <fieldset className="eligibility-fieldset">
      <legend>PM-KISAN questions (farmer families)</legend>

      <p className="eligibility-fieldset-note">
        In these questions, “family” means husband, wife and minor
        children. Choose “Not sure” if you do not know — it is not
        treated as “No”.
      </p>

      <div className="eligibility-form-grid">
        {PMKISAN_QUESTIONS.map((question) => (
          <YesNoQuestion
            key={question.name}
            question={question}
            value={form[question.name]}
            onChange={onChange}
          />
        ))}
      </div>
    </fieldset>
  )
}

function NmmssQuestions({ form, onChange }) {
  return (
    <fieldset className="eligibility-fieldset">
      <legend>NMMSS scholarship questions (school students)</legend>

      <p className="eligibility-fieldset-note">
        Your annual family income and social category above are also
        used for this scheme. Choose “Not sure” if you do not know —
        it is not treated as “No”.
      </p>

      <div className="eligibility-form-grid">
        <label>
          What type of school are you studying in?

          <select
            name="school_type"
            value={form.school_type}
            onChange={onChange}
          >
            <option value="">Select school type</option>

            {SCHOOL_TYPE_OPTIONS.map((type) => (
              <option key={type} value={type}>
                {type}
              </option>
            ))}
          </select>
        </label>

        <label>
          Percentage scored in the Class VII examination

          <input
            type="number"
            name="class_7_marks_percentage"
            min="0"
            max="100"
            step="0.01"
            value={form.class_7_marks_percentage}
            onChange={onChange}
            placeholder="e.g. 58"
            aria-describedby="class7-help"
          />

          <small id="class7-help">
            Needed to confirm you could sit the selection test (55%,
            or 50% for SC/ST students). Leave blank if unknown.
          </small>
        </label>

        <label>
          Percentage scored in the Class VIII examination

          <input
            type="number"
            name="class_8_marks_percentage"
            min="0"
            max="100"
            step="0.01"
            value={form.class_8_marks_percentage}
            onChange={onChange}
            placeholder="e.g. 62.5"
            aria-describedby="class8-help"
          />

          <small id="class8-help">
            Enter a number between 0 and 100, or leave blank if
            unknown.
          </small>
        </label>

        {NMMSS_QUESTIONS.map((question) => (
          <YesNoQuestion
            key={question.name}
            question={question}
            value={form[question.name]}
            onChange={onChange}
          />
        ))}
      </div>
    </fieldset>
  )
}

function TopClassQuestions({ form, onChange }) {
  return (
    <fieldset className="eligibility-fieldset">
      <legend>Top Class Education scholarship questions</legend>

      <p className="eligibility-fieldset-note">
        Your education level and annual family income above are also
        used for this scheme. Choose “Not sure” if you do not know —
        it is not treated as “No”.
      </p>

      <div className="eligibility-form-grid">
        <label>
          Disability percentage on your certificate or UDID card

          <input
            type="number"
            name="disability_percentage"
            min="0"
            max="100"
            step="0.01"
            value={form.disability_percentage}
            onChange={onChange}
            placeholder="e.g. 45"
            aria-describedby="disability-pct-help"
          />

          <small id="disability-pct-help">
            Enter a number between 0 and 100, or leave blank if
            unknown.
          </small>
        </label>

        {DISABILITY_SCHOLARSHIP_QUESTIONS.map((question) => (
          <YesNoQuestion
            key={question.name}
            question={question}
            value={form[question.name]}
            onChange={onChange}
          />
        ))}
      </div>
    </fieldset>
  )
}

// ---------------------------------------------------------------------
// The page section
// ---------------------------------------------------------------------

export default function EligibilityChecker() {
  const [schemeKey, setSchemeKey] = useState('')
  const [form, setForm] = useState(initialForm)
  const [results, setResults] = useState([])
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')

  const selected = SCHEMES.find((scheme) => scheme.key === schemeKey)

  // Update the corresponding form field whenever the user changes it.

  function handleChange(event) {
    const { name, value } = event.target

    setForm((current) => ({
      ...current,
      [name]: value,
    }))
  }

  // Choosing another scheme clears the previous result and error.
  // Answers stay in the form but are only sent for the selected scheme.

  function handleSchemeChange(event) {
    setSchemeKey(event.target.value)
    setResults([])
    setError('')
  }

  // Convert form values to the data types expected by the backend.
  // Only the common fields and the selected scheme's fields are sent.

  async function handleSubmit(event) {
    event.preventDefault()

    if (!selected) return

    setLoading(true)
    setError('')
    setResults([])

    const sendFields = new Set([...COMMON_FIELDS, ...selected.fields])
    const profile = {}

    for (const [key, value] of Object.entries(form)) {
      if (!sendFields.has(key)) continue

      if (value === '') {
        profile[key] = null
      } else if (NUMBER_FIELDS.has(key)) {
        profile[key] = Number(value)
      } else if (BOOLEAN_FIELDS.has(key)) {
        profile[key] = value === 'yes'
      } else {
        profile[key] = value
      }
    }

    try {
      const data = await checkEligibility(profile)

      const chosen = (data.results ?? []).filter(
        (result) => result.scheme_id === selected.schemeId,
      )

      if (chosen.length === 0) {
        throw new Error(
          `The server returned no result for ${selected.label}. Please try again.`,
        )
      }

      setResults(chosen)
    } catch (err) {
      setError(
        err.message ||
          'Unable to check eligibility. Please try again.',
      )
    } finally {
      setLoading(false)
    }
  }

  // Clear all answers and any displayed result. The chosen scheme stays selected.

  function handleReset() {
    setForm(initialForm)
    setResults([])
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
          Check your eligibility <span>scheme by scheme.</span>
        </h2>

        <p>
          Choose a scheme and answer only the questions it needs. We
          compare your answers with the eligibility conditions
          currently recorded in SchemeWise.
        </p>
      </div>

      {/* Eligibility form */}

      <form
        className="eligibility-form"
        onSubmit={handleSubmit}
      >
        {/* Step 1: choose the scheme */}

        <div className="eligibility-scheme-picker">
          <label>
            Select scheme

            <select
              name="scheme"
              value={schemeKey}
              onChange={handleSchemeChange}
              aria-describedby="scheme-picker-help"
            >
              <option value="">Choose a scheme to check</option>

              {SCHEMES.map((scheme) => (
                <option key={scheme.key} value={scheme.key}>
                  {scheme.label}
                </option>
              ))}
            </select>

            <small id="scheme-picker-help">
              {selected
                ? selected.hint
                : 'We will then ask only the questions that scheme needs.'}
            </small>
          </label>
        </div>

        {/* Step 2: common details (always visible) */}

        <fieldset className="eligibility-fieldset">
          <legend>Your details (used for every scheme)</legend>

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
        </fieldset>

        {/* Step 3: only the selected scheme's questions */}

        {selected?.key === 'pmkisan' && (
          <PmKisanQuestions form={form} onChange={handleChange} />
        )}

        {selected?.key === 'nmmss' && (
          <NmmssQuestions form={form} onChange={handleChange} />
        )}

        {selected?.key === 'top-class' && (
          <TopClassQuestions form={form} onChange={handleChange} />
        )}

        {/* Form actions */}

        <div className="eligibility-actions">
          <button type="submit" disabled={loading || !selected}>
            {loading
              ? 'Checking...'
              : selected
                ? `Check ${selected.label}`
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

        {!selected && (
          <p className="eligibility-fieldset-note">
            Select a scheme above to enable the check.
          </p>
        )}

        <p className="eligibility-privacy-note">
          Enter only the information needed for this check. Your
          answers for the selected scheme are sent to the SchemeWise
          backend for evaluation.
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

      {/* Eligibility result */}

      {results.length > 0 && (
        <section
          className="eligibility-results"
          aria-live="polite"
        >
          <div className="eligibility-results-heading">
            <div>
              <span className="eligibility-eyebrow">
                YOUR RESULT
              </span>

              <h3>Eligibility assessment</h3>
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

                <p className="eligibility-status-explanation">
                  {getStatusExplanation(result.status)}
                </p>

                {(result.conditions_not_met ?? []).length > 0 && (
                  <div className="eligibility-conditions eligibility-conditions--not-met">
                    <strong>Why this does not match</strong>

                    <ul>
                      {result.conditions_not_met.map((text, index) => (
                        <li key={`${result.scheme_id}-no-${index}`}>
                          <span aria-hidden="true">✗ </span>
                          <span className="sr-only">Not met: </span>
                          {text}
                        </li>
                      ))}
                    </ul>
                  </div>
                )}

                {(result.conditions_met ?? []).length > 0 && (
                  <div className="eligibility-conditions eligibility-conditions--met">
                    <strong>Conditions you meet</strong>

                    <ul>
                      {result.conditions_met.map((text, index) => (
                        <li key={`${result.scheme_id}-yes-${index}`}>
                          <span aria-hidden="true">✓ </span>
                          <span className="sr-only">Met: </span>
                          {text}
                        </li>
                      ))}
                    </ul>
                  </div>
                )}

                {(result.missing_information ?? []).length > 0 && (
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