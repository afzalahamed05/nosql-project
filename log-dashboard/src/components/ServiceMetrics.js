import React from 'react';
import {
  Box,
  Grid,
  Paper,
  Typography,
  LinearProgress,
  Chip,
  Divider,
  Tooltip,
} from '@mui/material';
import SpeedIcon from '@mui/icons-material/Speed';
import TrendingUpIcon from '@mui/icons-material/TrendingUp';
import TrendingDownIcon from '@mui/icons-material/TrendingDown';
import ErrorOutlineIcon from '@mui/icons-material/ErrorOutline';
import { useAnomaly } from '../contexts/AnomalyContext';

const ServiceMetrics = () => {
  const { serviceDetails, loading } = useAnomaly();
  
  if (loading.serviceDetails) {
    return (
      <Paper sx={{ p: 3, mb: 3 }}>
        <LinearProgress />
        <Typography variant="body2" sx={{ mt: 2, textAlign: 'center' }}>
          Loading service metrics...
        </Typography>
      </Paper>
    );
  }
  
  if (!serviceDetails) {
    return (
      <Paper sx={{ p: 3, mb: 3, textAlign: 'center' }}>
        <Typography variant="body1" color="text.secondary">
          Select a service to view detailed metrics
        </Typography>
      </Paper>
    );
  }
  
  const {
    service_name,
    total_logs,
    total_anomalies,
    anomaly_rate,
    logs_last_hour,
    anomalies_last_hour,
    avg_response_time_ms,
    p95_response_time_ms,
    error_rate,
    window_stats,
    detection_methods,
  } = serviceDetails;
  
  // Calculate trends (simplified - in production would compare with previous period)
  const logsTrend = logs_last_hour > (total_logs / 24) ? 'up' : 'down';
  const anomaliesTrend = anomalies_last_hour > (total_anomalies / 24) ? 'up' : 'down';
  
  // Determine status colors
  const getResponseTimeColor = (time) => {
    if (time < 500) return 'success';
    if (time < 1000) return 'warning';
    return 'error';
  };
  
  const getErrorRateColor = (rate) => {
    if (rate < 0.01) return 'success';
    if (rate < 0.05) return 'warning';
    return 'error';
  };
  
  const getAnomalyRateColor = (rate) => {
    if (rate < 0.01) return 'success';
    if (rate < 0.03) return 'warning';
    return 'error';
  };
  
  return (
    <Paper sx={{ p: 3, mb: 3 }}>
      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 2 }}>
        <Typography variant="h5">
          {service_name}
        </Typography>
        <Chip 
          label="Active" 
          color="success" 
          variant="outlined"
          size="small"
        />
      </Box>
      
      <Divider sx={{ mb: 3 }} />
      
      <Grid container spacing={3}>
        {/* Performance Metrics */}
        <Grid item xs={12} md={6}>
          <Typography variant="subtitle1" gutterBottom color="primary">
            Performance Metrics
          </Typography>
          
          <Grid container spacing={2}>
            {/* Average Response Time */}
            <Grid item xs={6}>
              <Paper sx={{ p: 2, textAlign: 'center' }}>
                <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'center', mb: 1 }}>
                  <SpeedIcon fontSize="small" sx={{ mr: 1 }} />
                  <Typography variant="body2" color="text.secondary">
                    Avg Response Time
                  </Typography>
                </Box>
                <Tooltip title={`${avg_response_time_ms.toFixed(1)} ms`}>
                  <Typography variant="h5" color={getResponseTimeColor(avg_response_time_ms)}>
                    {avg_response_time_ms.toFixed(0)} ms
                  </Typography>
                </Tooltip>
              </Paper>
            </Grid>
            
            {/* P95 Response Time */}
            <Grid item xs={6}>
              <Paper sx={{ p: 2, textAlign: 'center' }}>
                <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'center', mb: 1 }}>
                  <TrendingUpIcon fontSize="small" sx={{ mr: 1 }} />
                  <Typography variant="body2" color="text.secondary">
                    P95 Response Time
                  </Typography>
                </Box>
                <Tooltip title={`${p95_response_time_ms.toFixed(1)} ms`}>
                  <Typography variant="h5" color={getResponseTimeColor(p95_response_time_ms)}>
                    {p95_response_time_ms.toFixed(0)} ms
                  </Typography>
                </Tooltip>
              </Paper>
            </Grid>
            
            {/* Error Rate */}
            <Grid item xs={6}>
              <Paper sx={{ p: 2, textAlign: 'center' }}>
                <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'center', mb: 1 }}>
                  <ErrorOutlineIcon fontSize="small" sx={{ mr: 1 }} />
                  <Typography variant="body2" color="text.secondary">
                    Error Rate
                  </Typography>
                </Box>
                <Typography variant="h5" color={getErrorRateColor(error_rate)}>
                  {(error_rate * 100).toFixed(1)}%
                </Typography>
              </Paper>
            </Grid>
            
            {/* Window Request Count */}
            <Grid item xs={6}>
              <Paper sx={{ p: 2, textAlign: 'center' }}>
                <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'center', mb: 1 }}>
                  <Typography variant="body2" color="text.secondary">
                    Avg Requests/Window
                  </Typography>
                </Box>
                <Typography variant="h5">
                  {window_stats?.avg_request_count?.toFixed(0) || '0'}
                </Typography>
              </Paper>
            </Grid>
          </Grid>
        </Grid>
        
        {/* Anomaly Metrics */}
        <Grid item xs={12} md={6}>
          <Typography variant="subtitle1" gutterBottom color="primary">
            Anomaly Detection
          </Typography>
          
          <Grid container spacing={2}>
            {/* Total Anomalies */}
            <Grid item xs={6}>
              <Paper sx={{ p: 2, textAlign: 'center' }}>
                <Typography variant="body2" color="text.secondary" gutterBottom>
                  Total Anomalies
                </Typography>
                <Typography variant="h4">
                  {total_anomalies.toLocaleString()}
                </Typography>
                <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'center', mt: 1 }}>
                  {anomaliesTrend === 'up' ? (
                    <TrendingUpIcon fontSize="small" color="error" />
                  ) : (
                    <TrendingDownIcon fontSize="small" color="success" />
                  )}
                  <Typography variant="caption" color="text.secondary" sx={{ ml: 0.5 }}>
                    {anomalies_last_hour} last hour
                  </Typography>
                </Box>
              </Paper>
            </Grid>
            
            {/* Anomaly Rate */}
            <Grid item xs={6}>
              <Paper sx={{ p: 2, textAlign: 'center' }}>
                <Typography variant="body2" color="text.secondary" gutterBottom>
                  Anomaly Rate
                </Typography>
                <Typography variant="h4" color={getAnomalyRateColor(anomaly_rate)}>
                  {(anomaly_rate * 100).toFixed(1)}%
                </Typography>
                <Typography variant="caption" color="text.secondary">
                  of all logs
                </Typography>
              </Paper>
            </Grid>
            
            {/* Detection Method Breakdown */}
            <Grid item xs={12}>
              <Paper sx={{ p: 2 }}>
                <Typography variant="body2" color="text.secondary" gutterBottom>
                  Detection Method Breakdown
                </Typography>
                <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 1 }}>
                  {Object.entries(detection_methods || {}).map(([method, count]) => (
                    <Chip
                      key={method}
                      label={`${method}: ${count}`}
                      size="small"
                      color={
                        method.includes('rule') ? 'primary' :
                        method.includes('model') ? 'secondary' :
                        method.includes('hybrid') ? 'success' : 'default'
                      }
                      variant="outlined"
                    />
                  ))}
                  {(!detection_methods || Object.keys(detection_methods).length === 0) && (
                    <Typography variant="caption" color="text.secondary">
                      No anomalies detected yet
                    </Typography>
                  )}
                </Box>
              </Paper>
            </Grid>
            
            {/* Window Statistics */}
            <Grid item xs={12}>
              <Paper sx={{ p: 2 }}>
                <Typography variant="body2" color="text.secondary" gutterBottom>
                  Window Statistics
                </Typography>
                <Grid container spacing={1}>
                  <Grid item xs={6}>
                    <Typography variant="caption" color="text.secondary">
                      Total Windows:
                    </Typography>
                    <Typography variant="body2">
                      {window_stats?.total_windows?.toLocaleString() || '0'}
                    </Typography>
                  </Grid>
                  <Grid item xs={6}>
                    <Typography variant="caption" color="text.secondary">
                      Avg Error Rate:
                    </Typography>
                    <Typography variant="body2">
                      {window_stats?.avg_error_rate ? `${(window_stats.avg_error_rate * 100).toFixed(1)}%` : '0%'}
                    </Typography>
                  </Grid>
                </Grid>
              </Paper>
            </Grid>
          </Grid>
        </Grid>
      </Grid>
    </Paper>
  );
};

export default ServiceMetrics;