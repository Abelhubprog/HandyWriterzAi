'use client';

import React, { useState, useEffect } from 'react';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Badge } from '@/components/ui/badge';
import { useToast } from '@/components/ui/use-toast';
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from '@/components/ui/table';
import { Progress } from '@/components/ui/progress';
import { 
  Settings, 
  RefreshCw, 
  Save, 
  X, 
  TrendingUp, 
  Cloud, 
  Info, 
  AlertTriangle, 
  CheckCircle2 
} from 'lucide-react';

interface ModelConfig {
  id: string;
  name: string;
  provider: string;
  status: 'active' | 'inactive' | 'maintenance';
  latency: number;
  cost_per_token: number;
  max_tokens: number;
  enabled: boolean;
}

interface ModelMetrics {
  requests_per_hour: number;
  success_rate: number;
  avg_response_time: number;
  cost_today: number;
}

export const ModelConfigPanel: React.FC = () => {
  const [models, setModels] = useState<ModelConfig[]>([]);
  const [metrics, setMetrics] = useState<Record<string, ModelMetrics>>({});
  const [loading, setLoading] = useState(true);
  const [editingModel, setEditingModel] = useState<string | null>(null);
  const [selectedProvider, setSelectedProvider] = useState<string>('all');
  const { toast } = useToast();

  const providers = ['OpenAI', 'Anthropic', 'Google', 'Cohere', 'Meta'];
  const statuses = ['active', 'inactive', 'maintenance'] as const;

  useEffect(() => {
    loadModels();
    loadMetrics();
  }, []);

  const loadModels = async () => {
    try {
      setLoading(true);
      // Mock data - replace with actual API call
      const mockModels: ModelConfig[] = [
        {
          id: 'gpt-4',
          name: 'GPT-4',
          provider: 'OpenAI',
          status: 'active',
          latency: 2.5,
          cost_per_token: 0.00003,
          max_tokens: 8192,
          enabled: true
        },
        {
          id: 'claude-3',
          name: 'Claude 3 Sonnet',
          provider: 'Anthropic',
          status: 'active',
          latency: 1.8,
          cost_per_token: 0.000015,
          max_tokens: 4096,
          enabled: true
        }
      ];
      setModels(mockModels);
    } catch (error) {
      toast({
        title: "Error",
        description: "Failed to load models",
        variant: "destructive",
      });
    } finally {
      setLoading(false);
    }
  };

  const loadMetrics = async () => {
    try {
      // Mock metrics - replace with actual API call
      const mockMetrics: Record<string, ModelMetrics> = {
        'gpt-4': {
          requests_per_hour: 150,
          success_rate: 99.2,
          avg_response_time: 2.5,
          cost_today: 12.45
        },
        'claude-3': {
          requests_per_hour: 89,
          success_rate: 99.8,
          avg_response_time: 1.8,
          cost_today: 8.32
        }
      };
      setMetrics(mockMetrics);
    } catch (error) {
      console.error('Failed to load metrics:', error);
    }
  };

  const handleSaveModel = async (modelId: string) => {
    try {
      // Save model configuration - replace with actual API call
      toast({
        title: "Success",
        description: "Model configuration saved successfully",
      });
      setEditingModel(null);
    } catch (error) {
      toast({
        title: "Error",
        description: "Failed to save model configuration",
        variant: "destructive",
      });
    }
  };

  const handleToggleModel = async (modelId: string, enabled: boolean) => {
    try {
      setModels(prev => prev.map(model => 
        model.id === modelId ? { ...model, enabled } : model
      ));
      toast({
        title: "Success",
        description: `Model ${enabled ? 'enabled' : 'disabled'} successfully`,
      });
    } catch (error) {
      toast({
        title: "Error",
        description: "Failed to update model status",
        variant: "destructive",
      });
    }
  };

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'active':
        return <CheckCircle2 className="h-4 w-4 text-green-500" />;
      case 'maintenance':
        return <AlertTriangle className="h-4 w-4 text-yellow-500" />;
      default:
        return <X className="h-4 w-4 text-red-500" />;
    }
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'active':
        return 'bg-green-100 text-green-800';
      case 'maintenance':
        return 'bg-yellow-100 text-yellow-800';
      default:
        return 'bg-red-100 text-red-800';
    }
  };

  const filteredModels = selectedProvider === 'all' 
    ? models 
    : models.filter(model => model.provider === selectedProvider);

  if (loading) {
    return (
      <div className="p-6">
        <div className="flex items-center gap-2 mb-4">
          <RefreshCw className="h-5 w-5 animate-spin" />
          <span>Loading model configurations...</span>
        </div>
        <Progress value={45} className="w-full" />
      </div>
    );
  }

  return (
    <div className="p-6 space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-2">
          <Settings className="h-6 w-6" />
          <h1 className="text-2xl font-bold">Model Configuration</h1>
        </div>
        <div className="flex items-center gap-2">
          <Button onClick={loadModels} variant="outline" size="sm">
            <RefreshCw className="h-4 w-4 mr-2" />
            Refresh
          </Button>
          <Select value={selectedProvider} onValueChange={setSelectedProvider}>
            <SelectTrigger className="w-40">
              <SelectValue placeholder="Filter by provider" />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="all">All Providers</SelectItem>
              {providers.map(provider => (
                <SelectItem key={provider} value={provider}>{provider}</SelectItem>
              ))}
            </SelectContent>
          </Select>
        </div>
      </div>


      {/* Models Table */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Cloud className="h-5 w-5" />
            Available Models
          </CardTitle>
        </CardHeader>
        <CardContent>
          <Table>
            <TableHeader>
              <TableRow>
                <TableHead>Model</TableHead>
                <TableHead>Provider</TableHead>
                <TableHead>Status</TableHead>
                <TableHead>Latency</TableHead>
                <TableHead>Cost/Token</TableHead>
                <TableHead>Max Tokens</TableHead>
                <TableHead>Enabled</TableHead>
                <TableHead>Actions</TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {filteredModels.map((model) => (
                <TableRow key={model.id}>
                  <TableCell className="font-medium">{model.name}</TableCell>
                  <TableCell>
                    <Badge variant="outline">{model.provider}</Badge>
                  </TableCell>
                  <TableCell>
                    <div className="flex items-center gap-2">
                      {getStatusIcon(model.status)}
                      <Badge className={getStatusColor(model.status)}>
                        {model.status}
                      </Badge>
                    </div>
                  </TableCell>
                  <TableCell>{model.latency}s</TableCell>
                  <TableCell>${model.cost_per_token}</TableCell>
                  <TableCell>{model.max_tokens.toLocaleString()}</TableCell>
                  <TableCell>
                    <Button
                      variant={model.enabled ? "default" : "outline"}
                      size="sm"
                      onClick={() => handleToggleModel(model.id, !model.enabled)}
                    >
                      {model.enabled ? "Enabled" : "Disabled"}
                    </Button>
                  </TableCell>
                  <TableCell>
                    <div className="flex items-center gap-2">
                      <Button
                        variant="outline"
                        size="sm"
                        onClick={() => setEditingModel(model.id)}
                      >
                        <Settings className="h-4 w-4" />
                      </Button>
                      <Button
                        variant="outline"
                        size="sm"
                      >
                        <TrendingUp className="h-4 w-4" />
                      </Button>
                    </div>
                  </TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
        </CardContent>
      </Card>

      {/* Metrics Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        {filteredModels.map((model) => {
          const modelMetrics = metrics[model.id];
          if (!modelMetrics) return null;

          return (
            <Card key={`metrics-${model.id}`}>
              <CardHeader className="pb-2">
                <CardTitle className="text-sm font-medium">{model.name} Metrics</CardTitle>
              </CardHeader>
              <CardContent className="space-y-2">
                <div className="flex justify-between text-sm">
                  <span>Requests/hr:</span>
                  <span className="font-medium">{modelMetrics.requests_per_hour}</span>
                </div>
                <div className="flex justify-between text-sm">
                  <span>Success Rate:</span>
                  <span className="font-medium">{modelMetrics.success_rate}%</span>
                </div>
                <div className="flex justify-between text-sm">
                  <span>Avg Response:</span>
                  <span className="font-medium">{modelMetrics.avg_response_time}s</span>
                </div>
                <div className="flex justify-between text-sm">
                  <span>Cost Today:</span>
                  <span className="font-medium">${modelMetrics.cost_today}</span>
                </div>
              </CardContent>
            </Card>
          );
        })}
      </div>
    </div>
  );
};