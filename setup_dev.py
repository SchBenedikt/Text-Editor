#!/usr/bin/env python3
"""
Development Setup Script for Text Editor
Run this once to set up your development environment securely.
"""

import os
import sys

def create_env_file():
    """Create .env file with prompts for credentials."""
    
    if os.path.exists('.env'):
        print("✅ .env file already exists!")
        return
    
    print("🔧 Setting up your development environment...")
    print("\n📋 You'll need GitHub OAuth credentials from:")
    print("   https://github.com/settings/applications/new")
    print("\n💡 For development, you can use these settings:")
    print("   Application name: Text Editor Dev")
    print("   Homepage URL: http://localhost:5000")
    print("   Authorization callback URL: http://127.0.0.1:5000/callback")
    
    # Get credentials from user
    print("\n" + "="*50)
    client_id = input("Enter your GitHub Client ID: ").strip()
    client_secret = input("Enter your GitHub Client Secret: ").strip()
    redirect_uri = input("Enter the Authorization callback URL (default: http://127.0.0.1:5000/callback): ").strip() or "http://127.0.0.1:5000/callback"
    
    # Generate a random secret key
    import secrets
    flask_secret = secrets.token_hex(32)
    
    # Create .env file
    env_content = f"""# GitHub OAuth Configuration
GITHUB_CLIENT_ID={client_id}
GITHUB_CLIENT_SECRET={client_secret}
OAUTH_REDIRECT_URI={redirect_uri}

# Flask Configuration  
FLASK_SECRET_KEY={flask_secret}
"""
    
    with open('.env', 'w') as f:
        f.write(env_content)
    
    print("\n✅ Created .env file successfully!")
    print("🔒 Your credentials are now secure and NOT in git history.")

def install_dependencies():
    """Install required dependencies."""
    print("\n📦 Installing dependencies...")
    os.system("pip install -r requirements.txt")

def main():
    print("🚀 Text Editor Development Setup")
    print("="*40)
    
    # Check if we're in the right directory
    if not os.path.exists('main.py'):
        print("❌ Please run this script from the Text-Editor directory")
        sys.exit(1)
    
    # Install dependencies
    install_dependencies()
    
    # Create environment file
    create_env_file()
    
    print("\n🎉 Setup complete! You can now run:")
    print("   python main.py")
    print("\n💡 Pro tip: Your credentials are secure in .env (which is git-ignored)")

if __name__ == "__main__":
    main() 