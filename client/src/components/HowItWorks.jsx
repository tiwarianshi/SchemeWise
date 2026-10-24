import { useReveal } from '../hooks/useReveal'

const STEPS = [
  { title: 'Explore schemes', body: 'Browse available schemes and read what each one covers.' },
  { title: 'Understand eligibility', body: 'See the stated requirements and which details you may be missing.' },
  { title: 'Prepare your documents', body: 'Know which documents to gather before you apply.' },
]

export default function HowItWorks() {
  const ref = useReveal()
  return (
    <section id="how-it-works" className="section" aria-labelledby="how-title">
      <div className="container">
        <h2 id="how-title" className="section__title">How it works</h2>
        <p className="section__sub">SchemeWise gives informational guidance. It is not an official eligibility decision or approval from any government body.</p>
        <ol ref={ref} className="steps reveal-group">
          {STEPS.map((s, i) => (
            <li className="step" key={s.title} style={{ '--i': i }}>
              <span className="step__num" aria-hidden="true">{i + 1}</span>
              <h3>{s.title}</h3>
              <p>{s.body}</p>
            </li>
          ))}
        </ol>
      </div>
    </section>
  )
}
