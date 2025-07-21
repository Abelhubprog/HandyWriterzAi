import React, { useState, useEffect } from 'react';
import {
  Box,
  Typography,
  Card,
  CardContent,
  Button,
  Select,
  MenuItem,
  FormControl,
  InputLabel,
  Alert,
  Chip,
  Grid,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  TextField,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Paper,
  IconButton,
  Tooltip,
  LinearProgress,
  Switch,
  FormControlLabel,
  Accordion,
  AccordionSummary,
  AccordionDetails,
  Snackbar
} from '@mui/material';
import {
  Edit as EditIcon,
  Refresh as RefreshIcon,
  Save as SaveIcon,
  Cancel as CancelIcon,
  TrendingUp as MetricsIcon,
  Settings as SettingsIcon,
  CloudSync as CloudSyncIcon,
  ExpandMore as ExpandMoreIcon,
  Info as InfoIcon,
  Warning as WarningIcon,
  CheckCircle as CheckCircleIcon
} from '@mui/icons-material';

interface AgentConfig {
  name: string;
  display_name: string;
  description: string;
  current_model: string;
  fallback_models: string[];
  temperature: number;
  max_tokens: number;
}

interface ModelMetrics {
  total_requests: number;
  total_tokens: number;
  total_cost: number;
  avg_response_time: number;
  error_count: number;
  last_used: string | null;
}

interface Provider {
  [key: string]: string[];
}

interface SwarmConfig {
  name: string;
  description: string;
  agents: Record<string, { model: string; weight: number }>;
  consensus_threshold: number;
  diversity_target: number;
}

