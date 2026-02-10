"""
Quick verification script to check if all required packages are available.
Run this after: pip install -r requirements.txt
"""

import sys

def check_imports():
    """Check if all required packages can be imported."""
    required_packages = {
        'flask': 'Flask',
        'flask_sqlalchemy': 'Flask-SQLAlchemy', 
        'flask_login': 'Flask-Login',
        'flask_wtf': 'Flask-WTF',
        'wtforms': 'WTForms',
        'werkzeug.security': 'Werkzeug (comes with Flask)'
    }
    
    print("=" * 60)
    print("Checking Flask App Dependencies")
    print("=" * 60)
    
    all_ok = True
    for package, display_name in required_packages.items():
        try:
            __import__(package)
            print(f"✓ {display_name:30} - OK")
        except ImportError:
            print(f"✗ {display_name:30} - MISSING")
            all_ok = False
    
    print("=" * 60)
    
    if all_ok:
        print("✓ All dependencies installed! Ready to run: python app.py")
        return 0
    else:
        print("✗ Some dependencies missing. Run: pip install -r requirements.txt")
        return 1

if __name__ == '__main__':
    sys.exit(check_imports())
