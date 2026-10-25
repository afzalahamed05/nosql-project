import React, { useState } from 'react';
import {
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  TablePagination,
  Chip,
  IconButton,
  Tooltip,
  Box,
  Typography,
  CircularProgress,
  Paper,
} from '@mui/material';
import InfoIcon from '@mui/icons-material/Info';
import ErrorIcon from '@mui/icons-material/Error';
import WarningIcon from '@mui/icons-material/Warning';
import CheckCircleIcon from '@mui/icons-material/CheckCircle';
import { useAnomaly } from '../contexts/AnomalyContext';
import { format } from 'date-fns';

const LogTable = () => {
  const { logs, loading } = useAnomaly();
  const [page, setPage] = useState(0);
  const [rowsPerPage, setRowsPerPage] = useState(5);
  
  if (loading.logs) {
    return (
      <Box sx={{ display: 'flex', justifyContent: 'center', alignItems: 'center', height: 300 }}>
        <CircularProgress />
        <Typography variant="body2" sx={{ ml: 2 }}>
          Loading logs...
        </Typography>
      </Box>
    );
  }
  
  const data = logs?.data || [];
  const total = logs?.total || 0;
  
  if (data.length === 0) {
    return (
      <Box sx={{ display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center', height: 300 }}>
        <InfoIcon sx={{ fontSize: 48, color: 'info.main', mb: 2 }} />
        <Typography variant="body1" gutterBottom>
          No Logs Found
        </Typography>
        <Typography variant="body2" color="text.secondary">
          No log entries in the selected time range.
        </Typography>
      </Box>
    );
  }
  
  const handleChangePage = (event, newPage) => {
    setPage(newPage);
  };
  
  const handleChangeRowsPerPage = (event) => {
    setRowsPerPage(parseInt(event.target.value, 10));
    setPage(0);
  };
  
  // Format timestamp
  const formatTimestamp = (timestamp) => {
    try {
      return format(new Date(timestamp), 'HH:mm:ss');
    } catch (error) {
      return 'Invalid date';
    }
  };
  
  // Get log level icon and color
  const getLogLevelInfo = (level) => {
    switch (level?.toUpperCase()) {
      case 'ERROR':
        return { icon: <ErrorIcon fontSize="small" />, color: 'error' };
      case 'WARNING':
        return { icon: <WarningIcon fontSize="small" />, color: 'warning' };
      case 'INFO':
        return { icon: <InfoIcon fontSize="small" />, color: 'info' };
      case 'DEBUG':
        return { icon: <CheckCircleIcon fontSize="small" />, color: 'success' };
      default:
        return { icon: <InfoIcon fontSize="small" />, color: 'default' };
    }
  };
  
  // Get HTTP status color
  const getStatusColor = (status) => {
    if (!status) return 'default';
    if (status >= 500) return 'error';
    if (status >= 400) return 'warning';
    if (status >= 300) return 'info';
    return 'success';
  };
  
  // Truncate message
  const truncateMessage = (message, length = 50) => {
    if (!message) return '';
    if (message.length <= length) return message;
    return message.substring(0, length) + '...';
  };
  
  // Paginate data
  const paginatedData = data.slice(page * rowsPerPage, page * rowsPerPage + rowsPerPage);
  
  return (
    <Box>
      <TableContainer component={Paper} variant="outlined">
        <Table size="small">
          <TableHead>
            <TableRow>
              <TableCell>Time</TableCell>
              <TableCell>Level</TableCell>
              <TableCell>Service</TableCell>
              <TableCell>Message</TableCell>
              <TableCell>Status</TableCell>
              <TableCell>Response Time</TableCell>
            </TableRow>
          </TableHead>
          <TableBody>
            {paginatedData.map((row, index) => {
              const levelInfo = getLogLevelInfo(row.log_level);
              const statusColor = getStatusColor(row.status_code);
              
              return (
                <TableRow key={row._id || index} hover>
                  <TableCell>
                    <Typography variant="caption" color="text.secondary">
                      {formatTimestamp(row.timestamp)}
                    </Typography>
                  </TableCell>
                  <TableCell>
                    <Tooltip title={row.log_level || 'Unknown'}>
                      <Chip
                        icon={levelInfo.icon}
                        label={row.log_level || 'UNKNOWN'}
                        size="small"
                        color={levelInfo.color}
                        variant="outlined"
                      />
                    </Tooltip>
                  </TableCell>
                  <TableCell>
                    <Typography variant="body2" fontWeight="medium">
                      {row.service_name || 'Unknown'}
                    </Typography>
                  </TableCell>
                  <TableCell>
                    <Tooltip title={row.message || 'No message'}>
                      <Typography variant="body2" sx={{ maxWidth: 200 }}>
                        {truncateMessage(row.message, 40)}
                      </Typography>
                    </Tooltip>
                  </TableCell>
                  <TableCell>
                    {row.status_code ? (
                      <Chip
                        label={row.status_code}
                        size="small"
                        color={statusColor}
                        variant="outlined"
                      />
                    ) : (
                      <Typography variant="caption" color="text.secondary">
                        N/A
                      </Typography>
                    )}
                  </TableCell>
                  <TableCell>
                    {row.response_time_ms ? (
                      <Box sx={{ display: 'flex', alignItems: 'center' }}>
                        <Typography 
                          variant="body2" 
                          color={
                            row.response_time_ms > 1000 ? 'error' :
                            row.response_time_ms > 500 ? 'warning' : 'text.primary'
                          }
                        >
                          {row.response_time_ms.toFixed(0)} ms
                        </Typography>
                      </Box>
                    ) : (
                      <Typography variant="caption" color="text.secondary">
                        N/A
                      </Typography>
                    )}
                  </TableCell>
                </TableRow>
              );
            })}
          </TableBody>
        </Table>
      </TableContainer>
      
      <TablePagination
        rowsPerPageOptions={[5, 10, 25]}
        component="div"
        count={total}
        rowsPerPage={rowsPerPage}
        page={page}
        onPageChange={handleChangePage}
        onRowsPerPageChange={handleChangeRowsPerPage}
        labelRowsPerPage="Rows per page:"
        labelDisplayedRows={({ from, to, count }) => `${from}-${to} of ${count}`}
      />
      
      {/* Summary row */}
      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mt: 2, p: 1, bgcolor: 'grey.50', borderRadius: 1 }}>
        <Typography variant="caption" color="text.secondary">
          Showing {paginatedData.length} of {total} logs
        </Typography>
        {total > 0 && (
          <Box sx={{ display: 'flex', gap: 2 }}>
            <Typography variant="caption" color="text.secondary">
              Errors: {data.filter(row => row.log_level === 'ERROR').length}
            </Typography>
            <Typography variant="caption" color="text.secondary">
              Warnings: {data.filter(row => row.log_level === 'WARNING').length}
            </Typography>
            <Typography variant="caption" color="text.secondary">
              Avg Response: {data.filter(row => row.response_time_ms).length > 0 
                ? `${(data.reduce((sum, row) => sum + (row.response_time_ms || 0), 0) / data.filter(row => row.response_time_ms).length).toFixed(0)} ms`
                : 'N/A'
              }
            </Typography>
          </Box>
        )}
      </Box>
    </Box>
  );
};

export default LogTable;