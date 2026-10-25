#!/usr/bin/env python3
"""
Script to run the FastAPI backend server.
"""

import os
import sys

# Add the project root to Python path
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_root)
sys.path.insert(0, os.path.join(project_root, "mongodb_anomaly_detection"))

# Now import and run the main module
if __name__ == "__main__":
    import uvicorn
    from mongodb_anomaly_detection.api.main import app
    
    print("Starting FastAPI backend server...")
    print("API will be available at: http://localhost:8000")
    print("API documentation: http://localhost:8000/docs")
    
    uvicorn.run(app, host="0.0.0.0", port=8000)