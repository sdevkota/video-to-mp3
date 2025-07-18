#!/bin/bash

# Streamlit Cloud Deployment Script

echo "🚀 Preparing for Streamlit Cloud deployment..."

# Check if git is initialized
if [ ! -d ".git" ]; then
    echo "📋 Initializing git repository..."
    git init
fi

# Create .gitignore if it doesn't exist
if [ ! -f ".gitignore" ]; then
    echo "📝 Creating .gitignore..."
    cat > .gitignore << EOF
# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
build/
develop-eggs/
dist/
downloads/
eggs/
.eggs/
lib/
lib64/
parts/
sdist/
var/
wheels/
share/python-wheels/
*.egg-info/
.installed.cfg
*.egg
MANIFEST

# Virtual environments
venv/
env/
ENV/

# IDE
.vscode/
.idea/
*.swp
*.swo
*~

# OS
.DS_Store
Thumbs.db

# Logs
*.log

# Temporary files
*.tmp
*.temp
EOF
fi

# Add all files
echo "📁 Adding files to git..."
git add .

# Commit changes
echo "💾 Committing changes..."
git commit -m "Prepare for Streamlit Cloud deployment"

echo "✅ Repository prepared for Streamlit Cloud!"
echo ""
echo "📋 Next steps:"
echo "1. Push this repository to GitHub:"
echo "   git remote add origin https://github.com/username/video-to-mp3.git"
echo "   git push -u origin main"
echo ""
echo "2. Go to https://share.streamlit.io/"
echo "3. Connect your GitHub account"
echo "4. Select your repository"
echo "5. Set main file to: app.py"
echo "6. Deploy!"
echo ""
echo "⚠️  Note: Streamlit Cloud may have limitations with ffmpeg."
echo "   Consider using Google Cloud Run for better compatibility."
