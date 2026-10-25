"""
Comprehensive evaluation metrics for anomaly detection system.
Implements precision, recall, F1, false-positive rate, per-scenario recall,
confusion matrices, detection latency, and throughput measurements.
"""

from typing import List, Dict, Any, Optional, Tuple
import numpy as np
from datetime import datetime, timedelta
from sklearn.metrics import (
    precision_score, recall_score, f1_score, 
    confusion_matrix, roc_curve, auc
)
import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
import json

from models.log_schema import AnomalyDetectionResult, WindowFeatures


class EvaluationMetrics:
    """
    Comprehensive evaluation metrics for anomaly detection.
    
    Implements all requested metrics:
    - Precision, Recall, F1 Score
    - False Positive Rate
    - Per-scenario Recall
    - Confusion Matrices
    - Detection Latency
    - Throughput
    - End-to-end latency measurement
    """
    
    def __init__(self, test_data_only: bool = True):
        """
        Initialize evaluation metrics.
        
        Args:
            test_data_only: Ensure only test data is used (prevent data leakage)
        """
        self.test_data_only = test_data_only
        self.results: List[Dict[str, Any]] = []
        self.true_labels: List[bool] = []
        self.predicted_labels: List[bool] = []
        self.confidence_scores: List[float] = []
        self.detection_latencies: List[float] = []
        self.scenario_labels: List[str] = []
        
        # Performance tracking
        self.metrics_summary = {}
        self.confusion_matrices = {}
        self.roc_data = {}
        
    def add_result(self, 
                  result: Dict[str, Any], 
                  true_label: bool, 
                  scenario: Optional[str] = None,
                  ingestion_timestamp: Optional[datetime] = None):
        """
        Add a detection result for evaluation.
        
        Args:
            result: Detection result dictionary
            true_label: Ground truth label (True for anomaly, False for normal)
            scenario: Scenario label for per-scenario metrics
            ingestion_timestamp: When the log was ingested (for end-to-end latency)
        """
        if not self.test_data_only:
            print("Warning: Adding non-test data. Ensure this is for evaluation only.")
        
        self.results.append(result)
        self.true_labels.append(true_label)
        self.predicted_labels.append(result.get("final_is_anomaly", False))
        self.confidence_scores.append(result.get("confidence", 0.0))
        
        # Calculate end-to-end latency if ingestion timestamp provided
        if ingestion_timestamp and "detection_timestamp" in result:
            detection_time = result["detection_timestamp"]
            if isinstance(detection_time, str):
                detection_time = datetime.fromisoformat(detection_time.replace('Z', '+00:00'))
            
            latency = (detection_time - ingestion_timestamp).total_seconds() * 1000  # ms
            self.detection_latencies.append(latency)
        
        # Add scenario label
        self.scenario_labels.append(scenario or "unknown")
        
        # Track detection latency from result if available
        if "detection_latency_ms" in result:
            self.detection_latencies.append(result["detection_latency_ms"])
    
    def calculate_all_metrics(self) -> Dict[str, Any]:
        """
        Calculate all evaluation metrics.
        
        Returns:
            Dictionary with all calculated metrics
        """
        if not self.results:
            raise ValueError("No results available for evaluation")
        
        print("Calculating comprehensive evaluation metrics...")
        
        # Basic classification metrics
        precision, recall, f1, fpr = self._calculate_basic_metrics()
        
        # Confusion matrix
        cm = self._calculate_confusion_matrix()
        
        # Per-scenario recall
        per_scenario_recall = self._calculate_per_scenario_recall()
        
        # ROC curve and AUC
        roc_auc = self._calculate_roc_auc()
        
        # Latency metrics
        latency_metrics = self._calculate_latency_metrics()
        
        # Throughput metrics
        throughput_metrics = self._calculate_throughput_metrics()
        
        # Detection method breakdown
        method_breakdown = self._analyze_detection_methods()
        
        # Borderline persistence analysis
        persistence_analysis = self._analyze_borderline_persistence()
        
        # Compile all metrics
        self.metrics_summary = {
            "basic_metrics": {
                "precision": precision,
                "recall": recall,
                "f1_score": f1,
                "false_positive_rate": fpr,
                "accuracy": self._calculate_accuracy(),
                "balanced_accuracy": self._calculate_balanced_accuracy()
            },
            "confusion_matrix": cm,
            "per_scenario_recall": per_scenario_recall,
            "roc_auc": roc_auc,
            "latency_metrics": latency_metrics,
            "throughput_metrics": throughput_metrics,
            "detection_method_breakdown": method_breakdown,
            "borderline_persistence_analysis": persistence_analysis,
            "sample_statistics": {
                "total_samples": len(self.results),
                "true_anomalies": sum(self.true_labels),
                "predicted_anomalies": sum(self.predicted_labels),
                "anomaly_prevalence": sum(self.true_labels) / len(self.true_labels)
            }
        }
        
        print("Evaluation metrics calculated successfully.")
        return self.metrics_summary
    
    def _calculate_basic_metrics(self) -> Tuple[float, float, float, float]:
        """Calculate precision, recall, F1, and false positive rate."""
        if not self.predicted_labels:
            return 0.0, 0.0, 0.0, 0.0
        
        precision = precision_score(self.true_labels, self.predicted_labels, zero_division=0)
        recall = recall_score(self.true_labels, self.predicted_labels, zero_division=0)
        f1 = f1_score(self.true_labels, self.predicted_labels, zero_division=0)
        
        # Calculate false positive rate
        tn, fp, fn, tp = confusion_matrix(self.true_labels, self.predicted_labels).ravel()
        fpr = fp / (fp + tn) if (fp + tn) > 0 else 0
        
        return precision, recall, f1, fpr
    
    def _calculate_confusion_matrix(self) -> Dict[str, int]:
        """Calculate confusion matrix."""
        if not self.predicted_labels:
            return {}
        
        cm = confusion_matrix(self.true_labels, self.predicted_labels)
        if cm.shape == (2, 2):
            tn, fp, fn, tp = cm.ravel()
            return {
                "true_negative": int(tn),
                "false_positive": int(fp),
                "false_negative": int(fn),
                "true_positive": int(tp)
            }
        else:
            return {}
    
    def _calculate_per_scenario_recall(self) -> Dict[str, float]:
        """Calculate recall for each scenario."""
        scenario_data = {}
        
        for true, pred, scenario in zip(self.true_labels, self.predicted_labels, self.scenario_labels):
            if scenario not in scenario_data:
                scenario_data[scenario] = {"true": 0, "detected": 0}
            
            if true:  # Only count actual anomalies
                scenario_data[scenario]["true"] += 1
                if pred:
                    scenario_data[scenario]["detected"] += 1
        
        # Calculate recall per scenario
        per_scenario_recall = {}
        for scenario, data in scenario_data.items():
            if data["true"] > 0:
                recall = data["detected"] / data["true"]
                per_scenario_recall[scenario] = {
                    "recall": recall,
                    "samples": data["true"],
                    "detected": data["detected"]
                }
        
        return per_scenario_recall
    
    def _calculate_roc_auc(self) -> Dict[str, Any]:
        """Calculate ROC curve and AUC."""
        if not self.confidence_scores or len(set(self.true_labels)) < 2:
            return {"auc": 0.0, "roc_curve": None}
        
        try:
            fpr, tpr, thresholds = roc_curve(self.true_labels, self.confidence_scores)
            roc_auc = auc(fpr, tpr)
            
            # Find optimal threshold (closest to top-left corner)
            distances = np.sqrt(fpr**2 + (1 - tpr)**2)
            optimal_idx = np.argmin(distances)
            optimal_threshold = thresholds[optimal_idx]
            
            self.roc_data = {
                "fpr": fpr.tolist(),
                "tpr": tpr.tolist(),
                "thresholds": thresholds.tolist(),
                "optimal_threshold": float(optimal_threshold)
            }
            
            return {
                "auc": float(roc_auc),
                "optimal_threshold": float(optimal_threshold),
                "has_roc_data": True
            }
        except Exception as e:
            print(f"ROC calculation failed: {e}")
            return {"auc": 0.0, "roc_curve": None, "error": str(e)}
    
    def _calculate_latency_metrics(self) -> Dict[str, float]:
        """Calculate latency statistics."""
        if not self.detection_latencies:
            return {}
        
        latencies = np.array(self.detection_latencies)
        
        return {
            "mean_ms": float(np.mean(latencies)),
            "median_ms": float(np.median(latencies)),
            "p90_ms": float(np.percentile(latencies, 90)),
            "p95_ms": float(np.percentile(latencies, 95)),
            "p99_ms": float(np.percentile(latencies, 99)),
            "max_ms": float(np.max(latencies)),
            "min_ms": float(np.min(latencies)),
            "std_ms": float(np.std(latencies)),
            "sample_count": len(latencies)
        }
    
    def _calculate_throughput_metrics(self) -> Dict[str, float]:
        """Calculate throughput statistics."""
        if not self.results:
            return {}
        
        # Extract timestamps
        timestamps = []
        for result in self.results:
            ts = result.get("detection_timestamp")
            if ts:
                if isinstance(ts, str):
                    ts = datetime.fromisoformat(ts.replace('Z', '+00:00'))
                timestamps.append(ts)
        
        if len(timestamps) < 2:
            return {}
        
        # Sort timestamps
        timestamps.sort()
        
        # Calculate time range
        time_range = (timestamps[-1] - timestamps[0]).total_seconds()
        
        if time_range > 0:
            throughput_per_second = len(timestamps) / time_range
            throughput_per_minute = throughput_per_second * 60
            throughput_per_hour = throughput_per_minute * 60
        else:
            throughput_per_second = throughput_per_minute = throughput_per_hour = 0
        
        return {
            "throughput_per_second": throughput_per_second,
            "throughput_per_minute": throughput_per_minute,
            "throughput_per_hour": throughput_per_hour,
            "total_processed": len(self.results),
            "time_range_seconds": time_range,
            "first_timestamp": timestamps[0].isoformat() if timestamps else None,
            "last_timestamp": timestamps[-1].isoformat() if timestamps else None
        }
    
    def _calculate_accuracy(self) -> float:
        """Calculate overall accuracy."""
        if not self.predicted_labels:
            return 0.0
        
        correct = sum(1 for t, p in zip(self.true_labels, self.predicted_labels) if t == p)
        return correct / len(self.true_labels)
    
    def _calculate_balanced_accuracy(self) -> float:
        """Calculate balanced accuracy (average of sensitivity and specificity)."""
        if not self.predicted_labels:
            return 0.0
        
        cm = confusion_matrix(self.true_labels, self.predicted_labels)
        if cm.shape == (2, 2):
            tn, fp, fn, tp = cm.ravel()
            sensitivity = tp / (tp + fn) if (tp + fn) > 0 else 0
            specificity = tn / (tn + fp) if (tn + fp) > 0 else 0
            return (sensitivity + specificity) / 2
        return 0.0
    
    def _analyze_detection_methods(self) -> Dict[str, Any]:
        """Analyze which detection methods triggered anomalies."""
        method_counts = {}
        method_effectiveness = {}
        
        for result, true_label in zip(self.results, self.true_labels):
            method = result.get("detection_method", "unknown")
            
            # Count occurrences
            method_counts[method] = method_counts.get(method, 0) + 1
            
            # Track effectiveness
            if method not in method_effectiveness:
                method_effectiveness[method] = {"true_positives": 0, "total": 0}
            
            method_effectiveness[method]["total"] += 1
            if result.get("final_is_anomaly", False) and true_label:
                method_effectiveness[method]["true_positives"] += 1
        
        # Calculate precision per method
        method_precision = {}
        for method, stats in method_effectiveness.items():
            if stats["total"] > 0:
                # For methods that detected anomalies, calculate precision
                detected_anomalies = sum(
                    1 for r, t in zip(self.results, self.true_labels)
                    if r.get("detection_method") == method and r.get("final_is_anomaly", False)
                )
                
                true_detections = sum(
                    1 for r, t in zip(self.results, self.true_labels)
                    if r.get("detection_method") == method and 
                    r.get("final_is_anomaly", False) and t
                )
                
                precision = true_detections / detected_anomalies if detected_anomalies > 0 else 0
                method_precision[method] = precision
        
        return {
            "method_counts": method_counts,
            "method_effectiveness": method_effectiveness,
            "method_precision": method_precision
        }
    
    def _analyze_borderline_persistence(self) -> Dict[str, Any]:
        """Analyze borderline persistence effectiveness."""
        persistence_results = []
        
        for result, true_label in zip(self.results, self.true_labels):
            if result.get("model_persistence_triggered", False):
                persistence_results.append({
                    "was_correct": result.get("final_is_anomaly", False) and true_label,
                    "consecutive_windows": result.get("model_consecutive_borderline", 0),
                    "borderline_score": result.get("model_borderline_score"),
                    "true_label": true_label
                })
        
        if not persistence_results:
            return {"triggered_count": 0}
        
        # Calculate persistence effectiveness
        correct_count = sum(1 for r in persistence_results if r["was_correct"])
        total_count = len(persistence_results)
        
        # Analyze consecutive windows distribution
        consecutive_counts = {}
        for r in persistence_results:
            count = r["consecutive_windows"]
            consecutive_counts[count] = consecutive_counts.get(count, 0) + 1
        
        return {
            "triggered_count": total_count,
            "correct_count": correct_count,
            "accuracy": correct_count / total_count if total_count > 0 else 0,
            "consecutive_windows_distribution": consecutive_counts,
            "average_consecutive_windows": np.mean([r["consecutive_windows"] for r in persistence_results]),
            "average_borderline_score": np.mean([r["borderline_score"] for r in persistence_results if r["borderline_score"] is not None])
        }
    
    def generate_report(self, output_path: Optional[str] = None) -> str:
        """
        Generate comprehensive evaluation report.
        
        Args:
            output_path: Path to save report (optional)
            
        Returns:
            Report as string
        """
        # Ensure metrics are calculated
        if not self.metrics_summary:
            self.calculate_all_metrics()
        
        # Generate report sections
        report_parts = []
        
        # 1. Header
        report_parts.append("=" * 80)
        report_parts.append("ANOMALY DETECTION EVALUATION REPORT")
        report_parts.append("=" * 80)
        report_parts.append(f"Generated: {datetime.utcnow().isoformat()}")
        report_parts.append(f"Total Samples: {len(self.results)}")
        report_parts.append(f"True Anomalies: {sum(self.true_labels)}")
        report_parts.append("")
        
        # 2. Basic Metrics
        report_parts.append("BASIC CLASSIFICATION METRICS")
        report_parts.append("-" * 40)
        basic = self.metrics_summary.get("basic_metrics", {})
        for metric, value in basic.items():
            report_parts.append(f"{metric.replace('_', ' ').title()}: {value:.4f}")
        report_parts.append("")
        
        # 3. Confusion Matrix
        report_parts.append("CONFUSION MATRIX")
        report_parts.append("-" * 40)
        cm = self.metrics_summary.get("confusion_matrix", {})
        if cm:
            report_parts.append(f"True Negatives:  {cm.get('true_negative', 0)}")
            report_parts.append(f"False Positives: {cm.get('false_positive', 0)}")
            report_parts.append(f"False Negatives: {cm.get('false_negative', 0)}")
            report_parts.append(f"True Positives:  {cm.get('true_positive', 0)}")
        report_parts.append("")
        
        # 4. Per-Scenario Recall
        report_parts.append("PER-SCENARIO RECALL")
        report_parts.append("-" * 40)
        scenarios = self.metrics_summary.get("per_scenario_recall", {})
        for scenario, data in scenarios.items():
            report_parts.append(f"{scenario}: {data.get('recall', 0):.4f} "
                              f"({data.get('detected', 0)}/{data.get('samples', 0)} detected)")
        report_parts.append("")
        
        # 5. Latency Metrics
        report_parts.append("DETECTION LATENCY METRICS (ms)")
        report_parts.append("-" * 40)
        latency = self.metrics_summary.get("latency_metrics", {})
        for metric, value in latency.items():
            if metric != "sample_count":
                report_parts.append(f"{metric.replace('_', ' ').title()}: {value:.2f}")
        report_parts.append("")
        
        # 6. Throughput Metrics
        report_parts.append("THROUGHPUT METRICS")
        report_parts.append("-" * 40)
        throughput = self.metrics_summary.get("throughput_metrics", {})
        for metric, value in throughput.items():
            if metric not in ["first_timestamp", "last_timestamp"]:
                if "throughput" in metric:
                    report_parts.append(f"{metric.replace('_', ' ').title()}: {value:.2f}")
                else:
                    report_parts.append(f"{metric.replace('_', ' ').title()}: {value}")
        report_parts.append("")
        
        # 7. Detection Method Breakdown
        report_parts.append("DETECTION METHOD BREAKDOWN")
        report_parts.append("-" * 40)
        methods = self.metrics_summary.get("detection_method_breakdown", {})
        counts = methods.get("method_counts", {})
        for method, count in counts.items():
            percentage = (count / len(self.results)) * 100
            report_parts.append(f"{method}: {count} ({percentage:.1f}%)")
        report_parts.append("")
        
        # 8. Borderline Persistence Analysis
        report_parts.append("BORDERLINE PERSISTENCE ANALYSIS")
        report_parts.append("-" * 40)
        persistence = self.metrics_summary.get("borderline_persistence_analysis", {})
        if persistence.get("triggered_count", 0) > 0:
            report_parts.append(f"Triggered: {persistence.get('triggered_count')} times")
            report_parts.append(f"Accuracy: {persistence.get('accuracy', 0):.4f}")
            report_parts.append(f"Avg Consecutive Windows: {persistence.get('average_consecutive_windows', 0):.1f}")
        else:
            report_parts.append("Never triggered")
        report_parts.append("")
        
        # 9. ROC AUC
        report_parts.append("ROC ANALYSIS")
        report_parts.append("-" * 40)
        roc = self.metrics_summary.get("roc_auc", {})
        report_parts.append(f"AUC: {roc.get('auc', 0):.4f}")
        if roc.get('optimal_threshold'):
            report_parts.append(f"Optimal Threshold: {roc.get('optimal_threshold'):.4f}")
        report_parts.append("")
        
        # 10. Summary
        report_parts.append("SUMMARY")
        report_parts.append("-" * 40)
        f1 = basic.get("f1_score", 0)
        if f1 > 0.8:
            report_parts.append("Overall Performance: EXCELLENT")
        elif f1 > 0.6:
            report_parts.append("Overall Performance: GOOD")
        elif f1 > 0.4:
            report_parts.append("Overall Performance: FAIR")
        else:
            report_parts.append("Overall Performance: NEEDS IMPROVEMENT")
        
        # Check for data leakage warning
        if not self.test_data_only:
            report_parts.append("")
            report_parts.append("WARNING: Non-test data was used for evaluation!")
            report_parts.append("Metrics may be optimistic due to data leakage.")
        
        report = "\n".join(report_parts)
        
        # Save to file if path provided
        if output_path:
            with open(output_path, 'w') as f:
                f.write(report)
            print(f"Report saved to: {output_path}")
        
        return report
    
    def plot_confusion_matrix(self, save_path: Optional[str] = None):
        """Plot confusion matrix."""
        if not self.metrics_summary.get("confusion_matrix"):
            self.calculate_all_metrics()
        
        cm = self.metrics_summary["confusion_matrix"]
        if not cm:
            return
        
        # Create matrix for plotting
        matrix = np.array([
            [cm.get("true_negative", 0), cm.get("false_positive", 0)],
            [cm.get("false_negative", 0), cm.get("true_positive", 0)]
        ])
        
        plt.figure(figsize=(8, 6))
        sns.heatmap(matrix, annot=True, fmt='d', cmap='Blues',
                   xticklabels=['Normal', 'Anomaly'],
                   yticklabels=['Normal', 'Anomaly'])
        plt.title('Confusion Matrix')
        plt.ylabel('True Label')
        plt.xlabel('Predicted Label')
        
        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
            plt.close()
            print(f"Confusion matrix plot saved to: {save_path}")
        else:
            plt.show()
    
    def plot_roc_curve(self, save_path: Optional[str] = None):
        """Plot ROC curve."""
        if not self.roc_data:
            self.calculate_all_metrics()
        
        if not self.roc_data.get("fpr"):
            return
        
        plt.figure(figsize=(8, 6))
        plt.plot(self.roc_data["fpr"], self.roc_data["tpr"], 
                color='darkorange', lw=2, label=f'ROC curve (AUC = {self.metrics_summary["roc_auc"]["auc"]:.3f})')
        plt.plot([0, 1], [0, 1], color='navy', lw=2, linestyle='--', label='Random')
        plt.xlim([0.0, 1.0])
        plt.ylim([0.0, 1.05])
        plt.xlabel('False Positive Rate')
        plt.ylabel('True Positive Rate')
        plt.title('Receiver Operating Characteristic (ROC) Curve')
        plt.legend(loc="lower right")
        plt.grid(True, alpha=0.3)
        
        # Mark optimal threshold
        if self.roc_data.get("optimal_threshold"):
            optimal_idx = np.argmin(np.sqrt(
                np.array(self.roc_data["fpr"])**2 + 
                (1 - np.array(self.roc_data["tpr"]))**2
            ))
            plt.scatter(self.roc_data["fpr"][optimal_idx], 
                       self.roc_data["tpr"][optimal_idx],
                       color='red', s=100, zorder=5,
                       label=f'Optimal threshold = {self.roc_data["optimal_threshold"]:.3f}')
            plt.legend(loc="lower right")
        
        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
            plt.close()
            print(f"ROC curve plot saved to: {save_path}")
        else:
            plt.show()
    
    def save_metrics_json(self, output_path: str):
        """Save all metrics as JSON file."""
        if not self.metrics_summary:
            self.calculate_all_metrics()
        
        # Convert numpy types to Python types for JSON serialization
        def convert_to_serializable(obj):
            if isinstance(obj, (np.float32, np.float64)):
                return float(obj)
            elif isinstance(obj, (np.int32, np.int64)):
                return int(obj)
            elif isinstance(obj, np.ndarray):
                return obj.tolist()
            elif isinstance(obj, datetime):
                return obj.isoformat()
            elif isinstance(obj, dict):
                return {k: convert_to_serializable(v) for k, v in obj.items()}
            elif isinstance(obj, list):
                return [convert_to_serializable(item) for item in obj]
            else:
                return obj
        
        serializable_metrics = convert_to_serializable(self.metrics_summary)
        
        with open(output_path, 'w') as f:
            json.dump(serializable_metrics, f, indent=2)
        
        print(f"Metrics saved as JSON to: {output_path}")
        return output_path