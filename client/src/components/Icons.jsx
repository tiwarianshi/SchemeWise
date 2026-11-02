/* eslint-disable react-refresh/only-export-components */
const base = { width: 20, height: 20, viewBox: '0 0 24 24', fill: 'none', stroke: 'currentColor', strokeWidth: 1.8, strokeLinecap: 'round', strokeLinejoin: 'round', 'aria-hidden': true, focusable: false }
const make = (d) => function Icon(props) { return <svg {...base} {...props}>{d}</svg> }

export const ArrowRight = make(<><path d="M5 12h14" /><path d="m13 6 6 6-6 6" /></>)
export const Search = make(<><circle cx="11" cy="11" r="7" /><path d="m20 20-3.5-3.5" /></>)
export const ShieldCheck = make(<><path d="M12 3 5 6v5c0 4.5 3 8 7 10 4-2 7-5.5 7-10V6l-7-3Z" /><path d="m9 12 2 2 4-4" /></>)
export const ListChecks = make(<><path d="m4 6 1.5 1.5L8 5" /><path d="m4 12 1.5 1.5L8 11" /><path d="m4 18 1.5 1.5L8 17" /><path d="M12 6h8M12 12h8M12 18h8" /></>)
export const FileText = make(<><path d="M14 3H7a2 2 0 0 0-2 2v14a2 2 0 0 0 2 2h10a2 2 0 0 0 2-2V8l-5-5Z" /><path d="M14 3v5h5M9 13h6M9 17h6" /></>)
export const Sparkles = make(<><path d="M12 3v4M12 17v4M3 12h4M17 12h4" /><path d="m6.5 6.5 2 2M15.5 15.5l2 2M17.5 6.5l-2 2M8.5 15.5l-2 2" /></>)
export const Menu = make(<><path d="M4 7h16M4 12h16M4 17h16" /></>)
export const Close = make(<><path d="m6 6 12 12M18 6 6 18" /></>)
export const Alert = make(<><circle cx="12" cy="12" r="9" /><path d="M12 8v5M12 16.5v.01" /></>)
export const Inbox = make(<><path d="M4 13 6.5 5h11L20 13" /><path d="M4 13v5a1 1 0 0 0 1 1h14a1 1 0 0 0 1-1v-5h-5l-1 2h-4l-1-2H4Z" /></>)
export const External = make(<><path d="M14 4h6v6M20 4l-9 9" /><path d="M18 14v5a1 1 0 0 1-1 1H5a1 1 0 0 1-1-1V7a1 1 0 0 1 1-1h5" /></>)
export const MapPin = make(<><path d="M12 21s7-6 7-11a7 7 0 0 0-14 0c0 5 7 11 7 11Z" /><circle cx="12" cy="10" r="2.5" /></>)

export function Logo({ size = 28 }) {
  return (
    <svg width={size} height={size} viewBox="0 0 32 32" aria-hidden="true" focusable="false">
      <defs>
        <linearGradient id="sw-logo" x1="0" y1="0" x2="32" y2="32" gradientUnits="userSpaceOnUse">
          <stop stopColor="#168BFF" /><stop offset="1" stopColor="#FF3D81" />
        </linearGradient>
      </defs>
      <rect width="32" height="32" rx="9" fill="url(#sw-logo)" />
      <path d="M10 21.5c1.4 1.4 3.4 2 5.6 2 3 0 5-1.3 5-3.4 0-2-1.5-2.8-4.4-3.4-2.7-.6-3.9-1-3.9-2.2 0-1.1 1.1-1.8 2.8-1.8 1.4 0 2.6.4 3.6 1.3l1.6-2.1c-1.2-1.1-2.9-1.7-5.1-1.7-2.9 0-4.9 1.4-4.9 3.6 0 2.1 1.6 3 4.4 3.5 2.5.5 3.8.9 3.8 2 0 1.1-1.1 1.8-2.9 1.8-1.7 0-3.1-.6-4.2-1.7L10 21.5Z" fill="#07090F" />
    </svg>
  )
}
