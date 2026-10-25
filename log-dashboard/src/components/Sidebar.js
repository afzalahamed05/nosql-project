import React from 'react';
import {
  Box,
  Divider,
  List,
  ListItem,
  ListItemButton,
  ListItemIcon,
  ListItemText,
  Typography,
  Chip,
  CircularProgress,
} from '@mui/material';
import DashboardIcon from '@mui/icons-material/Dashboard';
import TimelineIcon from '@mui/icons-material/Timeline';
import WarningIcon from '@mui/icons-material/Warning';
import ListAltIcon from '@mui/icons-material/ListAlt';
import SettingsIcon from '@mui/icons-material/Settings';
import RefreshIcon from '@mui/icons-material/Refresh';
import { useAnomaly } from '../contexts/AnomalyContext';
import { formatDistanceToNow } from 'date-fns';

const Sidebar = () => {
  const { 
    summary, 
    loading, 
    refreshAll,
    selectedService,
    setSelectedService,
    services 
  } = useAnomaly();

  const handleRefresh = () => {
    refreshAll();
  };

  const formatTime = (timestamp) => {
    if (!timestamp) return 'N/A';
    try {
      const date = new Date(timestamp);
      return formatDistanceToNow(date, { addSuffix: true });
    } catch (error) {
      return 'Invalid date';
    }
  };

  return (
    <Box sx={{ height: '100%', display: 'flex', flexDirection: 'column' }}>
      {/* Header */}
      <Box sx={{ p: 3, textAlign: 'center', borderBottom: 1, borderColor: 'divider' }}>
        <Typography variant="h6" gutterBottom>
          Anomaly Detection
        </Typography>
        <Typography variant="body2" color="text.secondary">
          Real-time Monitoring
        </Typography>
      </Box>

      {/* System Status */}
      <Box sx={{ p: 2, borderBottom: 1, borderColor: 'divider' }}>
        <Typography variant="subtitle2" gutterBottom>
          System Status
        </Typography>
        
        {loading.summary ? (
          <Box sx={{ display: 'flex', justifyContent: 'center', py: 2 }}>
            <CircularProgress size={24} />
          </Box>
        ) : summary ? (
          <Box>
            <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 1 }}>
              <Typography variant="body2">Total Logs:</Typography>
              <Typography variant="body2" fontWeight="medium">
                {summary.total_logs.toLocaleString()}
              </Typography>
            </Box>
            
            <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 1 }}>
              <Typography variant="body2">Anomalies:</Typography>
              <Chip
                label={`${summary.total_anomalies} (${(summary.anomaly_rate * 100).toFixed(1)}%)`}
                size="small"
                color={summary.anomaly_rate > 0.05 ? 'error' : 'success'}
                variant="outlined"
              />
            </Box>
            
            <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 1 }}>
              <Typography variant="body2">Services:</Typography>
              <Typography variant="body2" fontWeight="medium">
                {summary.services.length}
              </Typography>
            </Box>
            
            {summary.time_range?.latest && (
              <Box sx={{ display: 'flex', justifyContent: 'space-between' }}>
                <Typography variant="body2">Last Update:</Typography>
                <Typography variant="body2" color="text.secondary">
                  {formatTime(summary.time_range.latest)}
                </Typography>
              </Box>
            )}
          </Box>
        ) : (
          <Typography variant="body2" color="text.secondary">
            No data available
          </Typography>
        )}
        
        {/* Refresh button */}
        <Box sx={{ mt: 2 }}>
          <ListItemButton 
            onClick={handleRefresh}
            disabled={loading.summary}
            sx={{ borderRadius: 1 }}
          >
            <ListItemIcon sx={{ minWidth: 40 }}>
              <RefreshIcon fontSize="small" />
            </ListItemIcon>
            <ListItemText 
              primary="Refresh Data" 
              primaryTypographyProps={{ variant: 'body2' }}
            />
            {loading.summary && (
              <CircularProgress size={16} sx={{ ml: 1 }} />
            )}
          </ListItemButton>
        </Box>
      </Box>

      {/* Services List */}
      <Box sx={{ flexGrow: 1, overflow: 'auto', p: 2 }}>
        <Typography variant="subtitle2" gutterBottom>
          Services
        </Typography>
        
        {loading.services ? (
          <Box sx={{ display: 'flex', justifyContent: 'center', py: 2 }}>
            <CircularProgress size={24} />
          </Box>
        ) : services.length > 0 ? (
          <List dense disablePadding>
            {services.map((service) => (
              <ListItem key={service} disablePadding>
                <ListItemButton
                  selected={selectedService === service}
                  onClick={() => setSelectedService(service)}
                  sx={{
                    borderRadius: 1,
                    mb: 0.5,
                    '&.Mui-selected': {
                      backgroundColor: 'primary.light',
                      '&:hover': {
                        backgroundColor: 'primary.light',
                      },
                    },
                  }}
                >
                  <ListItemText 
                    primary={service}
                    primaryTypographyProps={{
                      variant: 'body2',
                      fontWeight: selectedService === service ? 'medium' : 'regular',
                    }}
                  />
                </ListItemButton>
              </ListItem>
            ))}
          </List>
        ) : (
          <Typography variant="body2" color="text.secondary">
            No services found
          </Typography>
        )}
      </Box>

      {/* Navigation */}
      <Box sx={{ p: 2, borderTop: 1, borderColor: 'divider' }}>
        <Typography variant="subtitle2" gutterBottom>
          Navigation
        </Typography>
        
        <List dense disablePadding>
          <ListItem disablePadding>
            <ListItemButton sx={{ borderRadius: 1, mb: 0.5 }}>
              <ListItemIcon sx={{ minWidth: 40 }}>
                <DashboardIcon fontSize="small" />
              </ListItemIcon>
              <ListItemText 
                primary="Dashboard" 
                primaryTypographyProps={{ variant: 'body2' }}
              />
            </ListItemButton>
          </ListItem>
          
          <ListItem disablePadding>
            <ListItemButton sx={{ borderRadius: 1, mb: 0.5 }}>
              <ListItemIcon sx={{ minWidth: 40 }}>
                <TimelineIcon fontSize="small" />
              </ListItemIcon>
              <ListItemText 
                primary="Analytics" 
                primaryTypographyProps={{ variant: 'body2' }}
              />
            </ListItemButton>
          </ListItem>
          
          <ListItem disablePadding>
            <ListItemButton sx={{ borderRadius: 1, mb: 0.5 }}>
              <ListItemIcon sx={{ minWidth: 40 }}>
                <WarningIcon fontSize="small" />
              </ListItemIcon>
              <ListItemText 
                primary="Anomalies" 
                primaryTypographyProps={{ variant: 'body2' }}
              />
            </ListItemButton>
          </ListItem>
          
          <ListItem disablePadding>
            <ListItemButton sx={{ borderRadius: 1, mb: 0.5 }}>
              <ListItemIcon sx={{ minWidth: 40 }}>
                <ListAltIcon fontSize="small" />
              </ListItemIcon>
              <ListItemText 
                primary="Logs" 
                primaryTypographyProps={{ variant: 'body2' }}
              />
            </ListItemButton>
          </ListItem>
          
          <Divider sx={{ my: 1 }} />
          
          <ListItem disablePadding>
            <ListItemButton sx={{ borderRadius: 1 }}>
              <ListItemIcon sx={{ minWidth: 40 }}>
                <SettingsIcon fontSize="small" />
              </ListItemIcon>
              <ListItemText 
                primary="Settings" 
                primaryTypographyProps={{ variant: 'body2' }}
              />
            </ListItemButton>
          </ListItem>
        </List>
      </Box>

      {/* Footer */}
      <Box sx={{ p: 2, borderTop: 1, borderColor: 'divider', textAlign: 'center' }}>
        <Typography variant="caption" color="text.secondary">
          Log Anomaly Detection System
        </Typography>
        <br />
        <Typography variant="caption" color="text.secondary">
          v1.0.0
        </Typography>
      </Box>
    </Box>
  );
};

export default Sidebar;