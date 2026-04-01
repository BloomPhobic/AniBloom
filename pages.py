import customtkinter as ctk
from styles import Colors, Fonts

class MainMenu(ctk.CTkFrame):
    def __init__(self, master, search_callback, history_callback, clear_history_callback):
        super().__init__(master, fg_color="transparent")
        self.search_callback = search_callback
        self.history_callback = history_callback

        title = ctk.CTkLabel(self, text="AniBloom", font=Fonts.TITLE, text_color=Colors.BRAND)
        title.pack(pady=(80, 10))

        sub = ctk.CTkLabel(self, text="Search for any anime to start watching", text_color=Colors.SUBTEXT, font=Fonts.BODY)
        sub.pack(pady=(0, 30))

        self.search_bar = ctk.CTkEntry(self, placeholder_text="e.g., Attack on Titan...", width=500, height=40, font=Fonts.BODY)
        self.search_bar.pack(pady=10)
        self.search_bar.bind("<Return>", self.handle_search)

        self.search_btn = ctk.CTkButton(self, text="Search", width=200, height=40, font=Fonts.BODY_BOLD, fg_color=Colors.PRIMARY, hover_color=Colors.PRIMARY_HOVER, command=self.handle_search)
        self.search_btn.pack(pady=20)

        self.history_container = ctk.CTkFrame(self, fg_color="transparent")
        self.history_container.pack(pady=(20, 0), fill="x", padx=100)
        
        self.history_top_bar = ctk.CTkFrame(self.history_container, fg_color="transparent")
        self.history_top_bar.pack(fill="x", pady=(0, 5))
        
        self.history_label = ctk.CTkLabel(self.history_top_bar, text="Your Library", font=Fonts.HEADER, text_color=Colors.TEXT)
        self.history_label.pack(side="left")
        
        self.clear_btn = ctk.CTkButton(self.history_top_bar, text="🗑️ Clear History", width=60, height=28, fg_color=Colors.ERROR, hover_color="#cc0000", font=Fonts.SMALL, command=clear_history_callback)
        self.clear_btn.pack(side="right")

        self.current_tab = "history"
        
        self.tab_nav_frame = ctk.CTkFrame(self.history_container, fg_color="transparent")
        self.tab_nav_frame.pack(fill="x", pady=(10, 5))

        self.tab_buttons_wrapper = ctk.CTkFrame(self.tab_nav_frame, fg_color="transparent")
        self.tab_buttons_wrapper.pack(anchor="center")

        # --- COMPOSITE HISTORY BUTTON ---
        self.btn_hist_frame = ctk.CTkFrame(self.tab_buttons_wrapper, fg_color=Colors.SURFACE, corner_radius=6, cursor="hand2")
        self.btn_hist_frame.pack(side="left", padx=5)
        
        self.lbl_hist_icon = ctk.CTkLabel(self.btn_hist_frame, text="🕒", font=("Roboto", 32), text_color=Colors.TEXT)
        self.lbl_hist_icon.pack(side="left", padx=(15, 5), pady=2)
        
        self.lbl_hist_text = ctk.CTkLabel(self.btn_hist_frame, text="Recent History", font=Fonts.BODY_BOLD, text_color=Colors.TEXT)
        self.lbl_hist_text.pack(side="left", padx=(0, 20), pady=10)

        # --- COMPOSITE FAVORITES BUTTON ---
        self.btn_fav_frame = ctk.CTkFrame(self.tab_buttons_wrapper, fg_color="transparent", corner_radius=6, cursor="hand2")
        self.btn_fav_frame.pack(side="left", padx=5)
        
        self.lbl_fav_icon = ctk.CTkLabel(self.btn_fav_frame, text="⭐", font=("Roboto", 40), text_color=Colors.SUBTEXT)
        self.lbl_fav_icon.pack(side="left", padx=(15, 5), pady=2)
        
        self.lbl_fav_text = ctk.CTkLabel(self.btn_fav_frame, text="Favorites", font=Fonts.BODY_BOLD, text_color=Colors.SUBTEXT)
        self.lbl_fav_text.pack(side="left", padx=(0, 20), pady=8)

        # --- BIND CLICKS & HOVER EFFECTS ---
        for w in [self.btn_hist_frame, self.lbl_hist_icon, self.lbl_hist_text]:
            w.bind("<Button-1>", lambda e: self.switch_tab("history"))
            w.bind("<Enter>", lambda e: self.btn_hist_frame.configure(fg_color=Colors.PRIMARY_HOVER) if self.current_tab == "history" else self.btn_hist_frame.configure(fg_color=Colors.SURFACE))
            w.bind("<Leave>", lambda e: self.btn_hist_frame.configure(fg_color=Colors.SURFACE) if self.current_tab == "history" else self.btn_hist_frame.configure(fg_color="transparent"))

        for w in [self.btn_fav_frame, self.lbl_fav_icon, self.lbl_fav_text]:
            w.bind("<Button-1>", lambda e: self.switch_tab("favorites"))
            w.bind("<Enter>", lambda e: self.btn_fav_frame.configure(fg_color=Colors.PRIMARY_HOVER) if self.current_tab == "favorites" else self.btn_fav_frame.configure(fg_color=Colors.SURFACE))
            w.bind("<Leave>", lambda e: self.btn_fav_frame.configure(fg_color=Colors.SURFACE) if self.current_tab == "favorites" else self.btn_fav_frame.configure(fg_color="transparent"))

        self.tab_content = ctk.CTkFrame(self.history_container, fg_color="transparent", height=250)
        self.tab_content.pack(fill="both", expand=True)

        self.history_scroll = ctk.CTkScrollableFrame(self.tab_content, fg_color="transparent")
        self.fav_scroll = ctk.CTkScrollableFrame(self.tab_content, fg_color="transparent")

        self.history_scroll.pack(fill="both", expand=True)

        # --- NEW: THE SIGNATURE ---
        # Anchored to the bottom right (se = south-east). Changed to BloomPhobic and Pure White!
        self.signature_label = ctk.CTkLabel(
            self, text="🌸 Crafted by BloomPhobic", 
            font=Fonts.SIGNATURE, text_color="#FFFFFF"
        )
        self.signature_label.place(relx=0.98, rely=0.98, anchor="se")

    def switch_tab(self, tab_name):
        self.current_tab = tab_name
        if tab_name == "history":
            self.btn_hist_frame.configure(fg_color=Colors.SURFACE)
            self.lbl_hist_icon.configure(text_color=Colors.TEXT)
            self.lbl_hist_text.configure(text_color=Colors.TEXT)
            
            self.btn_fav_frame.configure(fg_color="transparent")
            self.lbl_fav_icon.configure(text_color=Colors.SUBTEXT)
            self.lbl_fav_text.configure(text_color=Colors.SUBTEXT)
            
            self.fav_scroll.pack_forget()
            self.history_scroll.pack(fill="both", expand=True)
        else:
            self.btn_fav_frame.configure(fg_color=Colors.SURFACE)
            self.lbl_fav_icon.configure(text_color=Colors.ACCENT)
            self.lbl_fav_text.configure(text_color=Colors.ACCENT)
            
            self.btn_hist_frame.configure(fg_color="transparent")
            self.lbl_hist_icon.configure(text_color=Colors.SUBTEXT)
            self.lbl_hist_text.configure(text_color=Colors.SUBTEXT)
            
            self.history_scroll.pack_forget()
            self.fav_scroll.pack(fill="both", expand=True)

    def handle_search(self, event=None):
        query = self.search_bar.get().strip()
        if query:
            self.search_btn.configure(text="Scraping...", state="disabled")
            self.search_callback(query, self)

    def populate_history(self, history_data):
        for widget in self.history_scroll.winfo_children():
            widget.destroy()
            
        if not history_data:
            ctk.CTkLabel(self.history_scroll, text="Your watch history is empty.", text_color=Colors.SUBTEXT, font=Fonts.BODY).pack(pady=30)
            self.clear_btn.configure(state="disabled")
            return
            
        self.clear_btn.configure(state="normal")
            
        for item in history_data:
            name = item.get('name', 'Unknown')
            ep = item.get('episode', '1')
            
            btn = ctk.CTkButton(
                self.history_scroll, text=f" ▶   {name}   •   Ep {ep}", anchor="w",
                fg_color=Colors.SURFACE, hover_color=Colors.PRIMARY_HOVER,
                text_color=Colors.TEXT, font=Fonts.BODY,
                corner_radius=6, border_width=1, border_color=Colors.BORDER,
                height=38,
                command=lambda data=item: self.handle_history_click(data)
            )
            btn.pack(fill="x", pady=4, padx=8)

    def populate_favorites(self, fav_data):
        for widget in self.fav_scroll.winfo_children():
            widget.destroy()
            
        if not fav_data:
            ctk.CTkLabel(self.fav_scroll, text="No favorites yet. Go star some anime!", text_color=Colors.SUBTEXT, font=Fonts.BODY).pack(pady=30)
            return
            
        for item in fav_data:
            name = item.get('name', 'Unknown')
            
            btn = ctk.CTkButton(
                self.fav_scroll, text=f" ★   {name}", anchor="w",
                fg_color=Colors.SURFACE, hover_color=Colors.PRIMARY_HOVER,
                text_color=Colors.ACCENT, font=Fonts.BODY_BOLD,
                corner_radius=6, border_width=1, border_color=Colors.BORDER,
                height=38,
                command=lambda data=item: self.handle_history_click(data)
            )
            btn.pack(fill="x", pady=4, padx=8)

    def handle_history_click(self, item_data):
        self.history_label.configure(text=f"Loading '{item_data.get('name', '')}'...")
        self.history_callback(item_data)

