#!/bin/bash

echo "🌸 Welcome to the AniBloom Installer 🌸"
echo "---------------------------------------"

for req in ani-cli mpv fzf; do
    if ! command -v $req &> /dev/null; then
        echo "❌ ERROR: $req is not installed. Please install it first."
        exit 1
    fi
done
echo "✅ All system dependencies found!"

echo "📦 Setting up Python virtual environment..."
python3 -m venv venv
source venv/bin/activate

echo "📦 Installing Python libraries..."
pip install -r requirements.txt -q
echo "✅ Python libraries installed!"

echo "🖥️  Creating application shortcut..."
APP_DIR_PATH="$HOME/.local/share/applications"
mkdir -p "$APP_DIR_PATH"

DESKTOP_FILE="$APP_DIR_PATH/anibloom.desktop"
APP_DIR=$(pwd)

cat > "$DESKTOP_FILE" << EOF
[Desktop Entry]
Name=AniBloom
Comment=A modern GUI for ani-cli
Exec=bash -c "cd $APP_DIR && source venv/bin/activate && python main.py"
Icon=$INSTALL_DIR/icon.png
Terminal=false
Type=Application
Categories=AudioVideo;Video;Player;
EOF

chmod +x "$DESKTOP_FILE"
echo "✅ Desktop shortcut created!"

echo "---------------------------------------"
echo "✨ Installation Complete! You can now launch 'AniBloom' from your app launcher."
