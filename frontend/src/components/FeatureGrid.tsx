import FeatureCard from './FeatureCard';

export default function FeatureGrid() {
  return (
    <section className="px-6 py-16 bg-gradient-to-b from-slate-800 to-slate-900 text-slate-100">
      <div className="grid md:grid-cols-2 gap-6 max-w-5xl mx-auto">
        <FeatureCard
          title="Multi-modal context"
          copy="Drag PDFs, DOCX, audio and YouTube links."
          icon="📎"
        />
        <FeatureCard
          title="1 M-token brain"
          copy="Gemini 1.5 window—no compromise."
          icon="🧠"
        />
        <FeatureCard
          title="Turnitin safe-pass"
          copy="AI score 0 %, similarity < 10 %."
          icon="🛡️"
        />
        <FeatureCard
          title="Human checker marketplace"
          copy="Optional experts on standby."
          icon="🤝"
        />
      </div>
    </section>
  );
}