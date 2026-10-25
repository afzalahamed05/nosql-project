#!/usr/bin/env python3
"""
Verification script for the complete Log Anomaly Detection System.
Tests both backend API and frontend integration.
"""

import sys
import os
import subprocess
import time
import requests
import webbrowser
from datetime import datetime

def print_header(text):
    """Print formatted header."""
    print("\n" + "="*80)
    print(f" {text}")
    print("="*80)

def print_success(text):
    """Print success message."""
    print(f"✓ {text}")

def print_error(text):
    """Print error message."""
    print(f"✗ {text}")

def print_info(text):
    """Print info message."""
    print(f"  {text}")

def check_mongodb():
    """Check if MongoDB is running."""
    print_header("CHECKING MONGODB")
    
    try:
        import pymongo
        client = pymongo.MongoClient("mongodb://localhost:27017/", serverSelectionTimeoutMS=2000)
        client.admin.command('ping')
        print_success("MongoDB is running")
        return True
    except Exception as e:
        print_error(f"MongoDB connection failed: {e}")
        print_info("Please start MongoDB:")
        print_info("  Windows: net start MongoDB")
        print_info("  Linux/Mac: sudo systemctl start mongod")
        return False

def check_python_dependencies():
    """Check Python dependencies."""
    print_header("CHECKING PYTHON DEPENDENCIES")
    
    required_packages = [
        'fastapi', 'uvicorn', 'pymongo', 'pydantic',
        'scikit-learn', 'numpy', 'pandas'
    ]
    
    missing = []
    for package in required_packages:
        try:
            __import__(package.replace('-', '_'))
            print_success(f"{package} installed")
        except ImportError:
            missing.append(package)
            print_error(f"{package} not installed")
    
    if missing:
        print_info("\nInstall missing dependencies:")
        print_info(f"  pip install {' '.join(missing)}")
        return False
    
    return True

def start_backend():
    """Start the backend API server."""
    print_header("STARTING BACKEND API")
    
    backend_dir = os.path.join(os.path.dirname(__file__), "mongodb_anomaly_detection", "api")
    
    if not os.path.exists(os.path.join(backend_dir, "main.py")):
        print_error("Backend API not found")
        return None
    
    print_info("Starting FastAPI server on http://localhost:8000")
    
    # In a real implementation, we would start the server in a subprocess
    # For now, we'll check if it's already running
    try:
        response = requests.get("http://localhost:8000/api/health", timeout=5)
        if response.status_code == 200:
            print_success("Backend API is already running")
            return True
    except requests.ConnectionError:
        print_info("Backend API not running. Please start it manually:")
        print_info(f"  cd {backend_dir}")
        print_info("  python main.py")
        return False
    
    return True

def check_backend_api():
    """Check backend API endpoints."""
    print_header("TESTING BACKEND API ENDPOINTS")
    
    endpoints = [
        ("/api/health", "Health check"),
        ("/api/summary", "Summary endpoint"),
        ("/api/services", "Services list"),
        ("/api/logs?page_size=5", "Logs endpoint"),
        ("/api/anomalies?page_size=5", "Anomalies endpoint"),
        ("/api/rules", "Rules endpoint"),
        ("/api/model/versions", "Model versions"),
    ]
    
    all_ok = True
    for endpoint, description in endpoints:
        try:
            response = requests.get(f"http://localhost:8000{endpoint}", timeout=5)
            if response.status_code == 200:
                print_success(f"{description}: OK")
            else:
                print_error(f"{description}: HTTP {response.status_code}")
                all_ok = False
        except Exception as e:
            print_error(f"{description}: {e}")
            all_ok = False
    
    return all_ok

def check_frontend():
    """Check frontend setup."""
    print_header("CHECKING FRONTEND SETUP")
    
    frontend_dir = os.path.join(os.path.dirname(__file__), "log-dashboard")
    
    # Check if React app exists
    if not os.path.exists(os.path.join(frontend_dir, "package.json")):
        print_error("React frontend not found")
        return False
    
    # Check if node_modules exists
    if not os.path.exists(os.path.join(frontend_dir, "node_modules")):
        print_info("Node.js dependencies not installed")
        print_info(f"  cd {frontend_dir}")
        print_info("  npm install")
        return False
    
    print_success("React frontend setup complete")
    
    # Check if React dev server is running
    try:
        response = requests.get("http://localhost:3000", timeout=5)
        if response.status_code == 200:
            print_success("React dev server is already running")
            return True
    except requests.ConnectionError:
        print_info("React dev server not running. Please start it:")
        print_info(f"  cd {frontend_dir}")
        print_info("  npm start")
        return False
    
    return True

