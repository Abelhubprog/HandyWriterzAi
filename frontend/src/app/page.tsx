import Header from '@/components/Header'
import Hero from '@/components/Hero'
import FeatureGrid from '@/components/FeatureGrid'
import HowItWorks from '@/components/HowItWorks'
import CTA from '@/components/CTA'
import Footer from '@/components/Footer'

export default function LandingPage() {
  return (
    <div className="bg-slate-900">
      <Header />
      <Hero />
      <FeatureGrid />
      <HowItWorks />
      <CTA />
      <Footer />
    </div>
  )
}