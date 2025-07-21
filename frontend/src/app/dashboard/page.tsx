import React from 'react';
import AgentActivityDisplay, { AgentActivity } from '@/components/ui/AgentActivityDisplay';

const Dashboard: React.FC = () => {
  // Placeholder data - this will be replaced with real-time data from the backend
  const activities: AgentActivity[] = [
    { agentName: 'MasterOrchestrator', status: 'completed', timestamp: new Date().toISOString() },
    { agentName: 'EnhancedUserIntent', status: 'completed', timestamp: new Date().toISOString() },
    { agentName: 'GeminiSearchAgent', status: 'running', timestamp: new Date().toISOString() },
    { agentName: 'PerplexitySearchAgent', status: 'running', timestamp: new Date().toISOString() },
  ];

  return (
    <div className="p-8">
      <h1 className="text-3xl font-bold mb-4">System Dashboard</h1>
      <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
        <div>
          <h2 className="text-2xl font-semibold mb-4">Real-Time Agent Activity</h2>
          <AgentActivityDisplay activities={activities} />
        </div>
        <div>
          <h2 className="text-2xl font-semibold mb-4">Performance Metrics</h2>
          {/* Placeholder for performance charts */}
          <div className="p-4 border rounded-lg h-64 flex items-center justify-center">
            <p>Performance metrics will be displayed here.</p>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Dashboard;