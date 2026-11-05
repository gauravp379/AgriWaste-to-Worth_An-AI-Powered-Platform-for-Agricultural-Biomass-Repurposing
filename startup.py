#!/usr/bin/env python
"""
Startup Script - Run Full Project (Frontend + Backend)
Starts the unified Flask server on port 5000
"""

import os
import sys
import subprocess
import time
import webbrowser
from pathlib import Path

# Ensure UTF-8 output encoding for Windows terminals
if sys.stdout and hasattr(sys.stdout, 'reconfigure'):
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except Exception:
        pass
if sys.stderr and hasattr(sys.stderr, 'reconfigure'):
    try:
        sys.stderr.reconfigure(encoding='utf-8')
    except Exception:
        pass

# Load environment variables from .env
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

def check_dependencies():
    """Check if required packages are installed"""
    print("🔍 Checking dependencies...")
    
    required = {
        'flask': 'Flask',
        'pandas': 'pandas',
        'numpy': 'numpy',
        'tensorflow': 'tensorflow',
        'groq': 'groq',
        'gtts': 'gtts',
    }
    
    missing = []
    for import_name, package_name in required.items():
        try:
            __import__(import_name)
            print(f"  ✓ {package_name}")
        except ImportError:
            print(f"  ✗ {package_name} (MISSING)")
            missing.append(package_name)
    
    return missing

def install_missing_packages(packages):
    """Install missing packages"""
    if not packages:
        return True
    
    print(f"\n📦 Installing {len(packages)} missing packages...")
    
    try:
        subprocess.check_call([
            sys.executable, '-m', 'pip', 'install', 
            '--quiet', *packages
        ])
        print("✓ All packages installed successfully")
        return True
    except Exception as e:
        print(f"✗ Error installing packages: {e}")
        return False

def setup_env():
    """Setup environment variables"""
    # Set Flask environment
    os.environ['FLASK_APP'] = 'server.py'
    os.environ['FLASK_ENV'] = 'development'
    os.environ['FLASK_DEBUG'] = '1'
    
    # Set Groq API key if not already set
    if 'GROQ_API_KEY' not in os.environ:
        print("⚠️  GROQ_API_KEY is not set. Please set it as an environment variable.")
        print("   Example: set GROQ_API_KEY=your_key_here  (Windows)")
        print("            export GROQ_API_KEY=your_key_here  (Linux/Mac)")

def start_server():
    """Start the Flask server"""
    print("\n🚀 Starting Flask server...")
    print("="*60)
    
    try:
        # Run Flask server
        subprocess.run([sys.executable, 'server.py'])
    except KeyboardInterrupt:
        print("\n\n⏹️  Server stopped by user")
        sys.exit(0)
    except Exception as e:
        print(f"✗ Error starting server: {e}")
        sys.exit(1)

def main():
    """Main startup routine"""
    print("\n" + "="*60)
    print("🌾 AgriWaste to Worth - Full Project Startup")
    print("="*60)
    
    # Check Python version
    if sys.version_info < (3, 8):
        print("✗ Python 3.8+ required")
        sys.exit(1)
    
    print(f"✓ Python {sys.version.split()[0]}")
    
    # Check dependencies
    missing = check_dependencies()
    
    if missing:
        print(f"\n💿 Installing {len(missing)} missing package(s)...")
        if not install_missing_packages(missing):
            print("\n⚠️  Could not install all packages automatically")
            print("Try running: pip install " + " ".join(missing))
            sys.exit(1)
    else:
        print("\n✓ All dependencies are installed")
    
    # Setup environment
    setup_env()
    
    # Start server
    print("\n" + "="*60)
    print("📡 Starting Server...")
    print("="*60)
    print("\n✓ Server will start on http://localhost:5000")
    print("✓ Frontend: http://localhost:5000")
    print("✓ API: http://localhost:5000/api/")
    print("✓ Status: http://localhost:5000/api/status")
    print("\nPress Ctrl+C to stop the server")
    print("="*60 + "\n")
    
    # Small delay to give user time to read
    time.sleep(2)
    
    # Start the server
    start_server()

if __name__ == '__main__':
    main()
