import { useEffect, useRef, useState } from 'react'
import { Close, Logo, Menu } from './Icons'
import { ELIGIBILITY_HREF, NAV_LINKS } from '../config'

export default function Navbar() {
  const [open, setOpen] = useState(false)
  const toggleRef = useRef(null)

  useEffect(() => {
    if (!open) return
    const onKey = (e) => { if (e.key === 'Escape') { setOpen(false); toggleRef.current?.focus() } }
    document.addEventListener('keydown', onKey)
    return () => document.removeEventListener('keydown', onKey)
  }, [open])

  const close = () => setOpen(false)

  return (
    <header className="nav">
      <nav className="nav__inner" aria-label="Primary">
        <a className="brand" href="#home" onClick={close}>
          <Logo /><span>SchemeWise</span>
        </a>

        <ul id="nav-menu" className={`nav__links ${open ? 'is-open' : ''}`}>
          {NAV_LINKS.map((l) => (
            <li key={l.href}><a href={l.href} onClick={close}>{l.label}</a></li>
          ))}
          <li className="nav__cta-mobile"><a className="btn btn--primary" href={ELIGIBILITY_HREF} onClick={close}>Check Eligibility</a></li>
        </ul>

        <a className="btn btn--primary nav__cta" href={ELIGIBILITY_HREF}>Check Eligibility</a>

        <button
          ref={toggleRef}
          type="button"
          className="nav__toggle"
          aria-expanded={open}
          aria-controls="nav-menu"
          aria-label={open ? 'Close menu' : 'Open menu'}
          onClick={() => setOpen((v) => !v)}
        >
          {open ? <Close /> : <Menu />}
        </button>
      </nav>
    </header>
  )
}
