import { ArrowRight, FileText, ListChecks, Sparkles } from './Icons'
import { ELIGIBILITY_HREF, SCHEMES_HREF } from '../config'

function PreviewPanel() {
  return (
    <div className="preview" role="img" aria-label="Illustration of the SchemeWise workspace showing a scheme, its eligibility requirements, and a document checklist">
      <div className="preview__tag">Illustrative preview</div>
      <div className="preview__card">
        <div className="preview__head">
          <span className="chip chip--blue">Scheme overview</span>
          <span className="preview__dots" aria-hidden="true"><i /><i /><i /></span>
        </div>
        <div className="skel-line w70" /><div className="skel-line w95" /><div className="skel-line w55" />
      </div>
      <div className="preview__card preview__card--offset">
        <div className="preview__row"><ListChecks /><strong>Eligibility requirements</strong></div>
        <ul className="preview__list">
          <li><span className="tick tick--ok" />Requirement met</li>
          <li><span className="tick tick--ok" />Requirement met</li>
          <li><span className="tick tick--missing" />Information still needed</li>
        </ul>
      </div>
      <div className="preview__card">
        <div className="preview__row"><FileText /><strong>Document checklist</strong></div>
        <ul className="preview__list">
          <li><span className="box" />Document one</li>
          <li><span className="box" />Document two</li>
        </ul>
      </div>
      <div className="preview__ai"><Sparkles /><span>Ask about scheme rules…</span></div>
    </div>
  )
}

export default function Hero() {
  return (
    <section id="home" className="hero" aria-labelledby="hero-title">
      <div className="hero__glow" aria-hidden="true" />
      <div className="container hero__grid">
        <div className="hero__copy">
          <p className="eyebrow hero-anim" style={{ '--d': '0ms' }}>AI-POWERED SCHEME DISCOVERY</p>
          <h1 id="hero-title" className="hero-anim" style={{ '--d': '80ms' }}>
            Find the support<br />you’re <span className="grad">eligible for.</span>
          </h1>
          <p className="lead hero-anim" style={{ '--d': '160ms' }}>
            Discover government schemes, understand eligibility requirements, and prepare the right documents—all in one intelligent workspace.
          </p>
          <div className="hero__actions hero-anim" style={{ '--d': '240ms' }}>
            <a className="btn btn--primary btn--lg" href={SCHEMES_HREF}>Explore Schemes <ArrowRight /></a>
            <a className="btn btn--outline btn--lg" href={ELIGIBILITY_HREF}>Check My Eligibility</a>
          </div>
          <p className="trust-line hero-anim" style={{ '--d': '320ms' }}>Clear requirements. Source-backed information. Smarter discovery.</p>
        </div>
        <div className="hero__visual hero-anim" style={{ '--d': '200ms' }}><PreviewPanel /></div>
      </div>
    </section>
  )
}
