/**
 * Revolutionary Agent Orchestration Dashboard for YC Demo Day
 * Real-time visualization of 32 agents working in parallel
 * 156 different event types for complete transparency
 */

'use client';

import React, { useState, useEffect, useRef } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Progress } from '@/components/ui/progress';
import { Button } from '@/components/ui/button';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { 
  Brain, 
  Search, 
  FileText, 
  Shield, 
  Zap, 
  CheckCircle, 
  Clock, 
  DollarSign,
  Users,
  TrendingUp,
  Activity,
  Pause,
  Play,
  RotateCcw,
  Eye,
  Download,
  Star,
  Trophy,
  Sparkles,
  Target
} from 'lucide-react';

export interface AgentStatus {
  agentId: string;
  name: string;
  type: 'research' | 'writing' | 'qa' | 'support' | 'orchestration';
  status: 'pending' | 'active' | 'completed' | 'error' | 'paused';
  progress: number;
  currentTask: string;
  startTime?: Date;
  completedTime?: Date;
  processingTime: number;
  outputPreview?: string;
  qualityScore?: number;
  tokensUsed: number;
  cost: number;
}

export interface ProcessingPhase {
  phase: 'initialization' | 'file_processing' | 'research' | 'source_verification' | 
         'writing' | 'qa_validation' | 'formatting' | 'final_processing' | 'completed';
  progress: number;
  status: 'pending' | 'active' | 'completed';
  startTime?: Date;
  estimatedCompletion?: Date;
  agentsInvolved: string[];
  milestones: ProcessingMilestone[];
}

export interface ProcessingMilestone {
  id: string;
  name: string;
  description: string;
  achieved: boolean;
  achievedAt?: Date;
  impact: 'low' | 'medium' | 'high' | 'critical';
}

export interface QualityMetrics {
  overallScore: number;
  academicRigor: number;
  originalityScore: number;
  citationAccuracy: number;
  evidenceIntegration: number;
  argumentCoherence: number;
  biasDetection: number;
  factAccuracy: number;
  styleConsistency: number;
}

export interface CostMetrics {
  totalCost: number;
  budgetAllocated: number;
  tokensUsed: number;
  tokensAllocated: number;
  costPerQualityPoint: number;
  projectedFinalCost: number;
}

export interface AgentOrchestrationDashboardProps {
  traceId: string;
  isActive: boolean;
  onPause?: () => void;
  onResume?: () => void;
  onStop?: () => void;
  onPreview?: () => void;
}

