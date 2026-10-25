import React from 'react';
import {
  LineChart,
  Line,
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

const ResponseTimeChart = () => {
  const { windowMetrics, loading } = useAnomaly();
  
  // Process data for chart
  const chartData = windowMetrics
    .filter(item => item.avg_response_time_ms && item.window_start)
    .map(item => ({
      time: new Date(item.window_start),
      avg: item.avg_response_time_ms,
      p95: item.p95_response_time_ms,
      p99: item.p99_response_time_ms,
      requests: item.request_count,
    }))
    .sort((a, b) => a.time - b.time)
    .slice(-50); // Last 50 data points
  
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
                {entry.name === 'requests' 
                  ? entry.value.toLocaleString()
                  : `${entry.value.toFixed(0)} ms`
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
          No response time data available
        </Typography>
      </Box>
    );
  }
  
  return (
    <ResponsiveContainer width="100%" height={300}>
      <LineChart
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
          label={{ 
            value: 'ms', 
            angle: -90, 
            position: 'insideLeft',
            offset: 10,
            style: { textAnchor: 'middle', fontSize: 12 }
          }}
          stroke="#666"
          fontSize={12}
        />
        <Tooltip content={<CustomTooltip />} />
        <Legend />
        <Line
          type="monotone"
          dataKey="avg"
          name="Average"
          stroke="#8884d8"
          strokeWidth={2}
          dot={false}
          activeDot={{ r: 6 }}
        />
        <Line
          type="monotone"
          dataKey="p95"
          name="95th Percentile"
          stroke="#82ca9d"
          strokeWidth={2}
          dot={false}
          strokeDasharray="5 5"
        />
        <Line
          type="monotone"
          dataKey="p99"
          name="99th Percentile"
          stroke="#ff7300"
          strokeWidth={1}
          dot={false}
          strokeDasharray="3 3"
        />
      </LineChart>
    </ResponsiveContainer>
  );
};

export default ResponseTimeChart;