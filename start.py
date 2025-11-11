#!/usr/bin/env python3
"""
MediLab Analytics - Startup Script
This script helps you start the application easily
"""

import os
import sys
import subprocess
import webbrowser
import time
import threading
from pathlib import Path

def check_python_version():
    """Check if Python version is compatible"""
    if sys.version_info < (3, 8):
        print("❌ Error: Python 3.8 or higher is required")
        print(f"Current version: {sys.version}")
        sys.exit(1)
    print("✅ Python version compatible")

def check_dependencies():
    """Check if required packages are installed"""
    required_packages = [
        'flask',
        'flask_cors',
        'pandas',
        'pdfplumber',
        'reportlab'
    ]
    
    missing_packages = []
    for package in required_packages:
        try:
            __import__(package.replace('-', '_'))
        except ImportError:
            missing_packages.append(package)
    
    if missing_packages:
        print(f"❌ Missing packages: {', '.join(missing_packages)}")
        print("📦 Installing missing packages...")
        
        try:
            subprocess.check_call([sys.executable, '-m', 'pip', 'install', '-r', 'requirements.txt'])
            print("✅ Dependencies installed successfully")
        except subprocess.CalledProcessError:
            print("❌ Failed to install dependencies")
            print("Please run: pip install -r requirements.txt")
            sys.exit(1)
    else:
        print("✅ All dependencies are installed")

def setup_environment():
    """Set up the application environment"""
    # Create necessary directories
    directories = ['uploads', 'data', 'logs']
    for directory in directories:
        Path(directory).mkdir(exist_ok=True)
        print(f"📁 Created directory: {directory}")
    
    # Check if .env file exists
    if not Path('.env').exists():
        print("⚠️  .env file not found")
        print("📝 Creating sample .env file...")
        
        sample_env = """# Google Gemini API Configuration
GEMINI_API_KEY=your_gemini_api_key_here

# Flask Configuration
SECRET_KEY=your_secret_key_here_change_this_in_production
FLASK_ENV=development
FLASK_DEBUG=True

# Database Configuration
DATABASE_URL=sqlite:///medilab.db
"""
        
        with open('.env', 'w') as f:
            f.write(sample_env)
        print("✅ Sample .env file created")
        print("🔑 Please update the .env file with your actual API keys")

def start_flask_app():
    """Start the Flask backend application"""
    print("🚀 Starting Flask backend...")
    
    try:
        # Import and run the Flask app
        from api import app
        
        # Run in a separate thread to avoid blocking
        def run_app():
            app.run(host='0.0.0.0', port=5000, debug=False)
        
        flask_thread = threading.Thread(target=run_app, daemon=True)
        flask_thread.start()
        
        print("✅ Flask backend started on http://localhost:5000")
        return True
        
    except Exception as e:
        print(f"❌ Failed to start Flask app: {e}")
        return False

def open_browser():
    """Open the application in web browser"""
    time.sleep(2)  # Wait for Flask to start
    
    html_file = Path('index.html').absolute()
    if html_file.exists():
        print("🌐 Opening application in browser...")
        webbrowser.open(f'file://{html_file}')
        print("✅ Application opened successfully")
    else:
        print("❌ index.html not found")
        print("📁 Please ensure you're in the correct directory")

def display_menu():
    """Display startup menu"""
    print("\n" + "="*60)
    print("🏥 MediLab Analytics - Startup Menu")
    print("="*60)
    print("1. 🚀 Start Full Application (Backend + Frontend)")
    print("2. 🔧 Start Backend Only (API Server)")
    print("3. 🌐 Open Frontend Only (in browser)")
    print("4. 📦 Install Dependencies")
    print("5. 🧹 Reset/Clean Application")
    print("6. ❌ Exit")
    print("="*60)

def reset_application():
    """Reset the application (clean data)"""
    print("🧹 Cleaning application data...")
    
    # Remove data files
    data_files = ['users.json', 'timeline_data.json', 'medilab.db']
    for file in data_files:
        if Path(file).exists():
            Path(file).unlink()
            print(f"🗑️  Removed: {file}")
    
    # Clean upload directory
    upload_dir = Path('uploads')
    if upload_dir.exists():
        for file in upload_dir.glob('*'):
            file.unlink()
        print("🗑️  Cleaned uploads directory")
    
    print("✅ Application reset complete")

def main():
    """Main startup function"""
    print("🏥 MediLab Analytics - Starting Application...")
    print("="*50)
    
    try:
        # Initial checks
        check_python_version()
        check_dependencies()
        setup_environment()
        
        # Display menu
        while True:
            display_menu()
            choice = input("\nEnter your choice (1-6): ").strip()
            
            if choice == '1':
                print("\n🚀 Starting full application...")
                if start_flask_app():
                    open_browser()
                    print("\n✅ Application is running!")
                    print("🌐 Frontend: http://localhost:8000 (or open index.html)")
                    print("🔧 Backend API: http://localhost:5000")
                    print("\nPress Ctrl+C to stop the application")
                    
                    try:
                        # Keep the main thread alive
                        while True:
                            time.sleep(1)
                    except KeyboardInterrupt:
                        print("\n👋 Shutting down application...")
                        break
                else:
                    print("❌ Failed to start application")
                    
            elif choice == '2':
                print("\n🔧 Starting backend only...")
                if start_flask_app():
                    print("✅ Backend API running on http://localhost:5000")
                    print("\nPress Ctrl+C to stop the backend")
                    try:
                        while True:
                            time.sleep(1)
                    except KeyboardInterrupt:
                        print("\n👋 Shutting down backend...")
                        break
                
            elif choice == '3':
                print("\n🌐 Opening frontend...")
                open_browser()
                
            elif choice == '4':
                print("\n📦 Installing dependencies...")
                check_dependencies()
                
            elif choice == '5':
                confirm = input("Are you sure you want to reset the application? (y/N): ").strip().lower()
                if confirm == 'y':
                    reset_application()
                else:
                    print("❌ Reset cancelled")
                    
            elif choice == '6':
                print("👋 Goodbye!")
                break
                
            else:
                print("❌ Invalid choice. Please try again.")
                
    except KeyboardInterrupt:
        print("\n👋 Goodbye!")
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        print("Please check the logs and try again.")

if __name__ == '__main__':
    main()