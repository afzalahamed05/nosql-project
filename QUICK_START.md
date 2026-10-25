# Quick Start Guide

## 🚀 Get Started in 5 Minutes

### 1. Prerequisites Check
Make sure you have:
- Python 3.8+ (`python --version`)
- Node.js 16+ (`node --version`)
- MongoDB 5.0+ (running on port 27017)

### 2. One-Command Setup (Windows)
```powershell
# Run from project root directory
python verify_system.py
```

This will:
- Check all dependencies
- Start backend API (if not running)
- Generate test data
- Verify the complete system

### 3. Manual Setup

#### Backend (FastAPI)
```bash
# Install Python dependencies
pip install -r requirements.txt

# Start MongoDB (if not running)
net start MongoDB

# Start backend API
cd mongodb_anomaly_detection\api
python main.py
```

#### Frontend (React)
```bash
# Install Node.js dependencies
cd log-dashboard
npm install

# Start React development server
npm start
```

### 4. Access the System

- **React Dashboard**: http://localhost:3000
- **Backend API**: http://localhost:8000
- **API Documentation**: http://localhost:8000/docs

### 5. Test the System

1. Open the dashboard at http://localhost:3000
2. Select a service from the sidebar
3. View real-time charts and anomaly detection
4. Filter logs and anomalies using time ranges
5. Check the API documentation for integration

## 📊 Sample Data

The system includes:
- 500+ sample log entries across 3 services
- 20+ sample anomaly detections
- Rolling window features for charting
- Model versioning with performance metrics

## 🔧 Troubleshooting

### MongoDB Not Running
```powershell
# Start MongoDB service
net start MongoDB

# Or run manually
mongod --dbpath "C:\data\db"
```

### Python Dependencies Error
```bash
# Update pip
python -m pip install --upgrade pip

# Install requirements
pip install -r requirements.txt
```

### Node.js Dependencies Error
```bash
# Clear npm cache
npm cache clean --force

# Reinstall dependencies
cd log-dashboard
rm -rf node_modules package-lock.json
npm install
```

### Backend API Not Responding
1. Check if MongoDB is running
2. Verify port 8000 is not in use
3. Check Python dependencies are installed
4. Look for error messages in console

## 🎯 Next Steps

1. **Integrate Real Log Data**: Connect to your actual log sources
2. **Configure Detection Rules**: Customize thresholds for your environment
3. **Set Up Alerts**: Add notification system for anomalies
4. **Production Deployment**: Dockerize and deploy to cloud

## 📞 Need Help?

Check the full documentation in `README_COMPLETE.md` or run the verification script:
```bash
python verify_system.py
```