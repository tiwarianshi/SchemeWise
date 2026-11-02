import { ArrowRight } from './Icons'
import { SCHEMES_HREF } from '../config'

export default function FinalCta() {
  return (
    <section className="section" aria-labelledby="cta-title">
      <div className="container">
        <div className="cta">
          <h2 id="cta-title">Your next opportunity starts with the right information.</h2>
          <p>Explore available schemes and understand their requirements with confidence.</p>
          <a className="btn btn--primary btn--lg" href={SCHEMES_HREF}>Explore Schemes <ArrowRight /></a>
        </div>
      </div>
    </section>
  )
}
