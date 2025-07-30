export default async function OriginalityPage({ params }: { params: Promise<{ traceId: string }> }) {
  const { traceId } = await params;
  
  return (
    <div>
      <h1 className="text-2xl font-bold">Originality Check</h1>
      <p>Trace ID: {traceId}</p>
    </div>
  );
}
