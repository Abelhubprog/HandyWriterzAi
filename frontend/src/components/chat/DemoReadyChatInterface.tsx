/**
 * Demo-Ready Chat Interface for YC Demo Day
 * 13-minute doctoral dissertation generation with live visualization
 * Integration of all revolutionary components
 */

'use client';

import React, { useState, useEffect, useRef } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Textarea } from '@/components/ui/textarea';
import { Badge } from '@/components/ui/badge';
import { Progress } from '@/components/ui/progress';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { 
  Send, 
  Sparkles, 
  Trophy, 
  Clock, 
  Star, 
  Target, 
  DollarSign, 
  Brain, 
  Zap, 
  FileText, 
  Download, 
  Eye, 
  Share,
  Rocket,
  Crown,
  Award,
  TrendingUp,
  CheckCircle2,
  Users,
  Globe,
  Timer,
  Lightbulb,
  ArrowRight,
  Play,
  Pause,
  RotateCcw
} from 'lucide-react';

import { RevolutionaryFileUploader } from '@/components/upload/RevolutionaryFileUploader';
import { AgentOrchestrationDashboard } from '@/components/agent/AgentOrchestrationDashboard';
import { ProcessedContent } from '@/types/multimodal';

// Define ProcessingProgress locally since it's not exported from multimodal types
interface ProcessingProgress {
  fileId: string;
  fileName: string;
  progress: number;
  stage: string;
  insights: any[]; // Array of insights for metrics calculation
  processingTime: number; // Processing time for metrics
}
import { useAdvancedChat } from '@/hooks/useAdvancedChat';

interface DissertationResult {
  id: string;
  title: string;
  wordCount: number;
  qualityScore: number;
  originalityScore: number;
  citationCount: number;
  processingTime: number;
  cost: number;
  downloadUrls: {
    docx: string;
    pdf: string;
    slides: string;
    executive: string;
  };
  achievements: Achievement[];
}

interface Achievement {
  id: string;
  name: string;
  description: string;
  icon: 'quality' | 'speed' | 'originality' | 'citations' | 'innovation';
  achieved: boolean;
  value: number;
  target: number;
}

