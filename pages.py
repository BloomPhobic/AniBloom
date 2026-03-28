import customtkinter as ctk
from styles import Colors, Fonts

class MainMenu(ctk.CTkFrame):
    # --- NEW: Added clear_history_callback ---
    def __init__(self, master, search_callback, history_callback, clear_history_callback):
        super().__init__(master, fg_color="transparent")
        self.search_callback = search_callback
        self.history_callback = history_callback

        title = ctk.CTkLabel(self, text="AniBloom", font=Fonts.TITLE, text_color=Colors.PRIMARY)
        title.pack(pady=(80, 10))

        sub = ctk.CTkLabel(self, text="Search for any anime to start watching", text_color=Colors.SUBTEXT, font=Fonts.BODY)
        sub.pack(pady=(0, 30))

        self.search_bar = ctk.CTkEntry(self, placeholder_text="e.g., Attack on Titan...", width=500, height=40, font=Fonts.BODY)
        self.search_bar.pack(pady=10)
        self.search_bar.bind("<Return>", self.handle_search)

        self.search_btn = ctk.CTkButton(self, text="Search", width=200, height=40, font=Fonts.BODY_BOLD, fg_color=Colors.PRIMARY, hover_color=Colors.PRIMARY_HOVER, command=self.handle_search)
        self.search_btn.pack(pady=20)

        # --- History UI Area ---
        self.history_container = ctk.CTkFrame(self, fg_color="transparent")
        self.history_container.pack(pady=(20, 0), fill="x", padx=100)
        
        # --- NEW: A top bar to hold the Title on the left, and the Clear button on the right ---
        self.history_top_bar = ctk.CTkFrame(self.history_container, fg_color="transparent")
        self.history_top_bar.pack(fill="x", pady=(0, 10))
        
        self.history_label = ctk.CTkLabel(self.history_top_bar, text="Continue Watching", font=Fonts.HEADER, text_color=Colors.TEXT)
        self.history_label.pack(side="left")
        
        self.clear_btn = ctk.CTkButton(self.history_top_bar, text="🗑️ Clear", width=60, height=28, fg_color=Colors.ERROR, hover_color="#cc0000", font=Fonts.SMALL, command=clear_history_callback)
        self.clear_btn.pack(side="right")
        
        self.history_list = ctk.CTkScrollableFrame(self.history_container, height=180, fg_color=Colors.SURFACE)
        self.history_list.pack(fill="x")

    def handle_search(self, event=None):
        query = self.search_bar.get().strip()
        if query:
            self.search_btn.configure(text="Scraping...", state="disabled")
            self.search_callback(query, self)

    def populate_history(self, history_data):
        for widget in self.history_list.winfo_children():
            widget.destroy()
            
        if not history_data:
            ctk.CTkLabel(self.history_list, text="Your watch history is empty. Go watch something!", text_color=Colors.SUBTEXT, font=Fonts.BODY).pack(pady=30)
            self.clear_btn.configure(state="disabled") # Disable button if empty
            return
            
        self.clear_btn.configure(state="normal") # Enable button if there is data
            
        for item in history_data:
            name = item.get('name', 'Unknown')
            ep = item.get('episode', '1')
            
            btn_text = f"▶  {name}  |  Last watched: Ep {ep}"
            btn = ctk.CTkButton(
                self.history_list, text=btn_text, anchor="w", 
                fg_color="transparent", hover_color="#3a3a3a", text_color=Colors.TEXT, font=Fonts.BODY,
                command=lambda data=item: self.handle_history_click(data) 
            )
            btn.pack(fill="x", pady=2, padx=5)

    def handle_history_click(self, item_data):
        self.history_label.configure(text=f"Loading '{item_data.get('name', '')}'...")
        self.history_callback(item_data)

    def handle_search(self, event=None):
        query = self.search_bar.get().strip()
        if query:
            self.search_btn.configure(text="Scraping...", state="disabled")
            self.search_callback(query, self)

    def populate_history(self, history_data):
        for widget in self.history_list.winfo_children():
            widget.destroy()
            
        if not history_data:
            ctk.CTkLabel(self.history_list, text="Your watch history is empty. Go watch something!", text_color=Colors.SUBTEXT, font=Fonts.BODY).pack(pady=30)
            return
            
        for item in history_data:
            name = item.get('name', 'Unknown')
            ep = item.get('episode', '1')
            
            btn_text = f"▶  {name}  |  Last watched: Ep {ep}"
            btn = ctk.CTkButton(
                self.history_list, text=btn_text, anchor="w", 
                fg_color="transparent", hover_color="#3a3a3a", text_color=Colors.TEXT, font=Fonts.BODY,
                # --- UPDATED: Pass the WHOLE dictionary item, not just the name ---
                command=lambda data=item: self.handle_history_click(data) 
            )
            btn.pack(fill="x", pady=2, padx=5)

    def handle_history_click(self, item_data):
        self.history_label.configure(text=f"Loading '{item_data.get('name', '')}'...")
        self.history_callback(item_data)