class EpisodeMenu(ctk.CTkFrame):
    def __init__(self, master, back_callback, play_callback, download_callback, fav_callback):
        super().__init__(master, fg_color="transparent")
        self.play_callback = play_callback
        self.download_callback = download_callback
        self.fav_callback = fav_callback
        
        self.current_ep_page = 0
        self.eps_per_page = 28
        self.episodes_list = []
        self.watched_episodes = []
        self.total_episodes = 0
        
        self.download_mode = False
        self.selected_episodes = set()

        nav = ctk.CTkFrame(self, fg_color="transparent")
        nav.pack(fill="x", pady=10, padx=20)
        
        self.back_btn = ctk.CTkButton(
            nav, text="❮  Back to Results", width=60, font=("Roboto", 18, "bold"),
            fg_color="transparent", hover_color=Colors.PRIMARY_HOVER, text_color="#FFFFFF",
            command=back_callback
        )
        self.back_btn.pack(side="left")

        self.title_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.title_frame.pack(pady=(5, 10))
        
        self.title_label = ctk.CTkLabel(self.title_frame, text="Anime Name", font=Fonts.HEADER, text_color=Colors.TEXT, wraplength=600)
        self.title_label.pack(side="left", padx=10)
        
        self.fav_btn = ctk.CTkButton(
            self.title_frame, text="☆", width=40, font=("Roboto", 36),
            fg_color="transparent", hover_color=Colors.BG, text_color=Colors.SUBTEXT,
            command=self.handle_fav_click
        )
        self.fav_btn.pack(side="left")

        self.mode_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.mode_frame.pack(pady=5)
        
        self.toggle_mode_btn = ctk.CTkButton(
            self.mode_frame, text="⤓ Switch to Download Mode", font=Fonts.BODY_BOLD,
            fg_color="transparent", text_color="#FFFFFF", hover_color=Colors.PRIMARY_HOVER,
            border_width=1, border_color=Colors.BORDER, corner_radius=6,
            command=self.toggle_mode
        )
        self.toggle_mode_btn.pack(side="top", pady=5)
        
        self.dl_controls = ctk.CTkFrame(self.mode_frame, fg_color="transparent")
        
        self.select_all_btn = ctk.CTkButton(
            self.dl_controls, text="Select Page", width=100, font=Fonts.BODY,
            fg_color=Colors.SURFACE, hover_color=Colors.PRIMARY_HOVER, corner_radius=6,
            command=self.select_all_eps
        )
        self.select_all_btn.pack(side="left", padx=5)
        
        self.confirm_dl_btn = ctk.CTkButton(
            self.dl_controls, text="⬇️ Download Selected", width=160, font=Fonts.BODY_BOLD,
            fg_color=Colors.PRIMARY, hover_color=Colors.PRIMARY_HOVER,
            text_color=Colors.ACCENT, border_width=1, border_color=Colors.BORDER, corner_radius=6,
            command=self.handle_download
        )
        self.confirm_dl_btn.pack(side="left", padx=5)

        self.grid_container = ctk.CTkFrame(self, fg_color="transparent")
        self.grid_container.pack(pady=10)
        
        self.grid_frame = ctk.CTkFrame(self.grid_container, fg_color="transparent")
        self.grid_frame.pack()
        
        self.page_nav = ctk.CTkFrame(self.grid_container, fg_color="transparent")
        self.page_nav.pack(pady=15)
        
        self.prev_btn = ctk.CTkButton(self.page_nav, text="<", width=40, fg_color=Colors.SURFACE, hover_color=Colors.PRIMARY_HOVER, command=self.prev_page)
        self.prev_btn.pack(side="left", padx=10)
        self.page_label = ctk.CTkLabel(self.page_nav, text="Eps 1-28", font=Fonts.BODY, text_color=Colors.SUBTEXT)
        self.page_label.pack(side="left", padx=10)
        self.next_btn = ctk.CTkButton(self.page_nav, text=">", width=40, fg_color=Colors.SURFACE, hover_color=Colors.PRIMARY_HOVER, command=self.next_page)
        self.next_btn.pack(side="left", padx=10)

        self.watch_controls = ctk.CTkFrame(self, fg_color="transparent")
        self.watch_controls.pack(pady=5)
        
        ctk.CTkLabel(self.watch_controls, text="Episode:", font=Fonts.BODY, text_color=Colors.SUBTEXT).pack(side="left", padx=10)
        
        self.ep_input = ctk.CTkEntry(
            self.watch_controls, width=60, font=Fonts.BODY_BOLD, justify="center",
            fg_color=Colors.SURFACE, border_color=Colors.BORDER, text_color=Colors.TEXT
        )
        self.ep_input.insert(0, "1")
        self.ep_input.pack(side="left", padx=5)
        self.ep_input.bind("<Return>", self.handle_play)
        
        self.watch_btn = ctk.CTkButton(
            self.watch_controls, text="▶ Watch Now", font=Fonts.BODY_BOLD, width=140,
            fg_color=Colors.PRIMARY, hover_color=Colors.PRIMARY_HOVER,
            text_color=Colors.ACCENT, border_width=1, border_color=Colors.BORDER, corner_radius=6,
            command=self.handle_play
        )
        self.watch_btn.pack(side="left", padx=15)

        self.console = ctk.CTkTextbox(
            self, width=650, height=100, text_color=Colors.SUBTEXT,
            fg_color="transparent", border_width=1, border_color=Colors.BORDER, corner_radius=6
        )
        self.console.pack(pady=15)

    def handle_fav_click(self):
        is_now_fav = self.fav_callback()
        self.set_fav_visuals(is_now_fav)

    def set_fav_visuals(self, is_fav):
        if is_fav:
            self.fav_btn.configure(text="★", text_color=Colors.ACCENT)
        else:
            self.fav_btn.configure(text="☆", text_color=Colors.SUBTEXT)

    def toggle_mode(self):
        self.download_mode = not self.download_mode
        if self.download_mode:
            self.toggle_mode_btn.configure(text="✕ Cancel Download Mode", text_color=Colors.ERROR)
            self.watch_controls.pack_forget()
            self.dl_controls.pack(side="top", pady=5)
            self.log("ℹ️ Download Mode active. Click episodes to queue them.")
        else:
            self.toggle_mode_btn.configure(text="⤓ Switch to Download Mode", text_color="#FFFFFF")
            self.dl_controls.pack_forget()
            self.watch_controls.pack(pady=5)
            self.selected_episodes.clear()
            self.log("ℹ️ Returned to Watch Mode.")
        self.draw_grid()

    def select_all_eps(self):
        start_idx = self.current_ep_page * self.eps_per_page
        end_idx = min(start_idx + self.eps_per_page, self.total_episodes)
        
        for i in range(start_idx, end_idx):
            self.selected_episodes.add(self.episodes_list[i])
            
        self.draw_grid()
        self.log("✅ Selected all episodes on this page.")

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
                text_color = Colors.ACCENT
                border = Colors.ACCENT
            elif ep_str in self.watched_episodes:
                bg = "transparent"
                hover = Colors.SURFACE
                text_color = Colors.SUBTEXT
                border = Colors.BORDER
            else:
                bg = Colors.SURFACE
                hover = Colors.PRIMARY_HOVER
                text_color = Colors.TEXT
                border = Colors.BORDER

            btn = ctk.CTkButton(
                self.grid_frame, text=ep_str, width=48, height=42, font=Fonts.BODY_BOLD,
                fg_color=bg, hover_color=hover, text_color=text_color,
                border_width=1, border_color=border, corner_radius=6,
                command=lambda e=ep_str: self.grid_click(e)
            )
            row = i // cols
            col = i % cols
            btn.grid(row=row, column=col, padx=5, pady=5)

    def next_page(self):
        self.current_ep_page += 1
        self.draw_grid()

    def prev_page(self):
        if self.current_ep_page > 0:
            self.current_ep_page -= 1
            self.draw_grid()

    def setup(self, name, episodes_list, is_fav, watched_eps):
        self.episodes_list = [str(e) for e in episodes_list]
        self.watched_episodes = [str(e) for e in watched_eps]
        self.total_episodes = len(self.episodes_list)
        
        self.title_label.configure(text=name)
        self.set_fav_visuals(is_fav)
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
            self.ep_input.insert(0, self.episodes_list[0])
            
        self.current_ep_page = 0
        self.draw_grid()

    def log(self, text):
        self.console.insert("end", text + "\n")
        self.console.see("end")

    def handle_play(self, event=None):
        ep = self.ep_input.get().strip()
        if not ep:
            self.log("❌ ERROR: Please enter an episode number.")
            return
        self.watch_btn.configure(state="disabled", text="Extracting...")
        self.play_callback(ep, self)

