"""
Test script for the backend API endpoints.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import asyncio
from datetime import datetime, timedelta
import random
import requests
import time

# Test configuration
BASE_URL = "http://localhost:8000"
TEST_SERVICE = "test-service"


def test_health_check():
    """Test health check endpoint."""
    print("Testing health check...")
    response = requests.get(f"{BASE_URL}/api/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    print("✓ Health check passed")
    return True


def test_summary_endpoint():
    """Test summary endpoint."""
    print("\nTesting summary endpoint...")
    response = requests.get(f"{BASE_URL}/api/summary")
    assert response.status_code == 200
    data = response.json()
    
    # Check required fields
    assert "total_logs" in data
    assert "total_anomalies" in data
    assert "services" in data
    assert "time_range" in data
    assert "anomaly_rate" in data
    
    print(f"  Total logs: {data['total_logs']}")
    print(f"  Total anomalies: {data['total_anomalies']}")
    print(f"  Services: {len(data['services'])}")
    print("✓ Summary endpoint passed")
    return True


def test_services_endpoint():
    """Test services endpoint."""
    print("\nTesting services endpoint...")
    response = requests.get(f"{BASE_URL}/api/services")
    assert response.status_code == 200
    services = response.json()
    assert isinstance(services, list)
    print(f"  Found {len(services)} services")
    print("✓ Services endpoint passed")
    return True


def test_service_details_endpoint():
    """Test service details endpoint."""
    print("\nTesting service details endpoint...")
    
    # First get list of services
    response = requests.get(f"{BASE_URL}/api/services")
    services = response.json()
    
    if services:
        # Test first service
        service_name = services[0]
        response = requests.get(f"{BASE_URL}/api/services/{service_name}")
        
        if response.status_code == 200:
            data = response.json()
            assert data["service_name"] == service_name
            assert "total_logs" in data
            assert "total_anomalies" in data
            print(f"  Service details for '{service_name}':")
            print(f"    Logs: {data['total_logs']}")
            print(f"    Anomalies: {data['total_anomalies']}")
            print("✓ Service details endpoint passed")
            return True
        elif response.status_code == 404:
            print(f"  Service '{service_name}' not found (may have no data)")
            return True
    else:
        print("  No services found to test")
        return True
    
    print("✗ Service details endpoint failed")
    return False


def test_logs_endpoint():
    """Test logs endpoint with pagination."""
    print("\nTesting logs endpoint...")
    
    # Test without filters
    response = requests.get(f"{BASE_URL}/api/logs", params={"page": 1, "page_size": 10})
    assert response.status_code == 200
    data = response.json()
    
    assert "data" in data
    assert "total" in data
    assert "page" in data
    assert "page_size" in data
    assert "total_pages" in data
    
    print(f"  Logs: page {data['page']} of {data['total_pages']}")
    print(f"  Total logs: {data['total']}")
    print("✓ Logs endpoint passed")
    return True


def test_anomalies_endpoint():
    """Test anomalies endpoint."""
    print("\nTesting anomalies endpoint...")
    
    response = requests.get(f"{BASE_URL}/api/anomalies", params={"page": 1, "page_size": 10})
    assert response.status_code == 200
    data = response.json()
    
    assert "data" in data
    assert "total" in data
    
    print(f"  Anomalies: {data['total']} total")
    print(f"  Page data: {len(data['data'])} items")
    print("✓ Anomalies endpoint passed")
    return True


def test_model_versions_endpoint():
    """Test model versions endpoint."""
    print("\nTesting model versions endpoint...")
    
    response = requests.get(f"{BASE_URL}/api/model/versions")
    assert response.status_code == 200
    versions = response.json()
    assert isinstance(versions, list)
    
    print(f"  Model versions: {len(versions)}")
    if versions:
        print(f"  Latest version: {versions[0].get('version', 'N/A')}")
    print("✓ Model versions endpoint passed")
    return True


def test_rules_endpoint():
    """Test rules endpoint."""
    print("\nTesting rules endpoint...")
    
    response = requests.get(f"{BASE_URL}/api/rules")
    assert response.status_code == 200
    rules = response.json()
    assert isinstance(rules, list)
    
    print(f"  Detection rules: {len(rules)}")
    print("✓ Rules endpoint passed")
    return True


def test_window_metrics_endpoint():
    """Test window metrics endpoint."""
    print("\nTesting window metrics endpoint...")
    
    response = requests.get(f"{BASE_URL}/api/metrics/window", params={"hours": 24})
    assert response.status_code == 200
    windows = response.json()
    assert isinstance(windows, list)
    
    print(f"  Window metrics: {len(windows)} windows")
    print("✓ Window metrics endpoint passed")
    return True


def test_invalid_endpoints():
    """Test error handling for invalid endpoints."""
    print("\nTesting error handling...")
    
    # Test invalid service
    response = requests.get(f"{BASE_URL}/api/services/nonexistent-service-12345")
    assert response.status_code == 404
    
    # Test invalid page
    response = requests.get(f"{BASE_URL}/api/logs", params={"page": -1})
    assert response.status_code == 422  # Validation error
    
    print("✓ Error handling passed")
    return True


def run_all_tests():
    """Run all API tests."""
    print("=" * 80)
    print("STARTING BACKEND API TESTS")
    print("=" * 80)
    
    tests = [
        test_health_check,
        test_summary_endpoint,
        test_services_endpoint,
        test_service_details_endpoint,
        test_logs_endpoint,
        test_anomalies_endpoint,
        test_model_versions_endpoint,
        test_rules_endpoint,
        test_window_metrics_endpoint,
        test_invalid_endpoints,
    ]
    
    passed = 0
    failed = 0
    
    for test in tests:
        try:
            if test():
                passed += 1
            else:
                failed += 1
        except Exception as e:
            print(f"✗ {test.__name__} failed with error: {e}")
            failed += 1
    
    print("\n" + "=" * 80)
    print("TEST RESULTS")
    print("=" * 80)
    print(f"Passed: {passed}/{len(tests)}")
    print(f"Failed: {failed}/{len(tests)}")
    
    if failed == 0:
        print("\n✓ All backend API tests passed!")
        return True
    else:
        print(f"\n✗ {failed} test(s) failed")
        return False


def generate_test_data():
    """Generate some test data for the API."""
    print("\nGenerating test data...")
    
    from mongodb_anomaly_detection.config.database import init_database, get_db
    from mongodb_anomaly_detection.models.log_schema import LogEntry
    from datetime import datetime, timedelta
    import random
    
    # Initialize database
    init_database()
    db = get_db()
    
    # Generate some test logs
    services = ["auth-service", "payment-service", "inventory-service", "user-service"]
    log_levels = ["INFO", "WARNING", "ERROR", "DEBUG"]
    endpoints = ["/api/login", "/api/payment", "/api/products", "/api/users", "/api/health"]
    
    num_logs = 100
    base_time = datetime.utcnow() - timedelta(hours=24)
    
    print(f"Generating {num_logs} test log entries...")
    
    for i in range(num_logs):
        log = LogEntry(
            timestamp=base_time + timedelta(minutes=i*5),
            service_name=random.choice(services),
            log_level=random.choice(log_levels),
            message=f"Test log entry {i}",
            endpoint=random.choice(endpoints),
            response_time_ms=random.uniform(50, 500),
            status_code=random.choice([200, 201, 400, 404, 500]),
            metadata={"test": True, "iteration": i}
        )
        
        db["log_entries"].insert_one(log.dict(by_alias=True))
    
    print(f"Generated {num_logs} test log entries")
    
    # Generate some test anomalies
    print("Generating test anomaly results...")
    
    for i in range(10):
        anomaly = {
            "timestamp": datetime.utcnow() - timedelta(hours=random.randint(0, 23)),
            "service_name": random.choice(services),
            "detection_method": random.choice(["rule_only", "model_only", "hybrid"]),
            "is_anomaly": True,
            "confidence": random.uniform(0.7, 0.95),
            "rule_violations": [f"test_rule_{j}" for j in range(random.randint(1, 3))],
            "metadata": {"test": True}
        }
        
        db["anomaly_results"].insert_one(anomaly)
    
    print("Generated test anomaly results")
    
    return True


if __name__ == "__main__":
    # Check if API is running
    print("Checking if backend API is running...")
    try:
        response = requests.get(f"{BASE_URL}/api/health", timeout=5)
        if response.status_code == 200:
            print("Backend API is running")
            
            # Generate test data if needed
            generate_test_data()
            
            # Run tests
            success = run_all_tests()
            
            if success:
                print("\nBackend API verification complete!")
                print("All endpoints are functioning correctly.")
            else:
                print("\nBackend API verification failed!")
                sys.exit(1)
        else:
            print(f"API health check failed with status {response.status_code}")
            sys.exit(1)
    except requests.ConnectionError:
        print(f"Cannot connect to backend API at {BASE_URL}")
        print("Please start the backend server first:")
        print("  cd mongodb_anomaly_detection/api")
        print("  python main.py")
        sys.exit(1)
    except Exception as e:
        print(f"Error during testing: {e}")
        sys.exit(1)