import React from 'react';

export interface AgentActivity {
  agentName: string;
  status: 'running' | 'completed' | 'failed';
  timestamp: string;
}

interface AgentActivityDisplayProps {
  activities: AgentActivity[];
}

const AgentActivityDisplay: React.FC<AgentActivityDisplayProps> = ({ activities }) => {
  return (
    <div className="p-4 border rounded-lg">
      <h3 className="text-lg font-semibold mb-2">Agent Activity</h3>
      <ul className="space-y-2">
        {activities.map((activity, index) => (
          <li key={index} className="flex items-center justify-between">
            <span>{activity.agentName}</span>
            <span className={`px-2 py-1 text-xs rounded-full ${
              activity.status === 'completed' ? 'bg-green-500 text-white' :
              activity.status === 'running' ? 'bg-blue-500 text-white' :
              'bg-red-500 text-white'
            }`}>
              {activity.status}
            </span>
          </li>
        ))}
      </ul>
    </div>
  );
};

export default AgentActivityDisplay;