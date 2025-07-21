import React, { useState } from 'react';

const PerformanceBenchmark: React.FC = () => {
  const [overhead, setOverhead] = useState<number | null>(null);
  const [isTesting, setIsTesting] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const runBenchmark = async () => {
    setIsTesting(true);
    setError(null);
    setOverhead(null);

    try {
      const startTime = performance.now();
      const response = await fetch('/api/analyze', {
        method: 'POST',
        body: new URLSearchParams({ message: 'Simple test query' }),
      });
      const endTime = performance.now();

      if (!response.ok) {
        throw new Error('Failed to run benchmark');
      }

      setOverhead(endTime - startTime);
    } catch (err) {
      if (err instanceof Error) {
        setError(err.message);
      } else {
        setError('An unknown error occurred');
      }
    } finally {
      setIsTesting(false);
    }
  };

  return (
    <div className="p-8">
      <h1 className="text-3xl font-bold mb-4">Routing Performance Benchmark</h1>
      <div className="flex items-center space-x-4">
        <button
          onClick={runBenchmark}
          disabled={isTesting}
          className="px-4 py-2 bg-blue-500 text-white rounded-lg disabled:bg-gray-400"
        >
          {isTesting ? 'Testing...' : 'Run Benchmark'}
        </button>
        {overhead !== null && (
          <div className="text-xl">
            Routing Overhead: <span className="font-bold">{overhead.toFixed(2)}ms</span>
          </div>
        )}
        {error && <div className="text-red-500">Error: {error}</div>}
      </div>
    </div>
  );
};

export default PerformanceBenchmark;