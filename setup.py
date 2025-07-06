#!/usr/bin/env python3
"""
Setup script for Penny Stock Trading Application
"""

import os
import sys
import subprocess
import platform

def check_python_version():
    """Check if Python version is adequate"""
    version = sys.version_info
    if version.major < 3 or (version.major == 3 and version.minor < 8):
        print("❌ Python 3.8 or higher is required")
        print(f"Current version: {version.major}.{version.minor}.{version.micro}")
        return False
    print(f"✅ Python version {version.major}.{version.minor}.{version.micro} is compatible")
    return True

def install_requirements():
    """Install required packages"""
    print("📦 Installing required packages...")
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])
        print("✅ All packages installed successfully")
        return True
    except subprocess.CalledProcessError:
        print("❌ Failed to install packages")
        return False

def create_directories():
    """Create necessary directories"""
    print("📁 Creating directories...")
    directories = ["logs", "data", "backups"]
    for directory in directories:
        if not os.path.exists(directory):
            os.makedirs(directory)
            print(f"✅ Created directory: {directory}")
        else:
            print(f"📁 Directory exists: {directory}")

def initialize_database():
    """Initialize the database"""
    print("🗄️ Initializing database...")
    try:
        from database import init_db
        init_db()
        print("✅ Database initialized successfully")
        return True
    except Exception as e:
        print(f"❌ Database initialization failed: {str(e)}")
        return False

def run_tests():
    """Run basic tests"""
    print("🧪 Running basic tests...")
    try:
        # Test imports
        from config import Config
        from market_data import MarketDataService
        from risk_manager import RiskManager
        from trading_engine import TradingEngine
        
        print("✅ All imports successful")
        
        # Test basic functionality
        market_data = MarketDataService()
        risk_manager = RiskManager()
        trading_engine = TradingEngine()
        
        print("✅ Core components initialized successfully")
        return True
    except Exception as e:
        print(f"❌ Tests failed: {str(e)}")
        return False

def main():
    """Main setup function"""
    print("🚀 Penny Stock Trading Application Setup")
    print("=" * 50)
    
    # Check Python version
    if not check_python_version():
        sys.exit(1)
    
    # Install requirements
    if not install_requirements():
        sys.exit(1)
    
    # Create directories
    create_directories()
    
    # Initialize database
    if not initialize_database():
        sys.exit(1)
    
    # Run tests
    if not run_tests():
        sys.exit(1)
    
    print("\n🎉 Setup completed successfully!")
    print("=" * 50)
    print("Next steps:")
    print("1. Run the application: python main.py")
    print("2. Access dashboard at: http://localhost:8050")
    print("3. Or use CLI mode: python main.py --mode cli")
    print("=" * 50)

if __name__ == "__main__":
    main()