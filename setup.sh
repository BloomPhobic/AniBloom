#!/bin/bash

echo "🌸 Welcome to the AniBloom Installer 🌸"
echo "---------------------------------------"

# 1. Detect the Linux Distribution
if [ -f /etc/os-release ]; then
    . /etc/os-release
    OS=$ID
    OS_LIKE=$ID_LIKE
else
    OS="unknown"
    OS_LIKE="unknown"
fi

echo "🐧 Detected System: $OS"
echo "📦 Installing system dependencies (you may be asked for your password)..."

# 2. Install dependencies based on the distro
if [[ "$OS" == "arch" || "$OS" == "cachyos" || "$OS_LIKE" == *"arch"* ]]; then
    sudo pacman -S --needed mpv fzf ffmpeg yt-dlp tk python
elif [[ "$OS" == "ubuntu" || "$OS" == "debian" || "$OS_LIKE" == *"debian"* || "$OS_LIKE" == *"ubuntu"* ]]; then
    sudo apt-get update
    sudo apt-get install -y mpv fzf ffmpeg yt-dlp python3-tk python3-venv python3-pip
elif [[ "$OS" == "fedora" || "$OS_LIKE" == *"fedora"* ]]; then
    sudo dnf install -y mpv fzf ffmpeg yt-dlp python3-tkinter python3
else
    echo "⚠️ Could not auto-detect package manager. Please ensure mpv, fzf, ffmpeg, yt-dlp, and tk are installed."
fi

# 3. Check for ani-cli specifically (since it's not in standard repos for Ubuntu/Fedora)
if ! command -v ani-cli &> /dev/null; then
    echo "❌ ERROR: ani-cli is not installed on your system."
    echo "Please install it first: https://github.com/pystardust/ani-cli"
    exit 1
fi
echo "✅ All system dependencies found!"

# 4. Setup Python Virtual Environment
echo "📦 Setting up Python virtual environment..."
python3 -m venv venv
source venv/bin/activate

echo "📦 Installing Python libraries..."
pip install -r requirements.txt -q
echo "✅ Python libraries installed!"

# 5. Create Desktop Shortcut
echo "🖥️  Creating application shortcut..."
APP_DIR_PATH="$HOME/.local/share/applications"
mkdir -p "$APP_DIR_PATH"

DESKTOP_FILE="$APP_DIR_PATH/anibloom.desktop"
APP_DIR=$(pwd)

cat > "$DESKTOP_FILE" << EOF
[Desktop Entry]
Name=AniBloom
Comment=A modern GUI for ani-cli
Exec=bash -c "cd '$APP_DIR' && source venv/bin/activate && python main.py"
Icon=$APP_DIR/icon.png
Terminal=false
Type=Application
Categories=AudioVideo;Video;Player;
EOF

chmod +x "$DESKTOP_FILE"
# Force Linux to refresh the app menu so the shortcut appears immediately!
update-desktop-database "$APP_DIR_PATH" &> /dev/null

echo "✅ Desktop shortcut created!"

echo "---------------------------------------"
echo "✨ Installation Complete! You can now launch 'AniBloom' from your app launcher."