export const ModelConfigPanel: React.FC = () => {
  const [agents, setAgents] = useState<AgentConfig[]>([]);
  const [providers, setProviders] = useState<Provider>({});
  const [metrics, setMetrics] = useState<Record<string, ModelMetrics>>({});
  const [swarms, setSwarms] = useState<Record<string, SwarmConfig>>({});
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState<string | null>(null);
  
  // Edit dialog state
  const [editDialogOpen, setEditDialogOpen] = useState(false);
  const [editingAgent, setEditingAgent] = useState<AgentConfig | null>(null);
  const [newModel, setNewModel] = useState('');
  const [updateReason, setUpdateReason] = useState('');
  
  // Bulk update state
  const [bulkUpdateMode, setBulkUpdateMode] = useState(false);
  const [selectedUpdates, setSelectedUpdates] = useState<Record<string, string>>({});
  
  // Configuration summary
  const [configSummary, setConfigSummary] = useState<any>(null);

  // Fetch data on component mount
  useEffect(() => {
    loadAllData();
  }, []);

  const loadAllData = async () => {
    setLoading(true);
    try {
      await Promise.all([
        loadAgents(),
        loadProviders(),
        loadMetrics(),
        loadSwarms(),
        loadConfigSummary()
      ]);
    } catch (err) {
      setError('Failed to load configuration data');
      console.error('Load error:', err);
    } finally {
      setLoading(false);
    }
  };

  const loadAgents = async () => {
    const response = await fetch('/api/admin/models/agents', {
      headers: { 'Authorization': `Bearer ${localStorage.getItem('auth_token')}` }
    });
    
    if (!response.ok) throw new Error('Failed to load agents');
    
    const data = await response.json();
    setAgents(data.data.agents);
  };

  const loadProviders = async () => {
    const response = await fetch('/api/admin/models/providers', {
      headers: { 'Authorization': `Bearer ${localStorage.getItem('auth_token')}` }
    });
    
    if (!response.ok) throw new Error('Failed to load providers');
    
    const data = await response.json();
    setProviders(data.data.providers);
  };

  const loadMetrics = async () => {
    const response = await fetch('/api/admin/models/metrics', {
      headers: { 'Authorization': `Bearer ${localStorage.getItem('auth_token')}` }
    });
    
    if (!response.ok) throw new Error('Failed to load metrics');
    
    const data = await response.json();
    setMetrics(data.data.metrics);
  };

  const loadSwarms = async () => {
    const response = await fetch('/api/admin/models/swarms', {
      headers: { 'Authorization': `Bearer ${localStorage.getItem('auth_token')}` }
    });
    
    if (!response.ok) throw new Error('Failed to load swarms');
    
    const data = await response.json();
    setSwarms(data.data.swarms);
  };

  const loadConfigSummary = async () => {
    const response = await fetch('/api/admin/models/config/summary', {
      headers: { 'Authorization': `Bearer ${localStorage.getItem('auth_token')}` }
    });
    
    if (!response.ok) throw new Error('Failed to load config summary');
    
    const data = await response.json();
    setConfigSummary(data.data);
  };

  const handleEditAgent = (agent: AgentConfig) => {
    setEditingAgent(agent);
    setNewModel(agent.current_model);
    setUpdateReason('');
    setEditDialogOpen(true);
  };

  const handleUpdateModel = async () => {
    if (!editingAgent || !newModel) return;

    setLoading(true);
    try {
      const response = await fetch(`/api/admin/models/agents/${editingAgent.name}/model`, {
        method: 'PUT',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${localStorage.getItem('auth_token')}`
        },
        body: JSON.stringify({
          agent_name: editingAgent.name,
          new_model: newModel,
          reason: updateReason
        })
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || 'Failed to update model');
      }

      const data = await response.json();
      setSuccess(`Successfully updated ${editingAgent.display_name} to use ${newModel}`);
      setEditDialogOpen(false);
      await loadAgents(); // Reload agents
      
    } catch (err: any) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  const handleBulkUpdate = async () => {
    const updates = Object.entries(selectedUpdates)
      .filter(([_, model]) => model)
      .map(([agent_name, new_model]) => ({ agent_name, new_model }));

    if (updates.length === 0) {
      setError('No updates selected');
      return;
    }

    setLoading(true);
    try {
      const response = await fetch('/api/admin/models/agents/bulk-update', {
        method: 'PUT',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${localStorage.getItem('auth_token')}`
        },
        body: JSON.stringify({
          updates,
          reason: updateReason
        })
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || 'Bulk update failed');
      }

      const data = await response.json();
      setSuccess(`Bulk update completed: ${data.data.successful_count} successful, ${data.data.error_count} errors`);
      setBulkUpdateMode(false);
      setSelectedUpdates({});
      await loadAgents();
      
    } catch (err: any) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  const handleReloadConfig = async () => {
    setLoading(true);
    try {
      const response = await fetch('/api/admin/models/reload', {
        method: 'POST',
        headers: { 'Authorization': `Bearer ${localStorage.getItem('auth_token')}` }
      });

      if (!response.ok) throw new Error('Failed to reload configuration');

      const data = await response.json();
      setSuccess(data.message);
      await loadAllData();
      
    } catch (err: any) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  const getProviderColor = (model: string): string => {
    if (model.includes('claude')) return '#FF6B35';
    if (model.includes('gpt') || model.includes('o1') || model.includes('o3')) return '#10A37F';
    if (model.includes('gemini')) return '#4285F4';
    if (model.includes('grok')) return '#1DA1F2';
    if (model.includes('qwen')) return '#FF6600';
    if (model.includes('deepseek')) return '#8B5CF6';
    if (model.includes('sonar') || model.includes('llama')) return '#FF4081';
    return '#757575';
  };

  const formatMetric = (value: number, type: 'cost' | 'time' | 'count'): string => {
    switch (type) {
      case 'cost':
        return `$${value.toFixed(4)}`;
      case 'time':
        return `${value.toFixed(2)}s`;
      case 'count':
        return value.toLocaleString();
      default:
        return value.toString();
    }
  };

  return (
    <Box sx={{ p: 3 }}>
      <Typography variant="h4" gutterBottom>
        🔧 Pluggable-Model Control Panel
      </Typography>
      
      <Typography variant="subtitle1" color="text.secondary" gutterBottom>
        Dynamically configure AI models for HandyWriterz agents without redeploying
      </Typography>

      {/* Configuration Summary */}
      {configSummary && (
        <Card sx={{ mb: 3 }}>
          <CardContent>
            <Grid container spacing={2} alignItems="center">
              <Grid item xs={12} md={8}>
                <Typography variant="h6">Configuration Status</Typography>
                <Typography variant="body2" color="text.secondary">
                  Version: {configSummary.version} | 
                  Last Updated: {configSummary.last_updated ? new Date(configSummary.last_updated).toLocaleString() : 'Unknown'} |
                  Agents: {configSummary.total_agents} | 
                  Providers: {configSummary.total_providers}
                </Typography>
              </Grid>
              <Grid item xs={12} md={4} sx={{ textAlign: 'right' }}>
                <Button
                  variant="outlined"
                  startIcon={<RefreshIcon />}
                  onClick={handleReloadConfig}
                  disabled={loading}
                  sx={{ mr: 1 }}
                >
                  Reload Config
                </Button>
                <FormControlLabel
                  control={
                    <Switch
                      checked={bulkUpdateMode}
                      onChange={(e) => setBulkUpdateMode(e.target.checked)}
                    />
                  }
                  label="Bulk Update"
                />
              </Grid>
            </Grid>
          </CardContent>
        </Card>
      )}

      {/* Loading Indicator */}
      {loading && <LinearProgress sx={{ mb: 2 }} />}

      {/* Agent Configuration Table */}
      <Card sx={{ mb: 3 }}>
        <CardContent>
          <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 2 }}>
            <Typography variant="h6">Agent Model Configuration</Typography>
            {bulkUpdateMode && (
              <Box>
                <Button
                  variant="contained"
                  color="primary"
                  startIcon={<SaveIcon />}
                  onClick={handleBulkUpdate}
                  disabled={loading || Object.keys(selectedUpdates).length === 0}
                  sx={{ mr: 1 }}
                >
                  Apply Bulk Updates
                </Button>
                <Button
                  variant="outlined"
                  startIcon={<CancelIcon />}
                  onClick={() => {
                    setBulkUpdateMode(false);
                    setSelectedUpdates({});
                  }}
                >
                  Cancel
                </Button>
              </Box>
            )}
          </Box>

          <TableContainer component={Paper} variant="outlined">
            <Table>
              <TableHead>
                <TableRow>
                  <TableCell>Agent</TableCell>
                  <TableCell>Current Model</TableCell>
                  <TableCell>Fallback Models</TableCell>
                  <TableCell>Performance</TableCell>
                  <TableCell>Actions</TableCell>
                </TableRow>
              </TableHead>
              <TableBody>
                {agents.map((agent) => {
                  const agentMetrics = metrics[agent.name];
                  
                  return (
                    <TableRow key={agent.name}>
                      <TableCell>
                        <Box>
                          <Typography variant="subtitle2">{agent.display_name}</Typography>
                          <Typography variant="caption" color="text.secondary">
                            {agent.description}
                          </Typography>
                        </Box>
                      </TableCell>
                      
                      <TableCell>
                        {bulkUpdateMode ? (
                          <FormControl size="small" sx={{ minWidth: 200 }}>
                            <Select
                              value={selectedUpdates[agent.name] || agent.current_model}
                              onChange={(e) =>
                                setSelectedUpdates(prev => ({
                                  ...prev,
                                  [agent.name]: e.target.value
                                }))
                              }
                            >
                              {Object.entries(providers).map(([provider, models]) =>
                                models.map((model) => (
                                  <MenuItem key={model} value={model}>
                                    <Chip
                                      label={model}
                                      size="small"
                                      sx={{
                                        backgroundColor: getProviderColor(model),
                                        color: 'white',
                                        fontSize: '0.75rem'
                                      }}
                                    />
                                  </MenuItem>
                                ))
                              )}
                            </Select>
                          </FormControl>
                        ) : (
                          <Chip
                            label={agent.current_model}
                            size="small"
                            sx={{
                              backgroundColor: getProviderColor(agent.current_model),
                              color: 'white'
                            }}
                          />
                        )}
                      </TableCell>
                      
                      <TableCell>
                        <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 0.5 }}>
                          {agent.fallback_models.slice(0, 2).map((model) => (
                            <Chip
                              key={model}
                              label={model}
                              size="small"
                              variant="outlined"
                              sx={{ fontSize: '0.7rem' }}
                            />
                          ))}
                          {agent.fallback_models.length > 2 && (
                            <Tooltip title={agent.fallback_models.slice(2).join(', ')}>
                              <Chip
                                label={`+${agent.fallback_models.length - 2}`}
                                size="small"
                                variant="outlined"
                              />
                            </Tooltip>
                          )}
                        </Box>
                      </TableCell>
                      
                      <TableCell>
                        {agentMetrics ? (
                          <Box>
                            <Typography variant="caption" display="block">
                              Requests: {formatMetric(agentMetrics.total_requests, 'count')}
                            </Typography>
                            <Typography variant="caption" display="block">
                              Avg Time: {formatMetric(agentMetrics.avg_response_time, 'time')}
                            </Typography>
                            <Typography variant="caption" display="block">
                              Cost: {formatMetric(agentMetrics.total_cost, 'cost')}
                            </Typography>
                          </Box>
                        ) : (
                          <Typography variant="caption" color="text.secondary">
                            No data
                          </Typography>
                        )}
                      </TableCell>
                      
                      <TableCell>
                        {!bulkUpdateMode && (
                          <IconButton
                            size="small"
                            onClick={() => handleEditAgent(agent)}
                            disabled={loading}
                          >
                            <EditIcon />
                          </IconButton>
                        )}
                      </TableCell>
                    </TableRow>
                  );
                })}
              </TableBody>
            </Table>
          </TableContainer>
        </CardContent>
      </Card>

      {/* Swarm Intelligence Configuration */}
      <Card sx={{ mb: 3 }}>
        <CardContent>
          <Typography variant="h6" gutterBottom>
            Swarm Intelligence Configuration
          </Typography>
          
          {Object.entries(swarms).map(([swarmName, swarmConfig]) => (
            <Accordion key={swarmName}>
              <AccordionSummary expandIcon={<ExpandMoreIcon />}>
                <Typography variant="subtitle1">
                  {swarmConfig.name}
                </Typography>
                <Typography variant="caption" sx={{ ml: 2, color: 'text.secondary' }}>
                  {Object.keys(swarmConfig.agents).length} agents
                </Typography>
              </AccordionSummary>
              <AccordionDetails>
                <Typography variant="body2" color="text.secondary" paragraph>
                  {swarmConfig.description}
                </Typography>
                
                <Grid container spacing={2}>
                  <Grid item xs={12} md={8}>
                    <TableContainer component={Paper} variant="outlined" size="small">
                      <Table>
                        <TableHead>
                          <TableRow>
                            <TableCell>Agent Role</TableCell>
                            <TableCell>Model</TableCell>
                            <TableCell>Weight</TableCell>
                          </TableRow>
                        </TableHead>
                        <TableBody>
                          {Object.entries(swarmConfig.agents).map(([role, config]) => (
                            <TableRow key={role}>
                              <TableCell>{role.replace(/_/g, ' ')}</TableCell>
                              <TableCell>
                                <Chip
                                  label={config.model}
                                  size="small"
                                  sx={{
                                    backgroundColor: getProviderColor(config.model),
                                    color: 'white'
                                  }}
                                />
                              </TableCell>
                              <TableCell>{(config.weight * 100).toFixed(0)}%</TableCell>
                            </TableRow>
                          ))}
                        </TableBody>
                      </Table>
                    </TableContainer>
                  </Grid>
                  
                  <Grid item xs={12} md={4}>
                    <Box sx={{ p: 2, backgroundColor: 'grey.50', borderRadius: 1 }}>
                      <Typography variant="subtitle2" gutterBottom>
                        Swarm Parameters
                      </Typography>
                      <Typography variant="body2">
                        Consensus Threshold: {(swarmConfig.consensus_threshold * 100).toFixed(0)}%
                      </Typography>
                      <Typography variant="body2">
                        Diversity Target: {(swarmConfig.diversity_target * 100).toFixed(0)}%
                      </Typography>
                    </Box>
                  </Grid>
                </Grid>
              </AccordionDetails>
            </Accordion>
          ))}
        </CardContent>
      </Card>

      {/* Model Provider Overview */}
      <Card>
        <CardContent>
          <Typography variant="h6" gutterBottom>
            Available Model Providers
          </Typography>
          
          <Grid container spacing={2}>
            {Object.entries(providers).map(([provider, models]) => (
              <Grid item xs={12} md={6} lg={4} key={provider}>
                <Card variant="outlined">
                  <CardContent>
                    <Typography variant="subtitle1" gutterBottom>
                      {provider.charAt(0).toUpperCase() + provider.slice(1)}
                    </Typography>
                    <Typography variant="caption" color="text.secondary">
                      {models.length} models available
                    </Typography>
                    <Box sx={{ mt: 1 }}>
                      {models.slice(0, 3).map((model) => (
                        <Chip
                          key={model}
                          label={model}
                          size="small"
                          sx={{
                            m: 0.25,
                            fontSize: '0.7rem',
                            backgroundColor: getProviderColor(model),
                            color: 'white'
                          }}
                        />
                      ))}
                      {models.length > 3 && (
                        <Tooltip title={models.slice(3).join(', ')}>
                          <Chip
                            label={`+${models.length - 3} more`}
                            size="small"
                            sx={{ m: 0.25, fontSize: '0.7rem' }}
                          />
                        </Tooltip>
                      )}
                    </Box>
                  </CardContent>
                </Card>
              </Grid>
            ))}
          </Grid>
        </CardContent>
      </Card>

      {/* Edit Dialog */}
      <Dialog open={editDialogOpen} onClose={() => setEditDialogOpen(false)} maxWidth="md" fullWidth>
        <DialogTitle>
          Edit Model for {editingAgent?.display_name}
        </DialogTitle>
        <DialogContent>
          <Typography variant="body2" color="text.secondary" paragraph>
            {editingAgent?.description}
          </Typography>
          
          <FormControl fullWidth sx={{ mb: 2 }}>
            <InputLabel>Select Model</InputLabel>
            <Select
              value={newModel}
              onChange={(e) => setNewModel(e.target.value)}
              label="Select Model"
            >
              {Object.entries(providers).map(([provider, models]) =>
                models.map((model) => (
                  <MenuItem key={model} value={model}>
                    <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                      <Chip
                        label={provider}
                        size="small"
                        variant="outlined"
                        sx={{ fontSize: '0.7rem' }}
                      />
                      {model}
                    </Box>
                  </MenuItem>
                ))
              )}
            </Select>
          </FormControl>
          
          <TextField
            fullWidth
            label="Update Reason (Optional)"
            value={updateReason}
            onChange={(e) => setUpdateReason(e.target.value)}
            multiline
            rows={2}
            placeholder="Why are you changing this model?"
          />
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setEditDialogOpen(false)}>Cancel</Button>
          <Button
            onClick={handleUpdateModel}
            variant="contained"
            disabled={!newModel || loading}
          >
            Update Model
          </Button>
        </DialogActions>
      </Dialog>

      {/* Success/Error Snackbars */}
      <Snackbar
        open={!!success}
        autoHideDuration={6000}
        onClose={() => setSuccess(null)}
      >
        <Alert severity="success" onClose={() => setSuccess(null)}>
          {success}
        </Alert>
      </Snackbar>

      <Snackbar
        open={!!error}
        autoHideDuration={6000}
        onClose={() => setError(null)}
      >
        <Alert severity="error" onClose={() => setError(null)}>
          {error}
        </Alert>
      </Snackbar>
    </Box>
  );
};