"""
Rolling window feature extraction for anomaly detection.
Extracts request count, error rate, latency statistics, and other features
for mixed anomaly and gradual degradation detection.
"""

from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional, Tuple
import numpy as np
from collections import defaultdict
import pandas as pd

from models.log_schema import LogEntry, WindowFeatures


class WindowFeatureExtractor:
    """
    Extracts rolling window-level features from log data.
    
    Features include:
    - Request count statistics
    - Error rate and distribution
    - Latency statistics (avg, p95, p99, max)
    - Request/response size statistics
    - HTTP method distribution
    - Status code distribution
    """
    
    def __init__(self, window_size_minutes: int = 5, slide_minutes: int = 1):
        """
        Initialize window feature extractor.
        
        Args:
            window_size_minutes: Size of rolling window in minutes
            slide_minutes: Slide interval for windows
        """
        self.window_size_minutes = window_size_minutes
        self.slide_minutes = slide_minutes
        self.window_size_seconds = window_size_minutes * 60
        
    def extract_from_logs(self, logs: List[LogEntry]) -> List[WindowFeatures]:
        """
        Extract window features from a list of log entries.
        
        Args:
            logs: List of log entries
            
        Returns:
            List of window features
        """
        if not logs:
            return []
        
        # Sort logs by timestamp
        logs.sort(key=lambda x: x.timestamp)
        
        # Get time range
        min_time = logs[0].timestamp
        max_time = logs[-1].timestamp
        
        # Create windows
        windows = self._create_windows(min_time, max_time)
        
        # Process each window
        window_features = []
        for window_start, window_end in windows:
            window_logs = self._get_logs_in_window(logs, window_start, window_end)
            
            if window_logs:
                features = self._extract_window_features(window_logs, window_start, window_end)
                window_features.append(features)
        
        return window_features
    
    def extract_from_mongo_cursor(self, cursor, service_name: Optional[str] = None) -> List[WindowFeatures]:
        """
        Extract window features from MongoDB cursor.
        
        Args:
            cursor: MongoDB cursor with log entries
            service_name: Optional service name filter
            
        Returns:
            List of window features
        """
        logs = []
        for doc in cursor:
            try:
                log = LogEntry(**doc)
                if service_name is None or log.service_name == service_name:
                    logs.append(log)
            except Exception as e:
                print(f"Error parsing log entry: {e}")
                continue
        
        return self.extract_from_logs(logs)
    
    def _create_windows(self, start_time: datetime, end_time: datetime) -> List[Tuple[datetime, datetime]]:
        """
        Create sliding windows.
        
        Args:
            start_time: Start time
            end_time: End time
            
        Returns:
            List of (window_start, window_end) tuples
        """
        windows = []
        current_start = start_time
        
        while current_start < end_time:
            current_end = current_start + timedelta(minutes=self.window_size_minutes)
            windows.append((current_start, current_end))
            current_start += timedelta(minutes=self.slide_minutes)
        
        return windows
    
    def _get_logs_in_window(self, logs: List[LogEntry], 
                           window_start: datetime, 
                           window_end: datetime) -> List[LogEntry]:
        """
        Get logs within a specific time window.
        
        Args:
            logs: List of all logs
            window_start: Window start time
            window_end: Window end time
            
        Returns:
            Logs within the window
        """
        return [
            log for log in logs
            if window_start <= log.timestamp < window_end
        ]
    
    def _extract_window_features(self, logs: List[LogEntry], 
                                window_start: datetime, 
                                window_end: datetime) -> WindowFeatures:
        """
        Extract features from logs in a single window.
        
        Args:
            logs: Logs in the window
            window_start: Window start time
            window_end: Window end time
            
        Returns:
            WindowFeatures object
        """
        service_name = logs[0].service_name if logs else "unknown"
        
        # Basic counts
        request_count = len(logs)
        error_count = sum(1 for log in logs if log.log_level == "ERROR")
        error_rate = error_count / max(request_count, 1)
        
        # Extract latency values (response times)
        response_times = [
            log.response_time_ms for log in logs 
            if log.response_time_ms is not None
        ]
        
        # Extract request/response sizes
        request_sizes = [
            log.request_size_bytes for log in logs 
            if log.request_size_bytes is not None
        ]
        response_sizes = [
            log.response_size_bytes for log in logs 
            if log.response_size_bytes is not None
        ]
        
        # HTTP method distribution
        http_methods = defaultdict(int)
        for log in logs:
            if log.http_method:
                http_methods[log.http_method] += 1
        
        # Status code distribution
        status_codes = defaultdict(int)
        for log in logs:
            if log.status_code:
                status_codes[log.status_code] += 1
        
        # Calculate latency statistics
        if response_times:
            avg_response_time = np.mean(response_times)
            p95_response_time = np.percentile(response_times, 95)
            p99_response_time = np.percentile(response_times, 99)
            max_response_time = np.max(response_times)
        else:
            avg_response_time = p95_response_time = p99_response_time = max_response_time = 0.0
        
        # Calculate size statistics
        avg_request_size = np.mean(request_sizes) if request_sizes else 0.0
        avg_response_size = np.mean(response_sizes) if response_sizes else 0.0
        
        # Create feature vector for ML model
        feature_vector = self._create_feature_vector(
            request_count=request_count,
            error_rate=error_rate,
            avg_response_time=avg_response_time,
            p95_response_time=p95_response_time,
            p99_response_time=p99_response_time,
            max_response_time=max_response_time,
            avg_request_size=avg_request_size,
            avg_response_size=avg_response_size,
            http_method_distribution=http_methods,
            status_code_distribution=status_codes
        )
        
        # Create WindowFeatures object
        return WindowFeatures(
            window_start=window_start,
            window_end=window_end,
            window_size_minutes=self.window_size_minutes,
            service_name=service_name,
            request_count=request_count,
            error_count=error_count,
            error_rate=error_rate,
            avg_response_time_ms=avg_response_time,
            p95_response_time_ms=p95_response_time,
            p99_response_time_ms=p99_response_time,
            max_response_time_ms=max_response_time,
            avg_request_size_bytes=avg_request_size,
            avg_response_size_bytes=avg_response_size,
            http_method_distribution=dict(http_methods),
            status_code_distribution=dict(status_codes),
            feature_vector=feature_vector
        )
    
    def _create_feature_vector(self, **kwargs) -> List[float]:
        """
        Create numerical feature vector for ML model.
        
        Args:
            **kwargs: Window feature values
            
        Returns:
            List of numerical features
        """
        features = []
        
        # Basic features
        features.append(kwargs.get('request_count', 0))
        features.append(kwargs.get('error_rate', 0.0))
        features.append(kwargs.get('avg_response_time', 0.0))
        features.append(kwargs.get('p95_response_time', 0.0))
        features.append(kwargs.get('p99_response_time', 0.0))
        features.append(kwargs.get('max_response_time', 0.0))
        features.append(kwargs.get('avg_request_size', 0.0))
        features.append(kwargs.get('avg_response_size', 0.0))
        
        # HTTP method features (one-hot encoded)
        http_methods = kwargs.get('http_method_distribution', {})
        for method in ['GET', 'POST', 'PUT', 'DELETE', 'PATCH']:
            features.append(http_methods.get(method, 0))
        
        # Status code features (grouped)
        status_codes = kwargs.get('status_code_distribution', {})
        status_groups = {
            '2xx': sum(count for code, count in status_codes.items() if 200 <= code < 300),
            '3xx': sum(count for code, count in status_codes.items() if 300 <= code < 400),
            '4xx': sum(count for code, count in status_codes.items() if 400 <= code < 500),
            '5xx': sum(count for code, count in status_codes.items() if 500 <= code < 600)
        }
        
        for group in ['2xx', '3xx', '4xx', '5xx']:
            features.append(status_groups.get(group, 0))
        
        # Derived features
        features.append(features[0] * features[1])  # Error count approximation
        features.append(features[2] / max(features[0], 1))  # Response time per request
        
        return features
    
    def get_feature_names(self) -> List[str]:
        """
        Get names of features in the feature vector.
        
        Returns:
            List of feature names
        """
        feature_names = [
            'request_count',
            'error_rate',
            'avg_response_time_ms',
            'p95_response_time_ms',
            'p99_response_time_ms',
            'max_response_time_ms',
            'avg_request_size_bytes',
            'avg_response_size_bytes',
            'http_GET_count',
            'http_POST_count',
            'http_PUT_count',
            'http_DELETE_count',
            'http_PATCH_count',
            'status_2xx_count',
            'status_3xx_count',
            'status_4xx_count',
            'status_5xx_count',
            'error_count_approx',
            'response_time_per_request'
        ]
        
        return feature_names
    
    def extract_real_time(self, db, service_name: str, 
                         lookback_minutes: int = 10) -> Optional[WindowFeatures]:
        """
        Extract features for the most recent window in real-time.
        
        Args:
            db: MongoDB database instance
            service_name: Service name
            lookback_minutes: Minutes to look back
            
        Returns:
            WindowFeatures for the most recent window
        """
        collection = db["log_entries"]
        
        # Calculate time range
        end_time = datetime.utcnow()
        start_time = end_time - timedelta(minutes=lookback_minutes)
        
        # Query logs for the service
        query = {
            "service_name": service_name,
            "timestamp": {"$gte": start_time, "$lt": end_time}
        }
        
        cursor = collection.find(query).sort("timestamp", 1)
        logs = []
        
        for doc in cursor:
            try:
                logs.append(LogEntry(**doc))
            except Exception as e:
                print(f"Error parsing log entry: {e}")
                continue
        
        if not logs:
            return None
        
        # Create windows and get the most recent complete window
        windows = self._create_windows(start_time, end_time)
        
        # Get the most recent window that's fully within our data
        for window_start, window_end in reversed(windows):
            window_logs = self._get_logs_in_window(logs, window_start, window_end)
            
            # Check if window has sufficient data (at least 1 request per minute on average)
            expected_min_requests = self.window_size_minutes
            if len(window_logs) >= expected_min_requests:
                return self._extract_window_features(window_logs, window_start, window_end)
        
        return None