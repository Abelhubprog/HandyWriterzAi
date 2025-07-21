export default function OriginalityPage({ params }: { params: { traceId: string } }) {
  return (
    <div>
      <h1 className="text-2xl font-bold">Originality Check</h1>
      <p>Trace ID: {params.traceId}</p>
    </div>
  );
}
