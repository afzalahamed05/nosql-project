import React from 'react';
import {
  ComposedChart,
  Line,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
} from 'recharts';
import { Box, Typography, CircularProgress } from '@mui/material';
import { useAnomaly } from '../contexts/AnomalyContext';
import { format } from 'date-fns';

const ErrorRateChart = () => {
  const { windowMetrics, loading } = useAnomaly();
  
  // Process data for chart
  const chartData = windowMetrics
    .filter(item => item.error_rate !== undefined && item.window_start)
    .map(item => ({
      time: new Date(item.window_start),
      errorRate: item.error_rate * 100, // Convert to percentage
      errorCount: item.error_count,
      requestCount: item.request_count,
    }))
    .sort((a, b) => a.time - b.time)
    .slice(-50); // Last 50 data points
  
  // Calculate average error rate
  const avgErrorRate = chartData.length > 0 
    ? chartData.reduce((sum, item) => sum + item.errorRate, 0) / chartData.length
    : 0;
  
  // Format time for display
  const formatTime = (date) => {
    return format(new Date(date), 'HH:mm');
  };
  
  // Custom tooltip
  const CustomTooltip = ({ active, payload, label }) => {
    if (active && payload && payload.length) {
      return (
        <Box sx={{ 
          backgroundColor: 'white', 
          p: 1.5, 
          border: '1px solid #ccc',
          borderRadius: 1,
          boxShadow: 1
        }}>
          <Typography variant="body2" sx={{ fontWeight: 'medium', mb: 1 }}>
            {format(new Date(label), 'MMM d, HH:mm')}
          </Typography>
          {payload.map((entry, index) => (
            <Typography 
              key={index} 
              variant="body2"
              sx={{ 
                color: entry.color,
                display: 'flex',
                justifyContent: 'space-between',
                gap: 2
              }}
            >
              <span>{entry.name}:</span>
              <span style={{ fontWeight: 'bold' }}>
                {entry.name === 'errorRate' 
                  ? `${entry.value.toFixed(1)}%`
                  : entry.value.toLocaleString()
                }
              </span>
            </Typography>
          ))}
        </Box>
      );
    }
    return null;
  };
  
  if (loading.windowMetrics) {
    return (
      <Box sx={{ display: 'flex', justifyContent: 'center', alignItems: 'center', height: 300 }}>
        <CircularProgress />
        <Typography variant="body2" sx={{ ml: 2 }}>
          Loading chart data...
        </Typography>
      </Box>
    );
  }
  
  if (chartData.length === 0) {
    return (
      <Box sx={{ display: 'flex', justifyContent: 'center', alignItems: 'center', height: 300 }}>
        <Typography variant="body2" color="text.secondary">
          No error rate data available
        </Typography>
      </Box>
    );
  }
  
  return (
    <Box>
      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 2 }}>
        <Typography variant="caption" color="text.secondary">
          Average Error Rate: {avgErrorRate.toFixed(1)}%
        </Typography>
      </Box>
      
      <ResponsiveContainer width="100%" height={300}>
        <ComposedChart
          data={chartData}
          margin={{ top: 5, right: 30, left: 20, bottom: 5 }}
        >
          <CartesianGrid strokeDasharray="3 3" stroke="#f0f0f0" />
          <XAxis
            dataKey="time"
            tickFormatter={formatTime}
            stroke="#666"
            fontSize={12}
          />
          <YAxis
            yAxisId="left"
            label={{ 
              value: 'Error Rate %', 
              angle: -90, 
              position: 'insideLeft',
              offset: 10,
              style: { textAnchor: 'middle', fontSize: 12 }
            }}
            stroke="#666"
            fontSize={12}
          />
          <YAxis
            yAxisId="right"
            orientation="right"
            label={{ 
              value: 'Requests', 
              angle: 90, 
              position: 'insideRight',
              offset: 10,
              style: { textAnchor: 'middle', fontSize: 12 }
            }}
            stroke="#666"
            fontSize={12}
          />
          <Tooltip content={<CustomTooltip />} />
          <Legend />
          <Bar
            yAxisId="right"
            dataKey="requestCount"
            name="Requests"
            fill="#8884d8"
            opacity={0.6}
          />
          <Line
            yAxisId="left"
            type="monotone"
            dataKey="errorRate"
            name="Error Rate"
            stroke="#ff7300"
            strokeWidth={2}
            dot={false}
            activeDot={{ r: 6 }}
          />
        </ComposedChart>
      </ResponsiveContainer>
    </Box>
  );
};

export default ErrorRateChart;