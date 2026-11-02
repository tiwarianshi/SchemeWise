import { ListChecks, Search, ShieldCheck, FileText, Sparkles } from './Icons'
import { useReveal } from '../hooks/useReveal'

const TRUST = [
  { icon: ShieldCheck, text: 'Official-source-oriented information' },
  { icon: ListChecks, text: 'Clear eligibility explanations' },
  { icon: FileText, text: 'Organized document checklists' },
]

const FEATURES = [
  { icon: Search, title: 'Smart Scheme Discovery', body: 'Browse schemes by category and region and see what each one is about.', live: true },
  { icon: ListChecks, title: 'Eligibility Insights', body: 'Understand a scheme’s requirements and which details are still missing.', live: false },
  { icon: FileText, title: 'Document Checklist', body: 'See which documents a scheme asks for before you apply.', live: false },
  { icon: Sparkles, title: 'AI-Powered Assistance', body: 'Ask questions about scheme rules and the source material behind them.', live: false },
]

export default function Features() {
  const ref = useReveal()
  return (
    <>
      <section className="trust" aria-label="What SchemeWise offers">
        <ul className="container trust__list">
          {TRUST.map(({ icon: Icon, text }) => (
            <li key={text}><Icon /><span>{text}</span></li>
          ))}
        </ul>
      </section>

      <section id="features" className="section" aria-labelledby="features-title">
        <div className="container">
          <h2 id="features-title" className="section__title">Everything you need to understand a scheme</h2>
          <p className="section__sub">Discovery is live today. The rest is being built and is marked so you know what to expect.</p>
          <div ref={ref} className="cards reveal-group">
            {FEATURES.map(({ icon: Icon, title, body, live }, i) => (
              <article className="card feature" key={title} style={{ '--i': i }}>
                <span className="feature__icon"><Icon /></span>
                <h3>{title}</h3>
                <p>{body}</p>
                <span className={`status ${live ? 'status--live' : 'status--soon'}`}>{live ? 'Available now' : 'Coming soon'}</span>
              </article>
            ))}
          </div>
        </div>
      </section>
    </>
  )
}
