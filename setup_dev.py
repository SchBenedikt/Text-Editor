#!/usr/bin/env python3
"""
Development Setup Script for Text Editor
Run this once to set up your development environment securely.
"""

import os
import sys

def create_env_file():
    """Create .env file for local configuration."""
    
    if os.path.exists('.env'):
        print("✅ .env file already exists! Skipping creation.")
        return
    
    print("🔧 Setting up your development environment...")

    # GitHub credentials are now hardcoded in auth.py.
    
    # Get Ollama config from user
    print("\n" + "="*50)
    print("Ollama is used for local AI features.")
    ollama_host = input("Enter your Ollama Host URL (default: http://localhost:11434): ").strip() or "http://localhost:11434"
    ollama_model = input("Enter the default Ollama model to use (default: llama3): ").strip() or "llama3"

    # Generate a random secret key for Flask
    import secrets
    flask_secret = secrets.token_hex(32)
    
    # Create .env file
    env_content = f"""# Flask Configuration  
FLASK_SECRET_KEY={flask_secret}

# Ollama Configuration
OLLAMA_HOST={ollama_host}
OLLAMA_MODEL={ollama_model}
"""
    
    with open('.env', 'w') as f:
        f.write(env_content)
    
    print("\n✅ Created .env file successfully!")
    print("🔒 Your GitHub credentials are now hardcoded in auth.py. This is a security risk.")

def install_dependencies():
    """Install required dependencies from requirements.txt."""
    print("\n📦 Installing/updating dependencies...")
    # Use --upgrade to ensure all packages are at the versions specified.
    os.system(f"{sys.executable} -m pip install -r requirements.txt --upgrade")

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
    print("\n💡 Pro tip: For better security, consider moving the hardcoded GitHub credentials from auth.py to the .env file.")

if __name__ == "__main__":
    main() 