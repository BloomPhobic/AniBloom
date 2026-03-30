import customtkinter as ctk
import threading
import os
from PIL import Image, ImageTk
from styles import Colors, Fonts
import backend
from pages import MainMenu, ResultsMenu, EpisodeMenu, SettingsWindow
from customtkinter import filedialog

class App(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("AniBloom")
        self.geometry("800x600")
        ctk.set_appearance_mode("dark")
        self.configure(fg_color=Colors.BG)

        try:
            icon_path = os.path.join(os.path.dirname(__file__), "icon.png")
            if os.path.exists(icon_path):
                img = Image.open(icon_path)
                photo = ImageTk.PhotoImage(img)
                self.wm_iconphoto(True, photo)
        except Exception as e:
            print(f"Could not load icon: {e}")

        self.current_query = ""
        self.selected_index = 0

        self.main_page = MainMenu(self, self.on_search, self.on_history_select, self.on_clear_history)
        self.results_page = ResultsMenu(self, self.show_main, self.on_select_anime)
        self.episode_page = EpisodeMenu(self, self.show_results, self.on_play_episode, self.on_download_episodes, self.on_toggle_favorite)

        self.top_nav = ctk.CTkFrame(self, fg_color="transparent")
        self.top_nav.place(relx=0.98, rely=0.02, anchor="ne")

        self.dl_btn = ctk.CTkButton(
            self.top_nav, text="⤓", width=40, height=40, font=("Helvetica", 24),
            fg_color="transparent", text_color=Colors.TEXT, hover_color=Colors.PRIMARY_HOVER,
            command=self.toggle_downloads_box
        )
        self.dl_btn.pack(side="left", padx=5)

        self.settings_btn = ctk.CTkButton(
            self.top_nav, text="⚙️", width=40, height=40, font=("Helvetica", 24),
            fg_color="transparent", text_color=Colors.TEXT, hover_color=Colors.PRIMARY_HOVER,
            command=self.open_settings
        )
        self.settings_btn.pack(side="left", padx=5)

        self.dl_box_visible = False
        self.dl_box = ctk.CTkFrame(self, width=350, height=350, fg_color=Colors.SURFACE, border_width=1, border_color=Colors.BORDER)
        self.dl_box.pack_propagate(False)
        
        self.dl_header = ctk.CTkFrame(self.dl_box, fg_color="transparent")
        self.dl_header.pack(fill="x", padx=10, pady=10)
        ctk.CTkLabel(self.dl_header, text="Downloads", font=Fonts.BODY_BOLD, text_color=Colors.TEXT).pack(side="left")
        ctk.CTkButton(self.dl_header, text="🗑️", width=30, height=24, fg_color="transparent", hover_color=Colors.ERROR, text_color=Colors.TEXT, command=self.clear_download_data).pack(side="right")

        self.active_dl_frame = ctk.CTkFrame(self.dl_box, fg_color=Colors.BG, corner_radius=5)
        
        self.dl_status_label = ctk.CTkLabel(self.active_dl_frame, text="⬇️ Preparing...", font=Fonts.SMALL, text_color=Colors.TEXT)
        self.dl_status_label.pack(padx=10, pady=(5, 0), anchor="w")
        
        self.dl_progress = ctk.CTkProgressBar(self.active_dl_frame, width=390, height=6, fg_color=Colors.SURFACE, progress_color=Colors.PRIMARY)
        self.dl_progress.set(0)
        self.dl_progress.pack(padx=10, pady=5)
        
        self.dl_speed_label = ctk.CTkLabel(self.active_dl_frame, text="0.0 MiB/s", font=Fonts.SMALL, text_color=Colors.SUBTEXT)
        self.dl_speed_label.pack(padx=10, pady=(0, 5), anchor="w")

        self.dl_history_scroll = ctk.CTkScrollableFrame(self.dl_box, fg_color="transparent")
        self.dl_history_scroll.pack(fill="both", expand=True, padx=5, pady=5)

        settings = backend.load_settings()
        self.current_download_path = settings.get("download_path", backend.get_default_download_dir())
        self.current_quality = settings.get("preferred_quality", "1080p")
        self.settings_window = None

        self.show_main()
        self.refresh_lists()
        self.refresh_downloads_list()

    def hide_all(self):
        self.main_page.pack_forget()
        self.results_page.pack_forget()
        self.episode_page.pack_forget()

    def show_main(self):
        self.hide_all()
        self.main_page.pack(fill="both", expand=True)

    def show_results(self):
        self.hide_all()
        self.results_page.pack(fill="both", expand=True)

    def show_episode(self):
        self.hide_all()
        self.episode_page.pack(fill="both", expand=True)

    def refresh_lists(self):
        history_data = backend.load_history()
        self.main_page.populate_history(history_data)
        
        fav_data = backend.load_favorites()
        self.main_page.populate_favorites(fav_data)

    def toggle_downloads_box(self):
        if self.dl_box_visible:
            self.dl_box.place_forget()
            self.dl_box_visible = False
        else:
            self.dl_box.place(relx=0.98, rely=0.07, anchor="ne")
            self.dl_box.lift()
            self.dl_box_visible = True

    def refresh_downloads_list(self):
        for widget in self.dl_history_scroll.winfo_children():
            widget.destroy()
            
        downloads_data = backend.load_downloads_data()
        
        if not downloads_data:
            ctk.CTkLabel(self.dl_history_scroll, text="No downloads yet.", text_color=Colors.SUBTEXT, font=Fonts.BODY).pack(pady=20)
            return
            
        for item in downloads_data:
            name = item.get('name', 'Unknown')
            ep = item.get('episode', '?')
            folder = item.get('folder_path', '')
            
            short_name = name[:20] + "..." if len(name) > 20 else name
            
            btn = ctk.CTkButton(
                self.dl_history_scroll, text=f"📁 {short_name} - Ep {ep}", anchor="w",
                fg_color="transparent", hover_color="#3a3a3a", text_color=Colors.TEXT, font=Fonts.BODY,
                command=lambda p=folder: backend.open_file_manager(p)
            )
            btn.pack(fill="x", pady=2, padx=5)

    def clear_download_data(self):
        backend.clear_downloads_data()
        self.refresh_downloads_list()

    def open_settings(self):
        if self.settings_window is None or not self.settings_window.winfo_exists():
            self.settings_window = SettingsWindow(self, self.current_quality, self.current_download_path, self.save_settings, self.browse_directory)
        else:
            self.settings_window.focus()

    def browse_directory(self, window_instance):
        new_path = filedialog.askdirectory(title="Select Download Folder")
        if new_path:
            self.current_download_path = new_path
            window_instance.update_path_display(new_path)

    def save_settings(self, new_quality, window_instance):
        self.current_quality = new_quality
        # Tell the backend to save the JSON file!
        backend.save_settings(new_quality, self.current_download_path)
        window_instance.destroy()

    def on_clear_history(self):
        backend.clear_history()
        self.refresh_lists()

    def on_toggle_favorite(self):
        anime_name = self.episode_page.title_label.cget("text")
        new_state = backend.toggle_favorite(anime_name, self.current_query, self.selected_index)
        self.refresh_lists() # Update the tabbed UI in the background
        return new_state

    def on_search(self, query, page_instance):
        self.current_query = query
        page_instance.search_btn.configure(text="Scraping the web...", state="disabled")
        
        def worker():
            success, data = backend.search_anime_cli(query)
            self.after(0, self.handle_search_result, success, data, query, page_instance)

        threading.Thread(target=worker, daemon=True).start()

    def handle_search_result(self, success, data, query, page_instance):
        page_instance.search_btn.configure(text="Search", state="normal") 
        if success:
            self.results_page.populate(query, data)
            self.show_results()
        else:
            page_instance.search_btn.configure(text="No results found. Try again.")

    def on_history_select(self, item_data):
        self.current_query = item_data.get("query", item_data.get("name"))
        target_name = item_data.get("name", "Unknown Show")
        fallback_index = item_data.get("index", 1)

        self.episode_page.back_btn.configure(command=self.show_main)

        def worker():
            search_success, results = backend.search_anime_cli(self.current_query)
            best_index = fallback_index
            
            if search_success and results:
                for i, raw_result in enumerate(results):
                    clean_result = backend.clean_anime_title(raw_result)
                    if clean_result.lower() == target_name.lower():
                        best_index = i + 1 
                        break
            
            self.selected_index = best_index
            ep_success, total_eps = backend.get_episode_count_cli(self.current_query, self.selected_index)
            self.after(0, self.handle_history_transition, ep_success, total_eps, target_name)

        threading.Thread(target=worker, daemon=True).start()

    def handle_history_transition(self, success, episodes_list, name):
        self.main_page.history_label.configure(text="Your Library")
        if not success or not episodes_list:
            episodes_list = [str(i) for i in range(1, 1001)]
            
        is_fav = backend.is_favorite(name)
        watched_eps = backend.get_watched_episodes(name) # Grab the watched list
        self.episode_page.setup(name, episodes_list, is_fav, watched_eps)
        self.show_episode()

    def on_select_anime(self, name, index):
        self.selected_index = index + 1
        self.results_page.title_label.configure(text="Fetching episodes, please wait...")
        
        self.episode_page.back_btn.configure(command=self.show_results)
        cleaned_name = backend.clean_anime_title(name)
        
        def episode_worker():
            success, total_eps = backend.get_episode_count_cli(self.current_query, self.selected_index)
            self.after(0, self.handle_episode_count, success, total_eps, cleaned_name)

        threading.Thread(target=episode_worker, daemon=True).start()

    def handle_episode_count(self, success, episodes_list, name):
        self.results_page.title_label.configure(text=f"Results for '{self.current_query}'")
        if not success or not episodes_list:
            episodes_list = [str(i) for i in range(1, 1001)]
            
        is_fav = backend.is_favorite(name)
        watched_eps = backend.get_watched_episodes(name) # Grab the watched list
        self.episode_page.setup(name, episodes_list, is_fav, watched_eps)
        self.show_episode()

    def on_play_episode(self, episode, page_instance):
        page_instance.log(f"Extracting Episode {episode}...")
        page_instance.watch_btn.configure(state="disabled", text="Extracting...")

        def worker():
            success, url_or_error = backend.get_video_url_cli(self.current_query, self.selected_index, episode)
            # Pass the episode number forward so the UI knows what we are playing!
            self.after(0, self.handle_play_result, success, url_or_error, page_instance, episode)

        threading.Thread(target=worker, daemon=True).start()

    def handle_play_result(self, success, url_or_error, page_instance, episode):
        if success:
            page_instance.log(f"✅ SUCCESS! URL Found.")
            page_instance.log("▶ Launching player...")
            
            # 1. Update history file immediately
            watched_eps = backend.save_to_history(
                self.episode_page.title_label.cget("text"),
                episode,
                self.current_query,
                self.selected_index
            )
            self.refresh_lists()
            
            # 2. Visually "Dim" the button on the grid
            page_instance.watched_episodes = watched_eps
            page_instance.draw_grid()
            
            # 3. We MUST run the player in a separate thread because it blocks until you close it!
            def player_worker():
                play_success, msg = backend.play_video_cli(url_or_error)
                self.after(0, self.on_player_closed, play_success, msg, page_instance, episode)
            
            threading.Thread(target=player_worker, daemon=True).start()
        else:
            page_instance.log(f"❌ Extraction Failed:\n{url_or_error}")
            page_instance.watch_btn.configure(state="normal", text="▶ Watch Episode")

    def on_download_episodes(self, episodes_list, page_instance):
        anime_name = self.episode_page.title_label.cget("text")
        short_name = anime_name[:20] + "..." if len(anime_name) > 20 else anime_name
        
        page_instance.log(f"Starting background download for {len(episodes_list)} episodes...")
        page_instance.toggle_mode()
        
        if not self.dl_box_visible:
            self.toggle_downloads_box()
            
        self.dl_history_scroll.pack_forget()
        self.active_dl_frame.pack(fill="x", padx=10, pady=5) # Pack the progress bar first
        self.dl_history_scroll.pack(fill="both", expand=True, padx=5, pady=5) # Put the history list back underneath

        def update_progress(ep, percent, speed_text, is_indeterminate):
            def update_ui():
                self.dl_status_label.configure(text=f"⬇️ Ep {ep} - {short_name}", text_color=Colors.TEXT)
                self.dl_speed_label.configure(text=speed_text)
                
                if is_indeterminate:
                    if self.dl_progress.cget("mode") != "indeterminate":
                        self.dl_progress.configure(mode="indeterminate")
                        self.dl_progress.start()
                else:
                    if self.dl_progress.cget("mode") == "indeterminate":
                        self.dl_progress.stop()
                        self.dl_progress.configure(mode="determinate")
                    self.dl_progress.set(percent)
                    
            self.after(0, update_ui)

        def download_finished(success, msg):
            def update_ui():
                if self.dl_progress.cget("mode") == "indeterminate":
                    self.dl_progress.stop()
                    self.dl_progress.configure(mode="determinate")
                self.dl_progress.set(1.0)
                
                if success:
                    page_instance.log("✅ " + msg)
                    self.dl_status_label.configure(text="✅ Complete!", text_color=Colors.PRIMARY)
                    self.dl_speed_label.configure(text="")
                else:
                    page_instance.log("❌ " + msg)
                    self.dl_status_label.configure(text="❌ Failed", text_color=Colors.ERROR)
                
                self.refresh_downloads_list()
                self.after(3000, self.active_dl_frame.pack_forget)
            self.after(0, update_ui)

        def single_ep_done():
            self.after(0, self.refresh_downloads_list)

        threading.Thread(
            target=backend.download_episodes_native,
            args=(self.current_query, self.selected_index, episodes_list, anime_name, update_progress, download_finished, single_ep_done),
            daemon=True
        ).start()

    def on_player_closed(self, play_success, msg, page_instance, episode):
        if not play_success:
            page_instance.log(f"❌ Player Error: {msg}")
        else:
            page_instance.log("✅ Player closed.")
            
            # Auto-queue the next episode!
            try:
                current_idx = page_instance.episodes_list.index(episode)
                if current_idx + 1 < len(page_instance.episodes_list):
                    next_ep = page_instance.episodes_list[current_idx + 1]
                    page_instance.ep_input.delete(0, "end")
                    page_instance.ep_input.insert(0, next_ep)
                    page_instance.log(f"🍿 Queued up Episode {next_ep}! Hit play when ready.")
            except ValueError:
                pass

        page_instance.watch_btn.configure(state="normal", text="▶ Watch Episode")
if __name__ == "__main__":
    app = App()
    app.mainloop()