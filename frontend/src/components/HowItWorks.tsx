import { CheckCircle } from 'lucide-react';

export default function HowItWorks() {
  return (
    <section id="how-it-works" className="py-20 bg-slate-800 text-white">
      <div className="container mx-auto text-center">
        <h2 className="text-4xl font-bold mb-12">How It Works</h2>
        <div className="grid md:grid-cols-3 gap-12">
          <div className="flex flex-col items-center">
            <CheckCircle className="w-12 h-12 text-emerald-400 mb-4" />
            <h3 className="text-2xl font-semibold mb-2">1. Submit Your Request</h3>
            <p className="text-slate-400">
              Provide your assignment details, including topic, word count, and citation style.
            </p>
          </div>
          <div className="flex flex-col items-center">
            <CheckCircle className="w-12 h-12 text-emerald-400 mb-4" />
            <h3 className="text-2xl font-semibold mb-2">2. AI-Powered Research</h3>
            <p className="text-slate-400">
              Our advanced AI agents conduct thorough research to gather the most relevant and credible sources.
            </p>
          </div>
          <div className="flex flex-col items-center">
            <CheckCircle className="w-12 h-12 text-emerald-400 mb-4" />
            <h3 className="text-2xl font-semibold mb-2">3. Review and Submit</h3>
            <p className="text-slate-400">
              Receive a high-quality, plagiarism-free paper, complete with a Turnitin clearance report.
            </p>
          </div>
        </div>
      </div>
    </section>
  );
}