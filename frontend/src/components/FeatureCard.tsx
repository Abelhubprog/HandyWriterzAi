interface Props {
  title: string;
  copy: string;
  icon: string;
}
export default function FeatureCard({ title, copy, icon }: Props) {
  return (
    <div className="flex flex-col items-center bg-slate-700/40 p-6 rounded-xl backdrop-blur-xs">
      <span className="text-3xl mb-3">{icon}</span>
      <h3 className="font-semibold text-center">{title}</h3>
      <p className="text-center text-sm text-slate-300 mt-2">{copy}</p>
    </div>
  );
}