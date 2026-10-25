import './App.css'
import Navbar from './components/Navbar'
import Hero from './components/Hero'
import Features from './components/Features'
import SchemesSection from './components/SchemesSection'
import HowItWorks from './components/HowItWorks'
import FinalCta from './components/FinalCta'
import Footer from './components/Footer'
import EligibilityChecker from './components/EligibilityChecker'

export default function App() {
  return (
    <>
      <a className="skip" href="#schemes">Skip to schemes</a>
      <Navbar />
      <main>
        <Hero />
        <Features />
        <SchemesSection />
         <EligibilityChecker />
        <HowItWorks />
        <FinalCta />
      </main>
      <Footer />
    </>
  )
}
