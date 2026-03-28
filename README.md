# 🌸 AniBloom

A desktop application that acts as a graphical user interface (GUI) for the terminal anime tool ani-cli. 

## ✨ Key Features
* **Watch History:** Automatically remembers your last-watched shows and exact episode numbers for a single click "Continue Watching" experience.
* **Smart Auto-Selector:** The backend intelligently ranks and selects the best available stream (prioritizing 1080p -> 720p -> standard mp4).
* **Dynamic Episode Grids:** Natively handles complex names; decimal episodes (e.g., Ep 12.5), and single-episode movies.
* **Batch Downloading:** Select multiple episodes at once and download them directly to your pc.

## ⚙️ Requirements
You must have these installed on your system and available in your PATH:
* `ani-cli` 
* `mpv` 
* `fzf` 
* A standard terminal (e.g., kitty, alacritty) for download progress.

## 🚀 Installation

1. Clone the repository:
   ```bash
   git clone [https://github.com/BloomPhobic/anibloom.git](https://github.com/BloomPhobic/anibloom.git)
   cd anibloom

2. Set-up:
   ```bash
   Run the automated setup script. This will install the Python dependencies and create a shortcut in your application launcher!
   ```bash
   chmod +x setup.sh
   ./setup.sh

3. Launch the software:
   Open your application launcher (rofi, wofi, GNOME Dash, etc.), search for AniBloom, and hit enter!
