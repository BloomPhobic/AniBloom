import subprocess
import os
import re
import shutil
import json
import platform
from pathlib import Path

HISTORY_FILE = "watch_history.json"


SETTINGS_FILE = "settings.json"
DOWNLOADS_DATA_FILE = "downloads.json"

def get_default_download_dir():
    # Automatically finds the true ~/Downloads folder on Linux/Mac/Windows
    return str(Path.home() / "Downloads")

def load_settings():
    default_settings = {
        "preferred_quality": "1080p",
        "download_path": get_default_download_dir()
    }
    if not os.path.exists(SETTINGS_FILE):
        return default_settings
    try:
        with open(SETTINGS_FILE, "r") as f:
            data = json.load(f)
            return {**default_settings, **data} # Merges defaults in case keys are missing
    except Exception:
        return default_settings

def save_settings(quality, path):
    settings = {
        "preferred_quality": quality,
        "download_path": path
    }
    with open(SETTINGS_FILE, "w") as f:
        json.dump(settings, f, indent=4)

def load_downloads_data():
    if not os.path.exists(DOWNLOADS_DATA_FILE):
        return []
    try:
        with open(DOWNLOADS_DATA_FILE, "r") as f:
            return json.load(f)
    except Exception:
        return []

def save_download_data(anime_name, episode, folder_path):
    downloads = load_downloads_data()
    downloads.insert(0, {
        "name": anime_name,
        "episode": str(episode),
        "folder_path": folder_path
    })
    with open(DOWNLOADS_DATA_FILE, "w") as f:
        json.dump(downloads, f, indent=4)

def clear_downloads_data():
    if os.path.exists(DOWNLOADS_DATA_FILE):
        with open(DOWNLOADS_DATA_FILE, "w") as f:
            json.dump([], f)

def open_file_manager(path):
    """Safely opens the system's native file manager."""
    try:
        if platform.system() == "Windows":
            os.startfile(path)
        elif platform.system() == "Darwin":
            subprocess.Popen(["open", path])
        else: # Linux
            subprocess.Popen(["xdg-open", path])
    except Exception as e:
        print(f"Failed to open file manager: {e}")

def clean_anime_title(raw_title):
    clean = re.sub(r'\[\d+[^\]]*\]|\(\d+[^\)]*\)', '', raw_title)
    clean = " ".join(clean.split())
    return clean

def search_anime_cli(query):
    if not query:
        return False, "Query cannot be empty."

    # --- THE INVINCIBLE TRAP ---
    trap_script = "#!/bin/sh\ncat > .ani_results.tmp\nexit 1\n"
    for tool in ["fzf", "rofi", "dmenu", "wofi"]:
        with open(tool, "w") as f:
            f.write(trap_script)
        os.chmod(tool, 0o755)

    my_env = os.environ.copy()
    my_env["PATH"] = f"{os.getcwd()}:{my_env.get('PATH', '')}"
    my_env["TERM"] = "xterm-256color"

    try:
        subprocess.run(["ani-cli", query], env=my_env, capture_output=True)

        if os.path.exists(".ani_results.tmp"):
            with open(".ani_results.tmp", "r") as f:
                raw_lines = f.readlines()
            
            results = []
            for line in raw_lines:
                if line.strip():
                    clean_line = re.sub(r'\x1b\[[0-9;]*[a-zA-Z]', '', line.strip())
                    clean_line = re.sub(r'^[^a-zA-Z0-9]*\d+[\.\)\]]?\s*', '', clean_line)
                    results.append(clean_line)
            
            os.remove(".ani_results.tmp")
            
            if results:
                return True, results
            else:
                return False, "No shows found for that query."
        else:
            return False, "Failed to trap search results."
            
    except Exception as e:
        return False, f"System Error: {str(e)}"
    finally:
        # Clean up all the fake tools
        for tool in ["fzf", "rofi", "dmenu", "wofi"]:
            if os.path.exists(tool):
                os.remove(tool)

