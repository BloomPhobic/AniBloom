import subprocess
import os
import re
import shutil
import json

HISTORY_FILE = "watch_history.json"

def clean_anime_title(raw_title):
    clean = re.sub(r'\[\d+[^\]]*\]|\(\d+[^\)]*\)', '', raw_title)
    clean = " ".join(clean.split())
    return clean

def search_anime_cli(query):
    if not query:
        return False, "Query cannot be empty."

    with open("fzf", "w") as f:
        f.write("#!/bin/sh\ncat > .ani_results.tmp\nexit 1\n")
    os.chmod("fzf", 0o755)

    my_env = os.environ.copy()
    my_env["PATH"] = f"{os.getcwd()}:{my_env.get('PATH', '')}"

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
        if os.path.exists("fzf"):
            os.remove("fzf")

def get_episode_count_cli(query, index):
    with open("fzf", "w") as f:
        f.write("#!/bin/sh\ncat > .ani_results.tmp\nexit 1\n")
    os.chmod("fzf", 0o755)

    my_env = os.environ.copy()
    my_env["PATH"] = f"{os.getcwd()}:{my_env.get('PATH', '')}"

    try:
        subprocess.run(["ani-cli", query, "-S", str(index)], env=my_env, capture_output=True)

        if os.path.exists(".ani_results.tmp"):
            with open(".ani_results.tmp", "r") as f:
                raw_lines = f.readlines()
            os.remove(".ani_results.tmp")

            valid_lines = [line.strip() for line in raw_lines if line.strip()]
            
            if valid_lines:
                first_line = valid_lines[0].lower()
                
                # Movie filter: Server lists have "http" or ">"
                if "http" in first_line or ">" in first_line:
                    return True, ["1"]
                
                # --- THE NEW HARVESTER ---
                episodes = []
                for line in valid_lines:
                    clean = re.sub(r'\x1b\[[0-9;]*[a-zA-Z]', '', line).strip()
                    # Extract the exact episode number (even 0 or decimals like 1.5)
                    match = re.search(r'\d+(\.\d+)?', clean)
                    if match:
                        episodes.append(match.group())
                
                # Remove duplicates and sort them properly (e.g., 0, 1, 2, 3...)
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
        if os.path.exists("fzf"):
            os.remove("fzf")

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
        subprocess.Popen(["mpv", clean_url], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        return True, "Player launched successfully."
    except Exception as e:
        return False, str(e)

def download_episodes_cli(query, index, episodes_list):
    if not episodes_list:
        return False, "No episodes selected."

    terminals = ["kitty", "alacritty", "konsole", "gnome-terminal", "xfce4-terminal", "xterm"]
    chosen_term = next((term for term in terminals if shutil.which(term)), None)
    
    if not chosen_term:
        return False, "Could not find a standard terminal to show download progress."
        
    try:
        commands = []
        # Sorts the strings numerically before downloading
        for ep in sorted(episodes_list, key=lambda x: float(x) if x.replace('.','',1).isdigit() else 0):
            commands.append(f"echo '▶ Starting Episode {ep}...'; ani-cli '{query}' -S {index} -d -e {ep}")
            
        full_command = " && ".join(commands)
        bash_cmd = f"{full_command}; echo ''; echo '✅ All downloads finished! Press Enter to close.'; read"
        
        if chosen_term in ["gnome-terminal", "xfce4-terminal"]:
            subprocess.Popen([chosen_term, "--", "bash", "-c", bash_cmd])
        else:
            subprocess.Popen([chosen_term, "-e", "bash", "-c", bash_cmd])
            
        return True, f"Download launched in a new {chosen_term} window!"
    except Exception as e:
        return False, f"Failed to launch terminal: {str(e)}"

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
    history = [item for item in history if item.get('name') != anime_name]
    
    history.insert(0, {
        "name": anime_name, 
        "episode": episode,
        "query": query,
        "index": index
    })
    
    history = history[:10]
    with open(HISTORY_FILE, "w") as f:
        json.dump(history, f, indent=4)

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