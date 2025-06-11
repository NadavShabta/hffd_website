#!/usr/bin/env python3
"""
Algorithm Demonstration Website - Startup Script
Run this script to start the Flask development server
"""

import sys
import subprocess
import os

def check_requirements():
    """Check if required packages are installed"""
    try:
        import flask
        print("✓ Flask is installed")
        return True
    except ImportError:
        print("✗ Flask is not installed")
        print("Please run: pip install -r requirements.txt")
        return False

def main():
    print("=" * 50)
    print("Algorithm Demonstration Website")
    print("=" * 50)

    if not check_requirements():
        sys.exit(1)

    print("\nStarting Flask development server...")
    print("Access the website at: http://localhost:5000")
    print("Press Ctrl+C to stop the server")
    print("=" * 50)

    try:
        # Import and run the Flask app
        from app import app
        app.run(debug=True, host='0.0.0.0', port=5000)
    except KeyboardInterrupt:
        print("\n\nServer stopped. Goodbye!")
    except Exception as e:
        print(f"\nError starting server: {e}")
        print("Please check the requirements and try again.")

if __name__ == "__main__":
    main()