class ResultsMenu(ctk.CTkFrame):
    def __init__(self, master, back_callback, select_callback):
        super().__init__(master, fg_color="transparent")
        self.select_callback = select_callback

        nav = ctk.CTkFrame(self, fg_color="transparent")
        nav.pack(fill="x", pady=10, padx=20)

        ctk.CTkButton(nav, text="< Back", width=60, fg_color="transparent", hover_color=Colors.SURFACE, border_width=1, border_color=Colors.BORDER, text_color=Colors.TEXT, command=back_callback).pack(side="left")

        self.title_label = ctk.CTkLabel(self, text="Search Results", font=Fonts.HEADER, text_color=Colors.TEXT)
        self.title_label.pack(pady=(10, 20))

        self.scroll_frame = ctk.CTkScrollableFrame(self, width=600, height=400, fg_color=Colors.SURFACE)
        self.scroll_frame.pack(pady=10)

    def populate(self, query, results):
        self.title_label.configure(text=f"Results for '{query}'")
        for widget in self.scroll_frame.winfo_children():
            widget.destroy()
        for index, name in enumerate(results):
            btn = ctk.CTkButton(self.scroll_frame, text=name, anchor="w", fg_color="transparent", hover_color="#3a3a3a", text_color=Colors.TEXT, font=Fonts.BODY, command=lambda n=name, i=index: self.select_callback(n, i))
            btn.pack(fill="x", pady=2, padx=5)