def get_episode_count_cli(query, index):
    trap_script = "#!/bin/sh\ncat > .ani_results.tmp\nexit 1\n"
    for tool in ["fzf", "rofi", "dmenu", "wofi"]:
        with open(tool, "w") as f:
            f.write(trap_script)
        os.chmod(tool, 0o755)

    my_env = os.environ.copy()
    my_env["PATH"] = f"{os.getcwd()}:{my_env.get('PATH', '')}"
    my_env["TERM"] = "xterm-256color"

    try:
        subprocess.run(["ani-cli", query, "-S", str(index)], env=my_env, capture_output=True)

        if os.path.exists(".ani_results.tmp"):
            with open(".ani_results.tmp", "r") as f:
                raw_lines = f.readlines()
            os.remove(".ani_results.tmp")

            valid_lines = [line.strip() for line in raw_lines if line.strip()]
            
            if valid_lines:
                first_line = valid_lines[0].lower()
                
                if "http" in first_line or ">" in first_line:
                    return True, ["1"]
                
                episodes = []
                for line in valid_lines:
                    clean = re.sub(r'\x1b\[[0-9;]*[a-zA-Z]', '', line).strip()
                    match = re.search(r'\d+(\.\d+)?', clean)
                    if match:
                        episodes.append(match.group())
                
                episodes = list(set(episodes))
                try:
                    episodes.sort(key=float)
                except ValueError:
                    episodes.sort()
                    
                if episodes:
                    return True, episodes
                else:
                    return False, []
            else:
                return False, []
        else:
            return True, ["1"]

    except Exception as e:
        return False, []
    finally:
        for tool in ["fzf", "rofi", "dmenu", "wofi"]:
            if os.path.exists(tool):
                os.remove(tool)

def get_video_url_cli(query, index, episode):
    try:
        command = ["ani-cli", query, "-S", str(index), "-e", str(episode)]
        my_env = os.environ.copy()
        my_env["ANI_CLI_PLAYER"] = "debug"

        process = subprocess.run(command, env=my_env, capture_output=True, text=True)
        
        if process.returncode == 0:
            raw_text = process.stdout
            clean_text = re.sub(r'\x1b\[[0-9;]*[a-zA-Z]', '', raw_text)
            
            options = {}
            for line in clean_text.splitlines():
                if ">http" in line:
                    parts = line.split(">", 1)
                    name = parts[0].strip()
                    url = parts[1].strip()
                    options[name] = url
            
            if not options:
                all_urls = re.findall(r'(https?://[^\s\"\'<>]+)', clean_text)
                for i, url in enumerate(all_urls):
                    options[f"Link {i+1}"] = url

            if not options:
                return False, f"No video URLs detected for Episode {episode}."

            best_url = None
            
            # Priority 1: 1080p
            for key in options.keys():
                if "1080" in key:
                    best_url = options[key]
                    break
                    
            # Priority 2: 720p
            if not best_url:
                for key in options.keys():
                    if "720" in key:
                        best_url = options[key]
                        break

            # Priority 3: Mp4 (Catches your Sharepoint link) or standard video files
            if not best_url:
                for key, url in options.items():
                    if "mp4" in key.lower() or ".mp4" in url.lower() or ".m3u8" in url.lower():
                        best_url = url
                        break
                        
            # Priority 4: First available link (Crash prevention)
            if not best_url:
                best_url = list(options.values())[0]
                
            return True, best_url

        else:
            return False, f"ani-cli failed. Episode {episode} might not exist."

    except Exception as e:
        return False, f"System Error: {str(e)}"

