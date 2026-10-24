import { Alert, Inbox } from './Icons'
import SchemeCard from './SchemeCard'
import { useSchemes } from '../hooks/useSchemes'

function Skeletons() {
  return [0, 1].map((i) => (
    <div className="card scheme skeleton" key={i} aria-hidden="true">
      <div className="skel-pill" /><div className="skel-line w70 h20" />
      <div className="skel-line w95" /><div className="skel-line w85" /><div className="skel-line w40" />
    </div>
  ))
}

export default function SchemesSection() {
  const { status, schemes, error, retry } = useSchemes()

  return (
    <section id="schemes" className="section section--alt" aria-labelledby="schemes-title">
      <div className="container">
        <h2 id="schemes-title" className="section__title">Explore Government Schemes</h2>
        <p className="section__sub">Schemes loaded live from the SchemeWise API. Always confirm details on the official scheme source.</p>

        <div aria-live="polite" aria-busy={status === 'loading'}>
          {status === 'loading' && <div className="cards cards--2"><span className="sr-only">Loading schemes…</span><Skeletons /></div>}

          {status === 'success' && (
            <div className="cards cards--2">
              {schemes.map((s, i) => <SchemeCard key={s.id ?? i} scheme={s} />)}
            </div>
          )}

          {status === 'error' && (
            <div className="state state--error" role="alert">
              <Alert width={28} height={28} />
              <h3>We couldn’t load schemes</h3>
              <p>{error} Check that the backend is running, then try again.</p>
              <button type="button" className="btn btn--primary" onClick={retry}>Retry</button>
            </div>
          )}

          {status === 'empty' && (
            <div className="state">
              <Inbox width={28} height={28} />
              <h3>No schemes available yet</h3>
              <p>The API responded, but it returned no schemes. Check back soon.</p>
              <button type="button" className="btn btn--outline" onClick={retry}>Refresh</button>
            </div>
          )}
        </div>
      </div>
    </section>
  )
}