class ResultsMenu(ctk.CTkFrame):
    def __init__(self, master, back_callback, select_callback):
        super().__init__(master, fg_color="transparent")
        self.select_callback = select_callback

        nav = ctk.CTkFrame(self, fg_color="transparent")
        nav.pack(fill="x", pady=10, padx=20)

        ctk.CTkButton(
            nav, text="❮  Back to Search", width=60, font=("Roboto", 18, "bold"),
            fg_color="transparent", hover_color=Colors.PRIMARY_HOVER, text_color="#FFFFFF",
            command=back_callback
        ).pack(side="left")

        self.title_label = ctk.CTkLabel(self, text="Search Results", font=Fonts.HEADER, text_color=Colors.TEXT)
        self.title_label.pack(pady=(10, 20))

        self.scroll_frame = ctk.CTkScrollableFrame(self, fg_color="transparent")
        self.scroll_frame.pack(pady=10, fill="both", expand=True, padx=40)

    def populate(self, query, results):
        self.title_label.configure(text=f"Results for '{query}'")
        for widget in self.scroll_frame.winfo_children():
            widget.destroy()
            
        for index, name in enumerate(results):
            btn = ctk.CTkButton(
                self.scroll_frame, text=f"  {index + 1}.   {name}", anchor="w",
                fg_color=Colors.SURFACE, hover_color=Colors.PRIMARY_HOVER,
                text_color=Colors.TEXT, font=Fonts.BODY,
                corner_radius=6, border_width=1, border_color=Colors.BORDER,
                height=42,
                command=lambda n=name, i=index: self.select_callback(n, i)
            )
            btn.pack(fill="x", pady=5, padx=10)

            btn.bind("<Button-4>", lambda e: self.scroll_frame._parent_canvas.yview_scroll(-1, "units"))
            btn.bind("<Button-5>", lambda e: self.scroll_frame._parent_canvas.yview_scroll(1, "units"))
            btn.bind("<MouseWheel>", lambda e: self.scroll_frame._parent_canvas.yview_scroll(int(-1*(e.delta/120)), "units"))