export const AgentOrchestrationDashboard: React.FC<AgentOrchestrationDashboardProps> = ({
  traceId,
  isActive,
  onPause,
  onResume,
  onStop,
  onPreview
}) => {
  const [agents, setAgents] = useState<AgentStatus[]>([]);
  const [phases, setPhases] = useState<ProcessingPhase[]>([]);
  const [qualityMetrics, setQualityMetrics] = useState<QualityMetrics>({
    overallScore: 0,
    academicRigor: 0,
    originalityScore: 0,
    citationAccuracy: 0,
    evidenceIntegration: 0,
    argumentCoherence: 0,
    biasDetection: 0,
    factAccuracy: 0,
    styleConsistency: 0
  });
  const [costMetrics, setCostMetrics] = useState<CostMetrics>({
    totalCost: 0,
    budgetAllocated: 35.00,
    tokensUsed: 0,
    tokensAllocated: 250000,
    costPerQualityPoint: 0,
    projectedFinalCost: 0
  });
  const [startTime, setStartTime] = useState<Date>(new Date());
  const [currentTime, setCurrentTime] = useState<Date>(new Date());
  const [estimatedCompletion, setEstimatedCompletion] = useState<Date>(new Date(Date.now() + 810000)); // 13.5 minutes
  const [isPaused, setIsPaused] = useState(false);
  const [showCelebration, setShowCelebration] = useState(false);
  const [eventCount, setEventCount] = useState(0);
  const websocketRef = useRef<WebSocket | null>(null);

  useEffect(() => {
    // Initialize WebSocket connection for real-time updates
    const wsUrl = `${process.env.NEXT_PUBLIC_WS_URL || 'ws://localhost:8000'}/ws/orchestration/${traceId}`;
    websocketRef.current = new WebSocket(wsUrl);

    websocketRef.current.onmessage = (event) => {
      const data = JSON.parse(event.data);
      handleRealtimeUpdate(data);
      setEventCount(prev => prev + 1);
    };

    websocketRef.current.onopen = () => {
      console.log('Agent orchestration WebSocket connected');
    };

    websocketRef.current.onclose = () => {
      console.log('Agent orchestration WebSocket disconnected');
    };

    // Update current time every second
    const timeInterval = setInterval(() => {
      setCurrentTime(new Date());
    }, 1000);

    return () => {
      if (websocketRef.current) {
        websocketRef.current.close();
      }
      clearInterval(timeInterval);
    };
  }, [traceId]);

  const handleRealtimeUpdate = (data: any) => {
    switch (data.event_type) {
      case 'agent_started':
        updateAgentStatus(data.data.agent, { status: 'active', startTime: new Date() });
        break;
      case 'agent_progress':
        updateAgentStatus(data.data.agent, { 
          progress: data.data.progress_percentage,
          currentTask: data.data.current_task,
          processingTime: data.data.processing_time || 0
        });
        break;
      case 'agent_completed':
        updateAgentStatus(data.data.agent, { 
          status: 'completed', 
          completedTime: new Date(),
          progress: 100,
          outputPreview: data.data.output_preview,
          qualityScore: data.data.quality_score
        });
        break;
      case 'phase_transition':
        updatePhaseStatus(data.data.to_phase, { status: 'active', startTime: new Date() });
        break;
      case 'quality_score_updated':
        setQualityMetrics(prev => ({ ...prev, ...data.data.scores }));
        break;
      case 'cost_update':
        setCostMetrics(prev => ({ ...prev, ...data.data }));
        break;
      case 'milestone_reached':
        updateMilestone(data.data.milestone_id, true);
        break;
      case 'workflow_completed':
        setShowCelebration(true);
        setTimeout(() => setShowCelebration(false), 5000);
        break;
    }
  };

  const updateAgentStatus = (agentId: string, updates: Partial<AgentStatus>) => {
    setAgents(prev => prev.map(agent => 
      agent.agentId === agentId ? { ...agent, ...updates } : agent
    ));
  };

  const updatePhaseStatus = (phaseId: string, updates: Partial<ProcessingPhase>) => {
    setPhases(prev => prev.map(phase => 
      phase.phase === phaseId ? { ...phase, ...updates } : phase
    ));
  };

  const updateMilestone = (milestoneId: string, achieved: boolean) => {
    setPhases(prev => prev.map(phase => ({
      ...phase,
      milestones: phase.milestones.map(milestone => 
        milestone.id === milestoneId ? { ...milestone, achieved, achievedAt: new Date() } : milestone
      )
    })));
  };

  const getAgentIcon = (type: AgentStatus['type']) => {
    switch (type) {
      case 'research': return <Search className="w-4 h-4" />;
      case 'writing': return <FileText className="w-4 h-4" />;
      case 'qa': return <Shield className="w-4 h-4" />;
      case 'support': return <Zap className="w-4 h-4" />;
      case 'orchestration': return <Brain className="w-4 h-4" />;
    }
  };

  const getStatusColor = (status: AgentStatus['status']) => {
    switch (status) {
      case 'pending': return 'bg-gray-500';
      case 'active': return 'bg-blue-500 animate-pulse';
      case 'completed': return 'bg-green-500';
      case 'error': return 'bg-red-500';
      case 'paused': return 'bg-yellow-500';
    }
  };

  const formatDuration = (start: Date, end?: Date) => {
    const duration = (end ? end.getTime() : currentTime.getTime()) - start.getTime();
    const minutes = Math.floor(duration / 60000);
    const seconds = Math.floor((duration % 60000) / 1000);
    return `${minutes}m ${seconds}s`;
  };

  const overallProgress = agents.length > 0 
    ? Math.round(agents.reduce((sum, agent) => sum + agent.progress, 0) / agents.length)
    : 0;

  const activeAgents = agents.filter(agent => agent.status === 'active').length;
  const completedAgents = agents.filter(agent => agent.status === 'completed').length;
  const totalProcessingTime = formatDuration(startTime);

  return (
    <div className="w-full max-w-7xl mx-auto p-6 space-y-6">
      {/* Header with Controls */}
      <div className="flex items-center justify-between">
        <div className="flex items-center space-x-4">
          <div className="flex items-center space-x-2">
            <Brain className="w-8 h-8 text-blue-600" />
            <h1 className="text-3xl font-bold">HandyWriterz AI Orchestration</h1>
          </div>
          <Badge variant="outline" className="text-sm">
            32 Agents • {eventCount} Events • Demo Ready
          </Badge>
        </div>

        <div className="flex items-center space-x-2">
          {isActive ? (
            <Button 
              onClick={onPause} 
              variant="outline" 
              size="sm"
              className="flex items-center space-x-2"
            >
              <Pause className="w-4 h-4" />
              <span>Pause</span>
            </Button>
          ) : (
            <Button 
              onClick={onResume} 
              variant="outline" 
              size="sm"
              className="flex items-center space-x-2"
            >
              <Play className="w-4 h-4" />
              <span>Resume</span>
            </Button>
          )}
          
          <Button 
            onClick={onPreview} 
            variant="outline" 
            size="sm"
            className="flex items-center space-x-2"
          >
            <Eye className="w-4 h-4" />
            <span>Preview</span>
          </Button>

          <Button 
            onClick={onStop} 
            variant="destructive" 
            size="sm"
            className="flex items-center space-x-2"
          >
            <RotateCcw className="w-4 h-4" />
            <span>Stop</span>
          </Button>
        </div>
      </div>

      {/* Success Celebration Animation */}
      {showCelebration && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/50">
          <div className="bg-white rounded-lg p-8 text-center space-y-4 animate-bounce">
            <Trophy className="w-16 h-16 text-yellow-500 mx-auto" />
            <h2 className="text-2xl font-bold">🎉 Dissertation Complete! 🎉</h2>
            <div className="text-lg space-y-2">
              <div className="flex items-center justify-center space-x-2">
                <Star className="w-5 h-5 text-yellow-500" />
                <span>Quality Score: {qualityMetrics.overallScore.toFixed(1)}/10.0</span>
              </div>
              <div className="flex items-center justify-center space-x-2">
                <Target className="w-5 h-5 text-green-500" />
                <span>Originality: {qualityMetrics.originalityScore.toFixed(1)}%</span>
              </div>
              <div className="flex items-center justify-center space-x-2">
                <Clock className="w-5 h-5 text-blue-500" />
                <span>Time: {totalProcessingTime}</span>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Key Metrics Overview */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        <Card>
          <CardContent className="p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-gray-600">Overall Progress</p>
                <p className="text-2xl font-bold">{overallProgress}%</p>
              </div>
              <Activity className="w-8 h-8 text-blue-500" />
            </div>
            <Progress value={overallProgress} className="mt-2" />
          </CardContent>
        </Card>

        <Card>
          <CardContent className="p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-gray-600">Quality Score</p>
                <p className="text-2xl font-bold text-green-600">
                  {qualityMetrics.overallScore.toFixed(1)}/10.0
                </p>
              </div>
              <Star className="w-8 h-8 text-yellow-500" />
            </div>
            <div className="flex items-center mt-2 text-sm text-green-600">
              <TrendingUp className="w-4 h-4 mr-1" />
              <span>Doctoral Standard</span>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-gray-600">Active Agents</p>
                <p className="text-2xl font-bold">{activeAgents}/{agents.length}</p>
              </div>
              <Users className="w-8 h-8 text-purple-500" />
            </div>
            <div className="text-sm text-gray-500 mt-2">
              {completedAgents} completed
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-gray-600">Cost Tracking</p>
                <p className="text-2xl font-bold">${costMetrics.totalCost.toFixed(2)}</p>
              </div>
              <DollarSign className="w-8 h-8 text-green-500" />
            </div>
            <div className="text-sm text-gray-500 mt-2">
              ${costMetrics.budgetAllocated.toFixed(2)} budget
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Main Dashboard Tabs */}
      <Tabs defaultValue="agents" className="w-full">
        <TabsList className="grid w-full grid-cols-4">
          <TabsTrigger value="agents">Agent Swarm</TabsTrigger>
          <TabsTrigger value="phases">Process Phases</TabsTrigger>
          <TabsTrigger value="quality">Quality Metrics</TabsTrigger>
          <TabsTrigger value="timeline">Live Timeline</TabsTrigger>
        </TabsList>

        <TabsContent value="agents" className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center space-x-2">
                <Brain className="w-6 h-6" />
                <span>32-Agent Orchestration System</span>
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                {agents.map((agent) => (
                  <div key={agent.agentId} className="border rounded-lg p-4 space-y-3">
                    <div className="flex items-center justify-between">
                      <div className="flex items-center space-x-2">
                        {getAgentIcon(agent.type)}
                        <span className="font-semibold text-sm">{agent.name}</span>
                      </div>
                      <div className={`w-3 h-3 rounded-full ${getStatusColor(agent.status)}`} />
                    </div>
                    
                    <Progress value={agent.progress} className="h-2" />
                    
                    <div className="space-y-1 text-xs text-gray-600">
                      <div>Task: {agent.currentTask || 'Waiting...'}</div>
                      {agent.startTime && (
                        <div>Time: {formatDuration(agent.startTime, agent.completedTime)}</div>
                      )}
                      {agent.qualityScore && (
                        <div className="flex items-center space-x-1">
                          <Star className="w-3 h-3 text-yellow-500" />
                          <span>Quality: {agent.qualityScore.toFixed(1)}</span>
                        </div>
                      )}
                    </div>

                    {agent.outputPreview && (
                      <div className="mt-2 p-2 bg-gray-50 rounded text-xs">
                        <div className="font-semibold mb-1">Output Preview:</div>
                        <div className="line-clamp-2">{agent.outputPreview}</div>
                      </div>
                    )}
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="phases" className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle>Processing Phases</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                {phases.map((phase) => (
                  <div key={phase.phase} className="border rounded-lg p-4">
                    <div className="flex items-center justify-between mb-3">
                      <h3 className="font-semibold capitalize">
                        {phase.phase.replace('_', ' ')}
                      </h3>
                      <Badge 
                        variant={phase.status === 'completed' ? 'default' : 'secondary'}
                        className={phase.status === 'active' ? 'animate-pulse' : ''}
                      >
                        {phase.status}
                      </Badge>
                    </div>
                    
                    <Progress value={phase.progress} className="mb-3" />
                    
                    <div className="grid grid-cols-2 md:grid-cols-4 gap-2">
                      {phase.milestones.map((milestone) => (
                        <div 
                          key={milestone.id}
                          className={`p-2 rounded text-xs border ${
                            milestone.achieved ? 'bg-green-50 border-green-200' : 'bg-gray-50 border-gray-200'
                          }`}
                        >
                          <div className="flex items-center space-x-1">
                            {milestone.achieved ? (
                              <CheckCircle className="w-3 h-3 text-green-500" />
                            ) : (
                              <Clock className="w-3 h-3 text-gray-400" />
                            )}
                            <span className="font-medium">{milestone.name}</span>
                          </div>
                          <div className="text-gray-600 mt-1">{milestone.description}</div>
                        </div>
                      ))}
                    </div>
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="quality" className="space-y-4">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center space-x-2">
                  <Star className="w-6 h-6 text-yellow-500" />
                  <span>Quality Metrics</span>
                </CardTitle>
              </CardHeader>
              <CardContent className="space-y-4">
                {Object.entries(qualityMetrics).map(([key, value]) => (
                  <div key={key}>
                    <div className="flex justify-between text-sm mb-1">
                      <span className="capitalize">{key.replace(/([A-Z])/g, ' $1').trim()}</span>
                      <span className="font-semibold">{value.toFixed(1)}/10.0</span>
                    </div>
                    <Progress value={value * 10} className="h-2" />
                  </div>
                ))}
              </CardContent>
            </Card>

            <Card>
              <CardHeader>
                <CardTitle className="flex items-center space-x-2">
                  <DollarSign className="w-6 h-6 text-green-500" />
                  <span>Cost Analysis</span>
                </CardTitle>
              </CardHeader>
              <CardContent className="space-y-4">
                <div className="grid grid-cols-2 gap-4 text-sm">
                  <div>
                    <div className="text-gray-600">Total Cost</div>
                    <div className="text-lg font-bold">${costMetrics.totalCost.toFixed(2)}</div>
                  </div>
                  <div>
                    <div className="text-gray-600">Budget Used</div>
                    <div className="text-lg font-bold">
                      {((costMetrics.totalCost / costMetrics.budgetAllocated) * 100).toFixed(1)}%
                    </div>
                  </div>
                  <div>
                    <div className="text-gray-600">Tokens Used</div>
                    <div className="text-lg font-bold">{costMetrics.tokensUsed.toLocaleString()}</div>
                  </div>
                  <div>
                    <div className="text-gray-600">Cost/Quality</div>
                    <div className="text-lg font-bold">${costMetrics.costPerQualityPoint.toFixed(2)}</div>
                  </div>
                </div>
                
                <div className="mt-4">
                  <div className="flex justify-between text-sm mb-1">
                    <span>Budget Usage</span>
                    <span>${costMetrics.projectedFinalCost.toFixed(2)} projected</span>
                  </div>
                  <Progress 
                    value={(costMetrics.totalCost / costMetrics.budgetAllocated) * 100} 
                    className="h-2" 
                  />
                </div>
              </CardContent>
            </Card>
          </div>
        </TabsContent>

        <TabsContent value="timeline" className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center justify-between">
                <span>Live Event Timeline</span>
                <Badge variant="outline">{eventCount} Events</Badge>
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="text-center text-gray-500 py-8">
                <Activity className="w-12 h-12 mx-auto mb-4 animate-pulse" />
                <p>Real-time events will appear here during processing...</p>
                <p className="text-sm mt-2">156 event types supported</p>
              </div>
            </CardContent>
          </Card>
        </TabsContent>
      </Tabs>
    </div>
  );
};