def generate_test_data():
    """Generate test data for the system."""
    print_header("GENERATING TEST DATA")
    
    try:
        from mongodb_anomaly_detection.config.database import init_database, get_db
        from mongodb_anomaly_detection.models.log_schema import LogEntry
        from datetime import datetime, timedelta
        import random
        
        # Initialize database
        if init_database():
            db = get_db()
            
            # Generate some test logs
            services = ["auth-service", "payment-service", "inventory-service"]
            log_levels = ["INFO", "WARNING", "ERROR"]
            
            num_logs = 500
            base_time = datetime.utcnow() - timedelta(hours=24)
            
            logs_generated = 0
            for i in range(num_logs):
                log = LogEntry(
                    timestamp=base_time + timedelta(minutes=i*2),
                    service_name=random.choice(services),
                    log_level=random.choice(log_levels),
                    message=f"Test log entry {i} for system verification",
                    endpoint=random.choice(["/api/login", "/api/payment", "/api/products"]),
                    response_time_ms=random.uniform(50, 1000),
                    status_code=random.choice([200, 201, 400, 404, 500]),
                    metadata={"test": True, "verification": "system_test"}
                )
                
                db["log_entries"].insert_one(log.dict(by_alias=True))
                logs_generated += 1
            
            print_success(f"Generated {logs_generated} test log entries")
            
            # Generate some test anomalies
            for i in range(20):
                anomaly = {
                    "timestamp": datetime.utcnow() - timedelta(hours=random.randint(0, 23)),
                    "service_name": random.choice(services),
                    "detection_method": random.choice(["rule_only", "model_only", "hybrid"]),
                    "is_anomaly": True,
                    "confidence": random.uniform(0.7, 0.95),
                    "rule_violations": [f"test_rule_{j}" for j in range(random.randint(1, 3))],
                    "metadata": {"test": True, "verification": "system_test"}
                }
                
                db["anomaly_results"].insert_one(anomaly)
            
            print_success("Generated test anomaly results")
            
            return True
        else:
            print_error("Failed to initialize database")
            return False
            
    except Exception as e:
        print_error(f"Error generating test data: {e}")
        return False

def run_comprehensive_test():
    """Run comprehensive system test."""
    print_header("COMPREHENSIVE SYSTEM TEST")
    
    tests = [
        ("MongoDB", check_mongodb),
        ("Python Dependencies", check_python_dependencies),
        ("Backend API", start_backend),
        ("API Endpoints", check_backend_api),
        ("Frontend Setup", check_frontend),
        ("Test Data", generate_test_data),
    ]
    
    results = []
    for test_name, test_func in tests:
        print(f"\n{test_name}:")
        try:
            result = test_func()
            results.append((test_name, result))
            if result:
                print_success(f"{test_name} passed")
            else:
                print_error(f"{test_name} failed")
        except Exception as e:
            print_error(f"{test_name} error: {e}")
            results.append((test_name, False))
    
    # Print summary
    print_header("TEST SUMMARY")
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    print(f"\nTests passed: {passed}/{total}")
    
    for test_name, result in results:
        status = "✓ PASS" if result else "✗ FAIL"
        print(f"  {test_name:25} {status}")
    
    if passed == total:
        print_success("\nAll tests passed! System is ready.")
        print("\nAccess the system at:")
        print("  Backend API: http://localhost:8000")
        print("  React Dashboard: http://localhost:3000")
        print("\nAPI Documentation: http://localhost:8000/docs")
        
        # Offer to open dashboard in browser
        try:
            response = input("\nOpen dashboard in browser? (y/n): ")
            if response.lower() == 'y':
                webbrowser.open("http://localhost:3000")
        except:
            pass
            
        return True
    else:
        print_error("\nSome tests failed. Please fix the issues above.")
        return False

def main():
    """Main verification function."""
    print_header("LOG ANOMALY DETECTION SYSTEM VERIFICATION")
    print(f"Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    try:
        success = run_comprehensive_test()
        return 0 if success else 1
    except KeyboardInterrupt:
        print("\n\nVerification interrupted by user")
        return 1
    except Exception as e:
        print_error(f"Verification failed with error: {e}")
        return 1

if __name__ == "__main__":
    sys.exit(main())