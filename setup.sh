```bash
#!/bin/bash

echo "🌸 Welcome to the AniBloom Installer 🌸"
echo "---------------------------------------"

# 1. Check dependencies
for req in ani-cli mpv fzf; do
    if ! command -v $req &> /dev/null; then
        echo "❌ ERROR: $req is not installed. Please install it first."
        exit 1
    fi
done
echo "✅ All system dependencies found!"

# 2. Setup Python Virtual Environment
echo "📦 Setting up Python virtual environment..."
python3 -m venv venv
source venv/bin/activate

echo "📦 Installing Python libraries..."
pip install -r requirements.txt -q
echo "✅ Python libraries installed!"

# 3. Create Desktop Shortcut
echo "🖥️  Creating application shortcut..."
DESKTOP_FILE="$HOME/.local/share/applications/anibloom.desktop"
APP_DIR=$(pwd)

cat > "$DESKTOP_FILE" << EOF
[Desktop Entry]
Version=1.0
Name=AniBloom
Comment=A modern GUI for ani-cli
Exec=bash -c "cd $APP_DIR && source venv/bin/activate && python main.py"
Icon=mpv
Terminal=false
Type=Application
Categories=AudioVideo;Video;Player;
EOF

chmod +x "$DESKTOP_FILE"
echo "✅ Desktop shortcut created!"

echo "---------------------------------------"
echo "✨ Installation Complete! You can now launch 'AniBloom' from your app launcher."
