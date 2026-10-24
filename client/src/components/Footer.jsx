import { Logo } from './Icons'
import { NAV_LINKS } from '../config'

export default function Footer() {
  return (
    <footer id="about" className="footer">
      <div className="container footer__grid">
        <div>
          <a className="brand" href="#home"><Logo /><span>SchemeWise</span></a>
          <p className="footer__about">An AI-powered assistant for discovering government schemes, understanding eligibility, and preparing documents.</p>
        </div>
        <nav aria-label="Footer">
          <ul className="footer__links">
            {NAV_LINKS.map((l) => <li key={l.href}><a href={l.href}>{l.label}</a></li>)}
          </ul>
        </nav>
      </div>
      <div className="container footer__legal">
        <p>SchemeWise provides informational assistance only and is not affiliated with or endorsed by any government body. It does not guarantee eligibility or benefits. Please verify all requirements against official scheme sources before applying.</p>
        <p>© {new Date().getFullYear()} SchemeWise</p>
      </div>
    </footer>
  )
}
