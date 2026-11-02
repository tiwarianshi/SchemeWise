import { External, MapPin } from './Icons'

// Renders only the fields the API actually returned.
export default function SchemeCard({ scheme }) {
  const { name, category, state, description, eligibility_summary: eligibility, official_url: url } = scheme
  return (
    <article className="card scheme">
      {category && <span className="chip chip--rose">{category}</span>}
      <h3>{name || 'Untitled scheme'}</h3>
      {description && <p>{description}</p>}
      {eligibility && <p className="scheme__elig"><strong>Eligibility:</strong> {eligibility}</p>}
      <div className="scheme__foot">
        {state && <span className="scheme__meta"><MapPin width={16} height={16} />{state}</span>}
        {url && (
          <a className="link" href={url} target="_blank" rel="noreferrer noopener">
            Visit official website <External width={16} height={16} />
            <span className="sr-only"> (opens in a new tab)</span>
          </a>
        )}
      </div>
    </article>
  )
}
