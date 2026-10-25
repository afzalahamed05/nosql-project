import React, { createContext, useState, useContext, useCallback, useEffect } from 'react';
import { apiService } from '../services/api';
import { useSnackbar } from 'notistack';

const AnomalyContext = createContext({});

export const useAnomaly = () => {
  const context = useContext(AnomalyContext);
  if (!context) {
    throw new Error('useAnomaly must be used within AnomalyProvider');
  }
  return context;
};

export const AnomalyProvider = ({ children }) => {
  const { enqueueSnackbar } = useSnackbar();
  
  // State
  const [summary, setSummary] = useState(null);
  const [services, setServices] = useState([]);
  const [selectedService, setSelectedService] = useState(null);
  const [serviceDetails, setServiceDetails] = useState(null);
  const [logs, setLogs] = useState([]);
  const [anomalies, setAnomalies] = useState([]);
  const [windowMetrics, setWindowMetrics] = useState([]);
  const [modelVersions, setModelVersions] = useState([]);
  const [rules, setRules] = useState([]);
  
  // Loading states
  const [loading, setLoading] = useState({
    summary: false,
    services: false,
    serviceDetails: false,
    logs: false,
    anomalies: false,
    windowMetrics: false,
    modelVersions: false,
    rules: false,
  });
  
  // Filters
  const [filters, setFilters] = useState({
    timeRange: '24h',
    logLevel: null,
    detectionMethod: null,
    page: 1,
    pageSize: 50,
  });
  
  // Error state
  const [error, setError] = useState(null);
  
  // Helper to show errors
  const showError = useCallback((message) => {
    console.error(message);
    enqueueSnackbar(message, { variant: 'error' });
    setError(message);
  }, [enqueueSnackbar]);
  
  // Clear error
  const clearError = useCallback(() => {
    setError(null);
  }, []);
  
  // Fetch summary data
  const fetchSummary = useCallback(async () => {
    try {
      setLoading(prev => ({ ...prev, summary: true }));
      clearError();
      
      const response = await apiService.getSummary(filters.timeRange);
      setSummary(response.data);
    } catch (error) {
      showError(`Failed to fetch summary: ${error.message}`);
    } finally {
      setLoading(prev => ({ ...prev, summary: false }));
    }
  }, [filters.timeRange, showError, clearError]);
  
  // Fetch services list
  const fetchServices = useCallback(async () => {
    try {
      setLoading(prev => ({ ...prev, services: true }));
      clearError();
      
      const response = await apiService.getServices();
      setServices(response.data);
      
      // Auto-select first service if none selected
      if (response.data.length > 0 && !selectedService) {
        setSelectedService(response.data[0]);
      }
    } catch (error) {
      showError(`Failed to fetch services: ${error.message}`);
    } finally {
      setLoading(prev => ({ ...prev, services: false }));
    }
  }, [selectedService, showError, clearError]);
  
  // Fetch service details
  const fetchServiceDetails = useCallback(async (serviceName) => {
    if (!serviceName) return;
    
    try {
      setLoading(prev => ({ ...prev, serviceDetails: true }));
      clearError();
      
      const response = await apiService.getServiceDetails(serviceName, filters.timeRange);
      setServiceDetails(response.data);
    } catch (error) {
      showError(`Failed to fetch service details: ${error.message}`);
    } finally {
      setLoading(prev => ({ ...prev, serviceDetails: false }));
    }
  }, [filters.timeRange, showError, clearError]);
  
  // Fetch logs
  const fetchLogs = useCallback(async () => {
    try {
      setLoading(prev => ({ ...prev, logs: true }));
      clearError();
      
      const params = {
        page: filters.page,
        page_size: filters.pageSize,
        service_name: selectedService,
        log_level: filters.logLevel,
        sort_by: 'timestamp',
        sort_order: 'desc',
      };
      
      const response = await apiService.getLogs(params);
      setLogs(response.data);
    } catch (error) {
      showError(`Failed to fetch logs: ${error.message}`);
    } finally {
      setLoading(prev => ({ ...prev, logs: false }));
    }
  }, [selectedService, filters.page, filters.pageSize, filters.logLevel, showError, clearError]);
  
  // Fetch anomalies
  const fetchAnomalies = useCallback(async () => {
    try {
      setLoading(prev => ({ ...prev, anomalies: true }));
      clearError();
      
      const params = {
        page: filters.page,
        page_size: filters.pageSize,
        service_name: selectedService,
        detection_method: filters.detectionMethod,
        sort_by: 'timestamp',
        sort_order: 'desc',
      };
      
      const response = await apiService.getAnomalies(params);
      setAnomalies(response.data);
    } catch (error) {
      showError(`Failed to fetch anomalies: ${error.message}`);
    } finally {
      setLoading(prev => ({ ...prev, anomalies: false }));
    }
  }, [selectedService, filters.page, filters.pageSize, filters.detectionMethod, showError, clearError]);
  
  // Fetch window metrics for charts
  const fetchWindowMetrics = useCallback(async () => {
    try {
      setLoading(prev => ({ ...prev, windowMetrics: true }));
      clearError();
      
      const hours = filters.timeRange === '24h' ? 24 : 
                   filters.timeRange === '7d' ? 168 : 24;
      
      const response = await apiService.getWindowMetrics(selectedService, hours);
      setWindowMetrics(response.data);
    } catch (error) {
      showError(`Failed to fetch window metrics: ${error.message}`);
    } finally {
      setLoading(prev => ({ ...prev, windowMetrics: false }));
    }
  }, [selectedService, filters.timeRange, showError, clearError]);
  
  // Fetch model versions
  const fetchModelVersions = useCallback(async () => {
    try {
      setLoading(prev => ({ ...prev, modelVersions: true }));
      clearError();
      
      const response = await apiService.getModelVersions();
      setModelVersions(response.data);
    } catch (error) {
      showError(`Failed to fetch model versions: ${error.message}`);
    } finally {
      setLoading(prev => ({ ...prev, modelVersions: false }));
    }
  }, [showError, clearError]);
  
  // Fetch rules
  const fetchRules = useCallback(async () => {
    try {
      setLoading(prev => ({ ...prev, rules: true }));
      clearError();
      
      const response = await apiService.getRules();
      setRules(response.data);
    } catch (error) {
      showError(`Failed to fetch rules: ${error.message}`);
    } finally {
      setLoading(prev => ({ ...prev, rules: false }));
    }
  }, [showError, clearError]);
  
  // Retrain model
  const retrainModel = useCallback(async (trainingData) => {
    try {
      clearError();
      
      const response = await apiService.retrainModel(trainingData);
      enqueueSnackbar(response.data.message, { variant: 'success' });
      
      // Refresh model versions after retraining
      await fetchModelVersions();
      
      return response.data;
    } catch (error) {
      showError(`Failed to retrain model: ${error.message}`);
      throw error;
    }
  }, [enqueueSnackbar, fetchModelVersions, showError, clearError]);
  
  // Update filters
  const updateFilters = useCallback((newFilters) => {
    setFilters(prev => ({ ...prev, ...newFilters }));
  }, []);
  
  // Refresh all data
  const refreshAll = useCallback(async () => {
    await Promise.all([
      fetchSummary(),
      fetchServices(),
      fetchModelVersions(),
      fetchRules(),
    ]);
    
    if (selectedService) {
      await Promise.all([
        fetchServiceDetails(selectedService),
        fetchLogs(),
        fetchAnomalies(),
        fetchWindowMetrics(),
      ]);
    }
  }, [
    selectedService,
    fetchSummary,
    fetchServices,
    fetchServiceDetails,
    fetchLogs,
    fetchAnomalies,
    fetchWindowMetrics,
    fetchModelVersions,
    fetchRules,
  ]);
  
  // Effect to fetch initial data
  useEffect(() => {
    refreshAll();
  }, []);
  
  // Effect to update service details when selected service changes
  useEffect(() => {
    if (selectedService) {
      fetchServiceDetails(selectedService);
      fetchWindowMetrics();
      fetchLogs();
      fetchAnomalies();
    }
  }, [selectedService, fetchServiceDetails, fetchWindowMetrics, fetchLogs, fetchAnomalies]);
  
  // Effect to refresh data when filters change
  useEffect(() => {
    if (selectedService) {
      fetchServiceDetails(selectedService);
      fetchWindowMetrics();
      fetchLogs();
      fetchAnomalies();
    }
    fetchSummary();
  }, [filters.timeRange, filters.logLevel, filters.detectionMethod, filters.page, 
      selectedService, fetchSummary, fetchServiceDetails, fetchWindowMetrics, fetchLogs, fetchAnomalies]);
  
  // Context value
  const contextValue = {
    // State
    summary,
    services,
    selectedService,
    setSelectedService,
    serviceDetails,
    logs,
    anomalies,
    windowMetrics,
    modelVersions,
    rules,
    
    // Loading states
    loading,
    
    // Filters
    filters,
    updateFilters,
    
    // Error
    error,
    clearError,
    
    // Actions
    fetchSummary,
    fetchServices,
    fetchServiceDetails,
    fetchLogs,
    fetchAnomalies,
    fetchWindowMetrics,
    fetchModelVersions,
    fetchRules,
    retrainModel,
    refreshAll,
  };
  
  return (
    <AnomalyContext.Provider value={contextValue}>
      {children}
    </AnomalyContext.Provider>
  );
};