export const DemoReadyChatInterface: React.FC = () => {
  // Core state
  const [prompt, setPrompt] = useState('');
  const [writeupType, setWriteupType] = useState('dissertation');
  const [citationStyle, setCitationStyle] = useState('harvard');
  const [academicLevel, setAcademicLevel] = useState('doctoral');
  const [traceId] = useState(`trace_${Date.now()}_demo`);
  
  // Processing state
  const [isProcessing, setIsProcessing] = useState(false);
  const [isPaused, setIsPaused] = useState(false);
  const [processedFiles, setProcessedFiles] = useState<ProcessedContent[]>([]);
  const [overallProgress, setOverallProgress] = useState(0);
  const [currentPhase, setCurrentPhase] = useState('initialization');
  const [startTime, setStartTime] = useState<Date | null>(null);
  const [estimatedCompletion, setEstimatedCompletion] = useState<Date | null>(null);
  
  // Results state
  const [dissertationResult, setDissertationResult] = useState<DissertationResult | null>(null);
  const [showCelebration, setShowCelebration] = useState(false);
  const [achievements, setAchievements] = useState<Achievement[]>([
    {
      id: 'quality',
      name: 'Doctoral Excellence',
      description: 'Achieve 9.0+ quality score',
      icon: 'quality',
      achieved: false,
      value: 0,
      target: 9.0
    },
    {
      id: 'speed',
      name: 'Lightning Fast',
      description: 'Complete in under 15 minutes',
      icon: 'speed',
      achieved: false,
      value: 0,
      target: 900 // 15 minutes in seconds
    },
    {
      id: 'originality',
      name: 'Highly Original',
      description: '85%+ originality score',
      icon: 'originality',
      achieved: false,
      value: 0,
      target: 85
    },
    {
      id: 'citations',
      name: 'Research Master',
      description: '40+ academic citations',
      icon: 'citations',
      achieved: false,
      value: 0,
      target: 40
    }
  ]);

  // Demo metrics
  const [liveMetrics, setLiveMetrics] = useState({
    agentsActive: 0,
    eventsProcessed: 0,
    tokensGenerated: 0,
    currentCost: 0,
    qualityScore: 0,
    processingTime: 0
  });

  const { sendMessage, messages, isLoading } = useAdvancedChat();

  // Sample sophisticated prompt for demo
  const demoPrompt = `I need a comprehensive 8000-word doctoral dissertation on "The Intersection of Artificial Intelligence and International Cancer Treatment Protocols: Legal, Ethical, and Implementation Frameworks in Global Healthcare Governance"

Requirements:
- Focus on international law and regulatory compliance
- Analyze AI implementation in 15+ countries  
- Include cost-benefit analysis with economic modeling
- Integrate uploaded research files and audio/video sources
- Use PRISMA methodology for systematic review
- Harvard citation style with 40+ peer-reviewed sources
- Include methodology section, literature review, analysis, and conclusions
- Generate supplementary slides and infographics
- Ensure 90%+ originality score
- Target high-impact journal submission standards

Please process all uploaded files and integrate their content strategically throughout the dissertation.`;

  useEffect(() => {
    // Set demo prompt by default
    setPrompt(demoPrompt);
  }, []);

  const handleFilesProcessed = (files: ProcessedContent[]) => {
    setProcessedFiles(files);
  };

  const handleProcessingUpdate = (progress: ProcessingProgress[]) => {
    const totalProgress = progress.reduce((sum, p) => sum + p.progress, 0) / progress.length;
    setOverallProgress(totalProgress);
    
    // Update live metrics
    setLiveMetrics(prev => ({
      ...prev,
      tokensGenerated: progress.reduce((sum, p) => sum + p.insights.length * 100, 0),
      processingTime: progress.reduce((sum, p) => sum + p.processingTime, 0)
    }));
  };

  const handleStartDissertation = async () => {
    if (!prompt.trim()) return;

    setIsProcessing(true);
    setStartTime(new Date());
    setEstimatedCompletion(new Date(Date.now() + 810000)); // 13.5 minutes
    setCurrentPhase('file_processing');

    try {
      // This would call the actual API
      const response = await sendMessage(prompt, writeupType, {
        citationStyle,
        academicLevel,
        // Note: processedFiles and traceId would need to be handled differently
        // in the actual implementation as they're not part of the options interface
      });

      // Simulate processing completion after demo duration (only in demo mode)
      if (process.env.NEXT_PUBLIC_DEMO_MODE === 'true') {
        setTimeout(() => {
          simulateCompletion();
        }, 13.5 * 60 * 1000);
      }

    } catch (error) {
      console.error('Processing failed:', error);
      setIsProcessing(false);
    }
  };

  const simulateCompletion = () => {
    const result: DissertationResult = {
      id: 'diss_001',
      title: 'The Intersection of Artificial Intelligence and International Cancer Treatment Protocols',
      wordCount: 8734,
      qualityScore: 9.1,
      originalityScore: 88.7,
      citationCount: 67,
      processingTime: 13.45, // 13 minutes 27 seconds
      cost: 34.72,
      downloadUrls: {
        docx: '/downloads/dissertation.docx',
        pdf: '/downloads/dissertation.pdf',
        slides: '/downloads/presentation.pptx',
        executive: '/downloads/executive-summary.pdf'
      },
      achievements: []
    };

    setDissertationResult(result);
    setIsProcessing(false);
    setShowCelebration(true);

    // Update achievements
    setAchievements(prev => prev.map(achievement => {
      let achieved = false;
      let value = 0;

      switch (achievement.id) {
        case 'quality':
          value = result.qualityScore;
          achieved = value >= achievement.target;
          break;
        case 'speed':
          value = result.processingTime * 60; // Convert to seconds
          achieved = value <= achievement.target;
          break;
        case 'originality':
          value = result.originalityScore;
          achieved = value >= achievement.target;
          break;
        case 'citations':
          value = result.citationCount;
          achieved = value >= achievement.target;
          break;
      }

      return { ...achievement, achieved, value };
    }));

    setTimeout(() => setShowCelebration(false), 10000);
  };

  const handlePause = () => setIsPaused(true);
  const handleResume = () => setIsPaused(false);
  const handleStop = () => {
    setIsProcessing(false);
    setIsPaused(false);
    setOverallProgress(0);
  };

  const getAchievementIcon = (icon: Achievement['icon']) => {
    switch (icon) {
      case 'quality': return <Star className="w-5 h-5" />;
      case 'speed': return <Zap className="w-5 h-5" />;
      case 'originality': return <Target className="w-5 h-5" />;
      case 'citations': return <FileText className="w-5 h-5" />;
      case 'innovation': return <Lightbulb className="w-5 h-5" />;
    }
  };

  const formatTime = (seconds: number) => {
    const mins = Math.floor(seconds / 60);
    const secs = Math.floor(seconds % 60);
    return `${mins}m ${secs}s`;
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-purple-50 p-4">
      <div className="max-w-7xl mx-auto space-y-6">
        {/* Demo Header */}
        <div className="text-center space-y-4">
          <div className="flex items-center justify-center space-x-3">
            <Crown className="w-12 h-12 text-yellow-500" />
            <h1 className="text-4xl font-bold bg-gradient-to-r from-blue-600 to-purple-600 bg-clip-text text-transparent">
              HandyWriterz AI
            </h1>
            <Crown className="w-12 h-12 text-yellow-500" />
          </div>
          <p className="text-xl text-gray-600">
            Revolutionary Academic AI • 13-Minute Doctoral Dissertations • 9.1/10.0 Quality
          </p>
          <div className="flex justify-center space-x-4">
            <Badge variant="outline" className="text-green-600 border-green-600">
              ✨ YC Demo Day Ready
            </Badge>
            <Badge variant="outline" className="text-blue-600 border-blue-600">
              🚀 32 AI Agents
            </Badge>
            <Badge variant="outline" className="text-purple-600 border-purple-600">
              🧠 Gemini 2.5 Pro
            </Badge>
            <Badge variant="outline" className="text-red-600 border-red-600">
              💎 $2.3B Market
            </Badge>
          </div>
        </div>

        {/* Success Celebration */}
        {showCelebration && dissertationResult && (
          <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/70 backdrop-blur-sm">
            <Card className="max-w-2xl w-full mx-4 border-2 border-yellow-400">
              <CardContent className="p-8 text-center space-y-6">
                <div className="animate-bounce">
                  <Trophy className="w-20 h-20 text-yellow-500 mx-auto" />
                </div>
                
                <div className="space-y-2">
                  <h2 className="text-3xl font-bold text-green-600">
                    🎉 DISSERTATION COMPLETE! 🎉
                  </h2>
                  <p className="text-lg text-gray-600">
                    Revolutionary AI generates doctoral-quality research in record time
                  </p>
                </div>

                <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                  <div className="space-y-1">
                    <div className="text-2xl font-bold text-green-600">
                      {dissertationResult.qualityScore.toFixed(1)}
                    </div>
                    <div className="text-sm text-gray-600">Quality Score</div>
                  </div>
                  <div className="space-y-1">
                    <div className="text-2xl font-bold text-blue-600">
                      {dissertationResult.originalityScore.toFixed(1)}%
                    </div>
                    <div className="text-sm text-gray-600">Originality</div>
                  </div>
                  <div className="space-y-1">
                    <div className="text-2xl font-bold text-purple-600">
                      {formatTime(dissertationResult.processingTime * 60)}
                    </div>
                    <div className="text-sm text-gray-600">Processing Time</div>
                  </div>
                  <div className="space-y-1">
                    <div className="text-2xl font-bold text-yellow-600">
                      {dissertationResult.wordCount.toLocaleString()}
                    </div>
                    <div className="text-sm text-gray-600">Words</div>
                  </div>
                </div>

                <div className="flex justify-center space-x-3">
                  <Button className="flex items-center space-x-2">
                    <Download className="w-4 h-4" />
                    <span>Download All</span>
                  </Button>
                  <Button variant="outline" className="flex items-center space-x-2">
                    <Eye className="w-4 h-4" />
                    <span>Preview</span>
                  </Button>
                  <Button variant="outline" className="flex items-center space-x-2">
                    <Share className="w-4 h-4" />
                    <span>Share</span>
                  </Button>
                </div>
              </CardContent>
            </Card>
          </div>
        )}

        <Tabs defaultValue="compose" className="w-full">
          <TabsList className="grid w-full grid-cols-4">
            <TabsTrigger value="compose">Compose</TabsTrigger>
            <TabsTrigger value="upload">File Upload</TabsTrigger>
            <TabsTrigger value="orchestration">AI Orchestration</TabsTrigger>
            <TabsTrigger value="results">Results</TabsTrigger>
          </TabsList>

          <TabsContent value="compose" className="space-y-6">
            {/* Configuration Panel */}
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center space-x-2">
                  <Sparkles className="w-6 h-6 text-purple-500" />
                  <span>Dissertation Configuration</span>
                </CardTitle>
              </CardHeader>
              <CardContent className="space-y-4">
                <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                  <div>
                    <label className="text-sm font-medium mb-2 block">Document Type</label>
                    <Select value={writeupType} onValueChange={setWriteupType}>
                      <SelectTrigger>
                        <SelectValue />
                      </SelectTrigger>
                      <SelectContent>
                        <SelectItem value="dissertation">Doctoral Dissertation</SelectItem>
                        <SelectItem value="thesis">Master's Thesis</SelectItem>
                        <SelectItem value="research_paper">Research Paper</SelectItem>
                        <SelectItem value="review_article">Review Article</SelectItem>
                      </SelectContent>
                    </Select>
                  </div>

                  <div>
                    <label className="text-sm font-medium mb-2 block">Citation Style</label>
                    <Select value={citationStyle} onValueChange={setCitationStyle}>
                      <SelectTrigger>
                        <SelectValue />
                      </SelectTrigger>
                      <SelectContent>
                        <SelectItem value="harvard">Harvard</SelectItem>
                        <SelectItem value="apa">APA 7th</SelectItem>
                        <SelectItem value="mla">MLA 9th</SelectItem>
                        <SelectItem value="chicago">Chicago</SelectItem>
                        <SelectItem value="ieee">IEEE</SelectItem>
                      </SelectContent>
                    </Select>
                  </div>

                  <div>
                    <label className="text-sm font-medium mb-2 block">Academic Level</label>
                    <Select value={academicLevel} onValueChange={setAcademicLevel}>
                      <SelectTrigger>
                        <SelectValue />
                      </SelectTrigger>
                      <SelectContent>
                        <SelectItem value="doctoral">Doctoral/PhD</SelectItem>
                        <SelectItem value="masters">Master's</SelectItem>
                        <SelectItem value="undergraduate">Undergraduate</SelectItem>
                        <SelectItem value="professional">Professional</SelectItem>
                      </SelectContent>
                    </Select>
                  </div>
                </div>
              </CardContent>
            </Card>

            {/* Prompt Input */}
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center space-x-2">
                  <Brain className="w-6 h-6 text-blue-500" />
                  <span>Research Prompt</span>
                  <Badge variant="outline">Demo Ready</Badge>
                </CardTitle>
              </CardHeader>
              <CardContent className="space-y-4">
                <Textarea
                  value={prompt}
                  onChange={(e) => setPrompt(e.target.value)}
                  placeholder="Enter your dissertation prompt..."
                  className="min-h-[200px] text-sm"
                />
                
                <div className="flex items-center justify-between">
                  <div className="text-sm text-gray-500">
                    {prompt.length} characters • Complexity Score: 9.3/10.0
                  </div>
                  
                  <Button 
                    onClick={handleStartDissertation}
                    disabled={isProcessing || !prompt.trim()}
                    className="flex items-center space-x-2 bg-gradient-to-r from-blue-600 to-purple-600 hover:from-blue-700 hover:to-purple-700"
                    size="lg"
                  >
                    <Rocket className="w-5 h-5" />
                    <span>Generate Dissertation</span>
                    <ArrowRight className="w-5 h-5" />
                  </Button>
                </div>
              </CardContent>
            </Card>

            {/* Live Progress */}
            {isProcessing && (
              <Card>
                <CardHeader>
                  <CardTitle className="flex items-center justify-between">
                    <div className="flex items-center space-x-2">
                      <Timer className="w-6 h-6 text-green-500" />
                      <span>Live Processing Status</span>
                    </div>
                    <Badge variant="outline" className="animate-pulse">
                      Processing...
                    </Badge>
                  </CardTitle>
                </CardHeader>
                <CardContent className="space-y-4">
                  <div className="flex items-center justify-between text-sm">
                    <span>Overall Progress</span>
                    <span>{Math.round(overallProgress)}%</span>
                  </div>
                  <Progress value={overallProgress} className="h-3" />
                  
                  <div className="grid grid-cols-2 md:grid-cols-4 gap-4 text-sm">
                    <div>
                      <div className="text-gray-600">Phase</div>
                      <div className="font-semibold capitalize">{currentPhase.replace('_', ' ')}</div>
                    </div>
                    <div>
                      <div className="text-gray-600">Quality Score</div>
                      <div className="font-semibold">{liveMetrics.qualityScore.toFixed(1)}/10.0</div>
                    </div>
                    <div>
                      <div className="text-gray-600">Cost</div>
                      <div className="font-semibold">${liveMetrics.currentCost.toFixed(2)}</div>
                    </div>
                    <div>
                      <div className="text-gray-600">Time</div>
                      <div className="font-semibold">
                        {startTime ? formatTime((Date.now() - startTime.getTime()) / 1000) : '0m 0s'}
                      </div>
                    </div>
                  </div>

                  <div className="flex justify-center space-x-2">
                    <Button 
                      variant="outline" 
                      size="sm"
                      onClick={isPaused ? handleResume : handlePause}
                    >
                      {isPaused ? <Play className="w-4 h-4" /> : <Pause className="w-4 h-4" />}
                      <span className="ml-2">{isPaused ? 'Resume' : 'Pause'}</span>
                    </Button>
                    <Button variant="outline" size="sm" onClick={handleStop}>
                      <RotateCcw className="w-4 h-4" />
                      <span className="ml-2">Stop</span>
                    </Button>
                  </div>
                </CardContent>
              </Card>
            )}

            {/* Achievement Tracking */}
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center space-x-2">
                  <Award className="w-6 h-6 text-yellow-500" />
                  <span>Achievement Tracking</span>
                </CardTitle>
              </CardHeader>
              <CardContent>
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  {achievements.map((achievement) => (
                    <div 
                      key={achievement.id}
                      className={`p-4 rounded-lg border-2 transition-all ${
                        achievement.achieved 
                          ? 'border-green-500 bg-green-50' 
                          : 'border-gray-200 bg-gray-50'
                      }`}
                    >
                      <div className="flex items-center justify-between mb-2">
                        <div className="flex items-center space-x-2">
                          <div className={achievement.achieved ? 'text-green-600' : 'text-gray-400'}>
                            {getAchievementIcon(achievement.icon)}
                          </div>
                          <span className="font-semibold">{achievement.name}</span>
                        </div>
                        {achievement.achieved && <CheckCircle2 className="w-5 h-5 text-green-600" />}
                      </div>
                      <p className="text-sm text-gray-600 mb-2">{achievement.description}</p>
                      <div className="flex items-center justify-between text-sm">
                        <span>Progress:</span>
                        <span className="font-semibold">
                          {achievement.value}/{achievement.target}
                        </span>
                      </div>
                    </div>
                  ))}
                </div>
              </CardContent>
            </Card>
          </TabsContent>

          <TabsContent value="upload">
            <RevolutionaryFileUploader
              traceId={traceId}
              onFilesProcessed={handleFilesProcessed}
              onProcessingUpdate={handleProcessingUpdate}
              maxFiles={10}
              maxFileSize={500}
            />
          </TabsContent>

          <TabsContent value="orchestration">
            <AgentOrchestrationDashboard
              traceId={traceId}
              isActive={isProcessing}
              onPause={handlePause}
              onResume={handleResume}
              onStop={handleStop}
            />
          </TabsContent>

          <TabsContent value="results" className="space-y-6">
            {dissertationResult ? (
              <Card>
                <CardHeader>
                  <CardTitle className="flex items-center space-x-2">
                    <Trophy className="w-6 h-6 text-yellow-500" />
                    <span>Dissertation Complete</span>
                  </CardTitle>
                </CardHeader>
                <CardContent className="space-y-6">
                  <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                    <div className="text-center p-4 border rounded-lg">
                      <div className="text-2xl font-bold text-green-600">
                        {dissertationResult.qualityScore.toFixed(1)}
                      </div>
                      <div className="text-sm text-gray-600">Quality Score</div>
                    </div>
                    <div className="text-center p-4 border rounded-lg">
                      <div className="text-2xl font-bold text-blue-600">
                        {dissertationResult.originalityScore.toFixed(1)}%
                      </div>
                      <div className="text-sm text-gray-600">Originality</div>
                    </div>
                    <div className="text-center p-4 border rounded-lg">
                      <div className="text-2xl font-bold text-purple-600">
                        {dissertationResult.citationCount}
                      </div>
                      <div className="text-sm text-gray-600">Citations</div>
                    </div>
                    <div className="text-center p-4 border rounded-lg">
                      <div className="text-2xl font-bold text-yellow-600">
                        {formatTime(dissertationResult.processingTime * 60)}
                      </div>
                      <div className="text-sm text-gray-600">Time</div>
                    </div>
                  </div>

                  <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                    {Object.entries(dissertationResult.downloadUrls).map(([format, url]) => (
                      <Button key={format} variant="outline" className="flex items-center space-x-2">
                        <Download className="w-4 h-4" />
                        <span>{format.toUpperCase()}</span>
                      </Button>
                    ))}
                  </div>
                </CardContent>
              </Card>
            ) : (
              <Card>
                <CardContent className="py-12 text-center">
                  <FileText className="w-16 h-16 mx-auto mb-4 text-gray-400" />
                  <p className="text-lg text-gray-600">No results yet</p>
                  <p className="text-sm text-gray-500">Start processing to see your dissertation results</p>
                </CardContent>
              </Card>
            )}
          </TabsContent>
        </Tabs>
      </div>
    </div>
  );
};