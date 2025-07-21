import React, { useEffect, useState } from 'react';

interface RoutingStats {
  total_requests: number;
  simple_requests: number;
  advanced_requests: number;
  hybrid_requests: number;
  average_complexity: number;
}

const RoutingDashboard: React.FC = () => {
  const [stats, setStats] = useState<RoutingStats | null>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchStats = async () => {
      try {
        const response = await fetch('/api/status');
        if (!response.ok) {
          throw new Error('Failed to fetch routing stats');
        }
        const data = await response.json();
        setStats(data.routing.statistics);
      } catch (err) {
        if (err instanceof Error) {
          setError(err.message);
        } else {
          setError('An unknown error occurred');
        }
      }
    };

    fetchStats();
    const interval = setInterval(fetchStats, 5000); // Refresh every 5 seconds

    return () => clearInterval(interval);
  }, []);

  if (error) {
    return <div className="p-8 text-red-500">Error: {error}</div>;
  }

  if (!stats) {
    return <div className="p-8">Loading routing statistics...</div>;
  }

  return (
    <div className="p-8">
      <h1 className="text-3xl font-bold mb-4">Routing Dashboard</h1>
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-8">
        <div className="p-4 border rounded-lg">
          <h2 className="text-xl font-semibold">Total Requests</h2>
          <p className="text-3xl">{stats.total_requests}</p>
        </div>
        <div className="p-4 border rounded-lg">
          <h2 className="text-xl font-semibold">Simple Requests</h2>
          <p className="text-3xl">{stats.simple_requests}</p>
        </div>
        <div className="p-4 border rounded-lg">
          <h2 className="text-xl font-semibold">Advanced Requests</h2>
          <p className="text-3xl">{stats.advanced_requests}</p>
        </div>
        <div className="p-4 border rounded-lg">
          <h2 className="text-xl font-semibold">Hybrid Requests</h2>
          <p className="text-3xl">{stats.hybrid_requests}</p>
        </div>
        <div className="p-4 border rounded-lg col-span-full">
          <h2 className="text-xl font-semibold">Average Complexity</h2>
          <p className="text-3xl">{stats.average_complexity.toFixed(2)}</p>
        </div>
      </div>
    </div>
  );
};

export default RoutingDashboard;