def play_video_cli(url):
    clean_url = url.strip().strip("'\"")
    try:
        subprocess.run(["mpv", clean_url], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        return True, "Player closed."
    except Exception as e:
        return False, str(e)

def download_episodes_native(query, index, episodes_list, anime_name, progress_callback, finished_callback, single_finished_callback=None):
    if not episodes_list:
        finished_callback(False, "No episodes selected.")
        return

    settings = load_settings()
    # Correctly expands ~/Downloads to /home/bloom/Downloads
    download_dir = os.path.expanduser(settings.get("download_path", get_default_download_dir()))
    quality = settings.get("preferred_quality", "1080p")
    
    os.makedirs(download_dir, exist_ok=True)

    sorted_eps = sorted(episodes_list, key=lambda x: float(x) if x.replace('.','',1).isdigit() else 0)

    original_cwd = os.getcwd()
    my_env = os.environ.copy()
    my_env["PATH"] = f"{original_cwd}:{my_env.get('PATH', '')}"
    my_env["TERM"] = "xterm-256color"

    # REVERTED to the original trap that worked for you!
    trap_script = "#!/bin/sh\ncat > .ani_results.tmp\nexit 1\n"
    for tool in ["fzf", "rofi", "dmenu", "wofi"]:
        tool_path = os.path.join(original_cwd, tool)
        with open(tool_path, "w") as f:
            f.write(trap_script)
        os.chmod(tool_path, 0o755)

    try:
        for ep in sorted_eps:
            progress_callback(ep, 0.0, "Connecting...", False)
            
            # REVERTED to the original quality flag and script wrapper!
            q_flag = ""
            if quality != "Best Available":
                q_flag = f" -q {quality.replace('p', '')}"
                
            safe_query = query.replace("'", "'\\''")
            cmd_str = f"ani-cli '{safe_query}' -S {index} -d -e {ep}{q_flag}"
            command = ["script", "-q", "-e", "-c", cmd_str, "/dev/null"]
            
            process = subprocess.Popen(command, env=my_env, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, cwd=download_dir)
            
            buffer = ""
            while True:
                char_bytes = process.stdout.read(1)
                if not char_bytes and process.poll() is not None:
                    break
                    
                try:
                    char = char_bytes.decode('utf-8', errors='ignore')
                except Exception:
                    continue

                if char in ['\r', '\n']:
                    line = buffer.strip()
                    buffer = ""
                    if not line:
                        continue
                        
                    clean_line = re.sub(r'\x1b\[[0-9;]*[a-zA-Z]', '', line)
                    
                    if "%" in clean_line and "at" in clean_line:
                        try:
                            percent_str = re.search(r'(\d+\.?\d*)%', clean_line)
                            speed_str = re.search(r'at\s+([^ ]+)', clean_line)
                            if percent_str:
                                percent = float(percent_str.group(1)) / 100.0
                                speed = speed_str.group(1) if speed_str else "Unknown Speed"
                                progress_callback(ep, percent, speed, False)
                        except Exception: pass
                        
                    elif "size=" in clean_line and "time=" in clean_line:
                        try:
                            size_match = re.search(r'size=\s*([^ ]+)', clean_line)
                            speed_match = re.search(r'speed=\s*([^ ]+)', clean_line)
                            size = size_match.group(1) if size_match else ""
                            speed = speed_match.group(1) if speed_match else ""
                            progress_callback(ep, 0.0, f"{size} | Spd: {speed}", True)
                        except Exception: pass
                else:
                    buffer += char

            process.wait()
            
            if process.returncode != 0:
                finished_callback(False, f"Failed to download Episode {ep}.")
                return
            else:
                save_download_data(anime_name, ep, download_dir)
                if single_finished_callback:
                    single_finished_callback()
                    
        finished_callback(True, "All downloads finished successfully!")
        
    except Exception as e:
        finished_callback(False, f"System Error: {str(e)}")
    finally:
        for tool in ["fzf", "rofi", "dmenu", "wofi"]:
            tool_path = os.path.join(original_cwd, tool)
            if os.path.exists(tool_path):
                os.remove(tool_path)

def load_history():
    if not os.path.exists(HISTORY_FILE):
        return []
    try:
        with open(HISTORY_FILE, "r") as f:
            return json.load(f)
    except Exception:
        return []

def save_to_history(anime_name, episode, query="", index=1):
    history = load_history()
    
    # Check if we already have watched episodes for this show
    existing_item = next((item for item in history if item.get('name') == anime_name), None)
    watched_eps = existing_item.get('watched_eps', []) if existing_item else []
    
    # Add the new episode if it isn't already marked
    if str(episode) not in watched_eps:
        watched_eps.append(str(episode))
        
    history = [item for item in history if item.get('name') != anime_name]
    
    history.insert(0, {
        "name": anime_name,
        "episode": str(episode),
        "query": query,
        "index": index,
        "watched_eps": watched_eps # Save the array to the file!
    })
    
    history = history[:10]
    with open(HISTORY_FILE, "w") as f:
        json.dump(history, f, indent=4)
        
    return watched_eps

def get_watched_episodes(anime_name):
    history = load_history()
    for item in history:
        if item.get('name') == anime_name:
            return item.get('watched_eps', [])
    return []

def clear_history():
    if os.path.exists(HISTORY_FILE):
        with open(HISTORY_FILE, "w") as f:
            json.dump([], f)
            
    my_env = os.environ.copy()
    my_env["PATH"] = f"{os.getcwd()}:{my_env.get('PATH', '')}"
    try:
        subprocess.run(["ani-cli", "-D"], env=my_env, capture_output=True)
        return True
    except Exception:
        return False

FAVORITES_FILE = "favorites.json"

def load_favorites():
    if not os.path.exists(FAVORITES_FILE):
        return []
    try:
        with open(FAVORITES_FILE, "r") as f:
            return json.load(f)
    except Exception:
        return []

def toggle_favorite(anime_name, query="", index=1):
    favs = load_favorites()
    
    # Check if it already exists
    exists = any(item.get('name') == anime_name for item in favs)
    
    if exists:
        # Remove it
        favs = [item for item in favs if item.get('name') != anime_name]
        state = False
    else:
        # Add it to the top
        favs.insert(0, {
            "name": anime_name,
            "query": query,
            "index": index
        })
        state = True
        
    with open(FAVORITES_FILE, "w") as f:
        json.dump(favs, f, indent=4)
        
    return state

def is_favorite(anime_name):
    favs = load_favorites()
    return any(item.get('name') == anime_name for item in favs)