class SettingsWindow(ctk.CTkToplevel):
    def __init__(self, master, current_quality, current_path, save_callback, browse_callback):
        super().__init__(master)
        self.title("Settings")
        self.geometry("450x300")
        self.configure(fg_color=Colors.BG)
        self.attributes("-topmost", True)
        self.resizable(False, False)

        self.update_idletasks()
        x = (self.winfo_screenwidth() // 2) - (450 // 2)
        y = (self.winfo_screenheight() // 2) - (300 // 2)
        self.geometry(f"+{x}+{y}")

        self.bind("<Escape>", lambda event: self.destroy())

        title = ctk.CTkLabel(self, text="⚙️ Preferences", font=Fonts.HEADER, text_color=Colors.TEXT)
        title.pack(pady=(20, 20))

        qual_frame = ctk.CTkFrame(self, fg_color="transparent")
        qual_frame.pack(fill="x", padx=30, pady=10)
        ctk.CTkLabel(qual_frame, text="Preferred Quality:", font=Fonts.BODY_BOLD, text_color=Colors.TEXT).pack(side="left")
        
        self.quality_var = ctk.StringVar(value=current_quality)
        self.quality_menu = ctk.CTkOptionMenu(qual_frame, values=["1080p", "720p", "480p", "Best Available"], variable=self.quality_var, fg_color=Colors.SURFACE, button_color=Colors.PRIMARY, button_hover_color=Colors.PRIMARY_HOVER)
        self.quality_menu.pack(side="right")

        loc_frame = ctk.CTkFrame(self, fg_color="transparent")
        loc_frame.pack(fill="x", padx=30, pady=10)
        ctk.CTkLabel(loc_frame, text="Download Location:", font=Fonts.BODY_BOLD, text_color=Colors.TEXT).pack(anchor="w")
        
        path_controls = ctk.CTkFrame(loc_frame, fg_color="transparent")
        path_controls.pack(fill="x", pady=5)
        
        self.path_entry = ctk.CTkEntry(path_controls, state="disabled", fg_color=Colors.SURFACE)
        self.path_entry.pack(side="left", fill="x", expand=True, padx=(0, 10))
        self.update_path_display(current_path)

        self.browse_btn = ctk.CTkButton(path_controls, text="Browse...", width=80, fg_color=Colors.SECONDARY, hover_color=Colors.SECONDARY_HOVER, command=lambda: browse_callback(self))
        self.browse_btn.pack(side="right")

        self.save_btn = ctk.CTkButton(self, text="Save Settings", font=Fonts.BODY_BOLD, fg_color=Colors.PRIMARY, hover_color=Colors.PRIMARY_HOVER, command=lambda: save_callback(self.quality_var.get(), self))
        self.save_btn.pack(side="bottom", pady=20)

    def update_path_display(self, path):
        self.path_entry.configure(state="normal")
        self.path_entry.delete(0, "end")
        self.path_entry.insert(0, path)
        self.path_entry.configure(state="disabled")