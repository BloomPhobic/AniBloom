import customtkinter as ctk
import threading
from styles import Colors
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
        self.episode_page = EpisodeMenu(self, self.show_results, self.on_play_episode, self.on_download_episodes)

        self.show_main()
        self.refresh_history()

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

    def refresh_history(self):
        history_data = backend.load_history()
        self.main_page.populate_history(history_data)

    def on_clear_history(self):
        backend.clear_history()
        self.refresh_history() # Instantly update the UI to show an empty box

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
            # 1. Do a lightning-fast background search
            search_success, results = backend.search_anime_cli(self.current_query)
            
            # Default to our saved index just in case the search fails
            best_index = fallback_index
            
            if search_success and results:
                # 2. Loop through the fresh live results
                for i, raw_result in enumerate(results):
                    # Clean the live result so it matches our saved format
                    clean_result = backend.clean_anime_title(raw_result)
                    
                    # 3. Check for the EXACT text match (ignoring case)
                    if clean_result.lower() == target_name.lower():
                        best_index = i + 1  # Arrays start at 0, ani-cli starts at 1
                        break
            
            self.selected_index = best_index

            # 4. Fetch the episodes using the guaranteed correct live index
            ep_success, total_eps = backend.get_episode_count_cli(self.current_query, self.selected_index)
            self.after(0, self.handle_history_transition, ep_success, total_eps, target_name)

        threading.Thread(target=worker, daemon=True).start()

    def handle_history_transition(self, success, episodes_list, name):
        self.main_page.history_label.configure(text="Continue Watching")
        # If scraper fails, give a giant generic list as a fallback
        if not success or not episodes_list:
            episodes_list = [str(i) for i in range(1, 1001)]
        self.episode_page.setup(name, episodes_list)
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
        # If scraper fails, give a giant generic list as a fallback
        if not success or not episodes_list:
            episodes_list = [str(i) for i in range(1, 1001)]
        self.episode_page.setup(name, episodes_list)
        self.show_episode()

    def on_play_episode(self, episode, page_instance):
        page_instance.log(f"Extracting Episode {episode}...")
        page_instance.watch_btn.configure(state="disabled", text="Extracting...")

        def worker():
            success, url_or_error = backend.get_video_url_cli(self.current_query, self.selected_index, episode)
            self.after(0, self.handle_play_result, success, url_or_error, page_instance)

        threading.Thread(target=worker, daemon=True).start()

    def handle_play_result(self, success, url_or_error, page_instance):
        if success:
            page_instance.log(f"✅ SUCCESS! URL Found.")
            page_instance.log("▶ Launching player...")
            
            backend.save_to_history(
                self.episode_page.title_label.cget("text"), 
                self.episode_page.ep_input.get(),
                self.current_query,
                self.selected_index
            )
            self.refresh_history() 
            
            play_success, msg = backend.play_video_cli(url_or_error)
            if not play_success:
                page_instance.log(f"❌ Player Error: {msg}")
        else:
            page_instance.log(f"❌ Extraction Failed:\n{url_or_error}")

        page_instance.watch_btn.configure(state="normal", text="▶ Watch Episode")

    def on_download_episodes(self, episodes_list, page_instance):
        page_instance.log(f"Preparing to download {len(episodes_list)} episodes...")
        
        success, msg = backend.download_episodes_cli(self.current_query, self.selected_index, episodes_list)
        
        if success:
            page_instance.log(msg)
            page_instance.toggle_mode()
        else:
            page_instance.log(msg)

if __name__ == "__main__":
    app = App()
    app.mainloop()