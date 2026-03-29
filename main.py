import customtkinter as ctk
import threading
from styles import Colors, Fonts
import backend
from pages import MainMenu, ResultsMenu, EpisodeMenu

class App(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("AniBloom")
        self.geometry("800x600")
        ctk.set_appearance_mode("dark")
        self.configure(fg_color=Colors.BG)

        self.current_query = ""
        self.selected_index = 0

        self.main_page = MainMenu(self, self.on_search, self.on_history_select, self.on_clear_history)
        self.results_page = ResultsMenu(self, self.show_main, self.on_select_anime)
        self.episode_page = EpisodeMenu(self, self.show_results, self.on_play_episode, self.on_download_episodes, self.on_toggle_favorite)

        self.floating_dl_frame = ctk.CTkFrame(self, fg_color=Colors.SURFACE, corner_radius=10, border_width=1, border_color=Colors.BORDER)
        
        self.dl_status_label = ctk.CTkLabel(self.floating_dl_frame, text="⬇️ Preparing...", font=Fonts.BODY_BOLD, text_color=Colors.TEXT)
        self.dl_status_label.pack(padx=20, pady=(10, 5))
        
        self.dl_progress = ctk.CTkProgressBar(self.floating_dl_frame, width=150, height=8, fg_color=Colors.BG, progress_color=Colors.PRIMARY)
        self.dl_progress.set(0)
        self.dl_progress.pack(padx=20, pady=(0, 5))
        
        self.dl_speed_label = ctk.CTkLabel(self.floating_dl_frame, text="0.0 MiB/s", font=Fonts.SMALL, text_color=Colors.SUBTEXT)
        self.dl_speed_label.pack(padx=20, pady=(0, 10))

        self.show_main()
        self.refresh_lists()

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
        page_instance.log(f"Starting background download for {len(episodes_list)} episodes...")
        page_instance.toggle_mode()
        
        # --- NEW: Pin to Top Right Corner! ---
        # relx=0.97 means 97% to the right. rely=0.03 means 3% down from the top.
        self.floating_dl_frame.place(relx=0.97, rely=0.03, anchor="ne")

        def update_progress(ep, percent, speed_text, is_indeterminate):
            def update_ui():
                self.dl_status_label.configure(text=f"⬇️ Ep {ep} Downloading", text_color=Colors.TEXT)
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
                    # Hide the floating widget after 4 seconds
                    self.after(4000, self.floating_dl_frame.place_forget)
                else:
                    page_instance.log("❌ " + msg)
                    self.dl_status_label.configure(text="❌ Failed", text_color=Colors.ERROR)
                    self.after(4000, self.floating_dl_frame.place_forget)
            self.after(0, update_ui)

        threading.Thread(
            target=backend.download_episodes_native,
            args=(self.current_query, self.selected_index, episodes_list, update_progress, download_finished),
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