class EpisodeMenu(ctk.CTkFrame):
    def __init__(self, master, back_callback, play_callback, download_callback):
        super().__init__(master, fg_color="transparent")
        self.play_callback = play_callback
        self.download_callback = download_callback 
        
        # --- UPDATED VARIABLES ---
        self.current_ep_page = 0
        self.eps_per_page = 26
        self.episodes_list = [] # Store the exact array from the backend
        self.total_episodes = 0
        
        self.download_mode = False      
        self.selected_episodes = set()  

        nav = ctk.CTkFrame(self, fg_color="transparent")
        nav.pack(fill="x", pady=5, padx=20)
        self.back_btn = ctk.CTkButton(nav, text="< Back", width=60, fg_color="transparent", hover_color=Colors.SURFACE, border_width=1, border_color=Colors.BORDER, text_color=Colors.TEXT, command=back_callback)
        self.back_btn.pack(side="left")

        self.title_label = ctk.CTkLabel(self, text="Anime Name", font=Fonts.HEADER, text_color=Colors.TEXT, wraplength=700)
        self.title_label.pack(pady=(5, 5))

        self.mode_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.mode_frame.pack(pady=5)
        self.toggle_mode_btn = ctk.CTkButton(self.mode_frame, text="🔄 Switch to Download Mode", fg_color=Colors.SECONDARY, hover_color=Colors.SECONDARY_HOVER, command=self.toggle_mode)
        self.toggle_mode_btn.pack(side="top", pady=5)
        
        self.dl_controls = ctk.CTkFrame(self.mode_frame, fg_color="transparent")
        self.select_all_btn = ctk.CTkButton(self.dl_controls, text="Select All", width=100, fg_color=Colors.SURFACE, hover_color="#3a3a3a", command=self.select_all_eps)
        self.select_all_btn.pack(side="left", padx=5)
        self.confirm_dl_btn = ctk.CTkButton(self.dl_controls, text="⬇️ Download Selected", width=150, font=Fonts.BODY_BOLD, fg_color=Colors.PRIMARY, hover_color=Colors.PRIMARY_HOVER, command=self.handle_download)
        self.confirm_dl_btn.pack(side="left", padx=5)

        self.grid_container = ctk.CTkFrame(self, fg_color="transparent")
        self.grid_container.pack(pady=5)
        self.grid_frame = ctk.CTkFrame(self.grid_container, fg_color="transparent")
        self.grid_frame.pack()
        
        self.page_nav = ctk.CTkFrame(self.grid_container, fg_color="transparent")
        self.page_nav.pack(pady=10)
        self.prev_btn = ctk.CTkButton(self.page_nav, text="< Prev", width=60, fg_color=Colors.SURFACE, hover_color="#3a3a3a", command=self.prev_page)
        self.prev_btn.pack(side="left", padx=10)
        self.page_label = ctk.CTkLabel(self.page_nav, text="Eps 1-26", font=Fonts.BODY)
        self.page_label.pack(side="left", padx=10)
        self.next_btn = ctk.CTkButton(self.page_nav, text="Next >", width=60, fg_color=Colors.SURFACE, hover_color="#3a3a3a", command=self.next_page)
        self.next_btn.pack(side="left", padx=10)

        self.watch_controls = ctk.CTkFrame(self, fg_color="transparent")
        self.watch_controls.pack(pady=10)
        ctk.CTkLabel(self.watch_controls, text="Or enter manually:", font=Fonts.BODY, text_color=Colors.SUBTEXT).pack(side="left", padx=10)
        self.ep_input = ctk.CTkEntry(self.watch_controls, width=60, font=Fonts.BODY, justify="center")
        self.ep_input.insert(0, "1")
        self.ep_input.pack(side="left", padx=10)
        self.ep_input.bind("<Return>", self.handle_play)
        self.watch_btn = ctk.CTkButton(self.watch_controls, text="▶ Watch Episode", font=Fonts.BODY_BOLD, fg_color=Colors.PRIMARY, hover_color=Colors.PRIMARY_HOVER, command=self.handle_play)
        self.watch_btn.pack(side="left", padx=15)

        self.console = ctk.CTkTextbox(self, width=650, height=130, text_color=Colors.SUBTEXT, fg_color=Colors.SURFACE)
        self.console.pack(pady=10)

    def toggle_mode(self):
        self.download_mode = not self.download_mode
        if self.download_mode:
            self.toggle_mode_btn.configure(text="❌ Cancel Download Mode", fg_color=Colors.ERROR, hover_color="#cc0000")
            self.watch_controls.pack_forget()  
            self.dl_controls.pack(side="top", pady=5) 
            self.log("ℹ️ Download Mode active. Click episodes to select them.")
        else:
            self.toggle_mode_btn.configure(text="🔄 Switch to Download Mode", fg_color=Colors.SECONDARY, hover_color=Colors.SECONDARY_HOVER)
            self.dl_controls.pack_forget()
            self.watch_controls.pack(pady=10)
            self.selected_episodes.clear() 
            self.log("ℹ️ Returned to Watch Mode.")
        self.draw_grid() 

    def select_all_eps(self):
        start_idx = self.current_ep_page * self.eps_per_page
        end_idx = min(start_idx + self.eps_per_page, self.total_episodes)
        
        # Add exact episode names to the selection
        for i in range(start_idx, end_idx):
            self.selected_episodes.add(self.episodes_list[i])
            
        self.draw_grid()
        self.log("✅ Selected episodes on this page.")

    def handle_download(self):
        if not self.selected_episodes:
            self.log("❌ ERROR: No episodes selected.")
            return
        self.download_callback(list(self.selected_episodes), self)

    def grid_click(self, ep_str):
        if self.download_mode:
            if ep_str in self.selected_episodes:
                self.selected_episodes.remove(ep_str)
            else:
                self.selected_episodes.add(ep_str)
            self.draw_grid()
        else:
            self.ep_input.delete(0, "end")
            self.ep_input.insert(0, ep_str)
            self.handle_play()

    def draw_grid(self):
        for widget in self.grid_frame.winfo_children():
            widget.destroy()
            
        start_idx = self.current_ep_page * self.eps_per_page
        end_idx = min(start_idx + self.eps_per_page, self.total_episodes)
        
        # Display the real names in the page nav! (e.g. Eps 0 - 25)
        if self.total_episodes > 0:
            first_ep = self.episodes_list[start_idx]
            last_ep = self.episodes_list[end_idx - 1]
            self.page_label.configure(text=f"Eps {first_ep} - {last_ep}")
        else:
            self.page_label.configure(text="No Episodes")
            
        self.prev_btn.configure(state="normal" if self.current_ep_page > 0 else "disabled")
        self.next_btn.configure(state="normal" if end_idx < self.total_episodes else "disabled")

        cols = 7
        page_eps = self.episodes_list[start_idx:end_idx]
        
        for i, ep_str in enumerate(page_eps):
            if self.download_mode and ep_str in self.selected_episodes:
                bg = Colors.PRIMARY
                hover = Colors.PRIMARY_HOVER
            else:
                bg = Colors.SURFACE
                hover = Colors.PRIMARY_HOVER

            btn = ctk.CTkButton(
                self.grid_frame, text=ep_str, width=45, height=40, font=Fonts.BODY_BOLD,
                fg_color=bg, hover_color=hover, border_width=1, border_color=Colors.BORDER,
                command=lambda e=ep_str: self.grid_click(e)
            )
            row = i // cols
            col = i % cols
            btn.grid(row=row, column=col, padx=4, pady=4)

    def next_page(self):
        self.current_ep_page += 1
        self.draw_grid()

    def prev_page(self):
        if self.current_ep_page > 0:
            self.current_ep_page -= 1
            self.draw_grid()

    def setup(self, name, episodes_list):
        self.episodes_list = [str(e) for e in episodes_list] # Ensure they are string labels
        self.total_episodes = len(self.episodes_list)
        
        self.title_label.configure(text=name)
        self.console.delete("1.0", "end")
        
        if self.download_mode:
            self.toggle_mode()
        self.selected_episodes.clear()
        
        if self.total_episodes > 0 and self.episodes_list[0] == "1" and self.total_episodes == 1000:
            self.console.insert("end", "⚠️ Could not determine exact episode count.\nReady to extract video link.\n")
        else:
            self.console.insert("end", f"✅ Found {self.total_episodes} episodes.\nReady to extract video link.\n")
            
        self.ep_input.delete(0, "end")
        if self.episodes_list:
            # Auto-insert the exact first label! (If it's 0, it puts 0)
            self.ep_input.insert(0, self.episodes_list[0])
            
        self.current_ep_page = 0
        self.draw_grid()

    def log(self, text):
        self.console.insert("end", text + "\n")
        self.console.see("end")

    def handle_play(self, event=None):
        ep = self.ep_input.get().strip()
        
        # We only check if it's empty, so "0" or "1.5" still works!
        if not ep:
            self.log("❌ ERROR: Please enter an episode number.")
            return
            
        self.watch_btn.configure(state="disabled", text="Extracting...")
        self.play_callback(ep, self)