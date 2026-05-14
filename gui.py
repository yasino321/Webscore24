import os
import csv
import threading
import customtkinter as ctk
from tkinter import messagebox, filedialog
from dotenv import load_dotenv, set_key
from finder import find_leads, add_manual
from free_finder import find_leads_free
from analyser import analyse
from generator import generate
from reporter import create_report

# Appearance
ctk.set_appearance_mode("Dark")
ctk.set_default_color_theme("blue")

class WebScoreGUI(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("WebScore Pro - Website Analyse & Sales Tool")
        self.geometry("1100x750")

        # Load .env
        load_dotenv()
        self.env_path = ".env"
        if not os.path.exists(self.env_path):
            with open(self.env_path, "w") as f:
                f.write("")

        # Create sidebar
        self.sidebar_frame = ctk.CTkFrame(self, width=160, corner_radius=0)
        self.sidebar_frame.grid(row=0, column=0, rowspan=4, sticky="nsew")
        self.sidebar_frame.grid_rowconfigure(4, weight=1)

        self.logo_label = ctk.CTkLabel(self.sidebar_frame, text="WebScore", font=ctk.CTkFont(size=20, weight="bold"))
        self.logo_label.grid(row=0, column=0, padx=20, pady=(20, 10))

        self.btn_find = ctk.CTkButton(self.sidebar_frame, text="Leads finden", command=self.show_find)
        self.btn_find.grid(row=1, column=0, padx=20, pady=10)

        self.btn_analyse = ctk.CTkButton(self.sidebar_frame, text="Analysieren", command=self.show_analyse)
        self.btn_analyse.grid(row=2, column=0, padx=20, pady=10)

        self.btn_settings = ctk.CTkButton(self.sidebar_frame, text="Einstellungen", command=self.show_settings)
        self.btn_settings.grid(row=3, column=0, padx=20, pady=10)

        self.mode_var = ctk.StringVar(value="Premium")
        self.mode_switch = ctk.CTkSwitch(self.sidebar_frame, text="Free Mode", variable=self.mode_var, onvalue="Free", offvalue="Premium")
        self.mode_switch.grid(row=5, column=0, padx=20, pady=20)

        # Main content area
        self.main_frame = ctk.CTkFrame(self, corner_radius=0, fg_color="transparent")
        self.main_frame.grid(row=0, column=1, sticky="nsew", padx=20, pady=20)
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        self.show_find()

    def clear_main_frame(self):
        for widget in self.main_frame.winfo_children():
            widget.destroy()

    def show_find(self):
        self.clear_main_frame()

        mode = self.mode_var.get()
        title_text = "Neue Leads finden (Kostenlos)" if mode == "Free" else "Neue Leads finden (Premium)"
        title = ctk.CTkLabel(self.main_frame, text=title_text, font=ctk.CTkFont(size=24, weight="bold"))
        title.pack(pady=20)

        input_frame = ctk.CTkFrame(self.main_frame)
        input_frame.pack(padx=20, pady=20, fill="x")

        self.entry_branche = ctk.CTkEntry(input_frame, placeholder_text="Branche (z.B. Friseur)")
        self.entry_branche.pack(padx=20, pady=10, fill="x")

        self.entry_ort = ctk.CTkEntry(input_frame, placeholder_text="Ort (z.B. Berlin)")
        self.entry_ort.pack(padx=20, pady=10, fill="x")

        if mode == "Premium":
            self.entry_radius = ctk.CTkEntry(input_frame, placeholder_text="Radius in Metern (Default: 2000)")
            self.entry_radius.pack(padx=20, pady=10, fill="x")

        btn_run_find = ctk.CTkButton(self.main_frame, text="Suche starten", command=self.run_find_thread)
        btn_run_find.pack(pady=20)

        self.log_text = ctk.CTkTextbox(self.main_frame, height=200)
        self.log_text.pack(padx=20, pady=20, fill="both", expand=True)

    def run_find_thread(self):
        branche = self.entry_branche.get()
        ort = self.entry_ort.get()
        mode = self.mode_var.get()

        if not branche or not ort:
            messagebox.showwarning("Eingabe fehlt", "Bitte Branche und Ort angeben.")
            return

        self.log(f"Suche wird gestartet ({mode} Modus)...")
        if mode == "Free":
            threading.Thread(target=self.run_find_free, args=(branche, ort), daemon=True).start()
        else:
            radius = self.entry_radius.get() or "2000"
            threading.Thread(target=self.run_find_premium, args=(branche, ort, int(radius)), daemon=True).start()

    def run_find_premium(self, branche, ort, radius):
        try:
            leads = find_leads(branche, ort, radius)
            self.log(f"Premium Suche beendet. {len(leads)} Leads gefunden.")
            messagebox.showinfo("Erfolg", f"{len(leads)} Leads gefunden.")
        except Exception as e:
            self.log(f"Fehler: {e}")
            messagebox.showerror("Fehler", str(e))

    def run_find_free(self, branche, ort):
        try:
            leads = find_leads_free(branche, ort)
            self.log(f"Kostenlose Suche beendet. {len(leads)} Leads gefunden.")
            messagebox.showinfo("Erfolg", f"{len(leads)} Leads gefunden.")
        except Exception as e:
            self.log(f"Fehler: {e}")
            messagebox.showerror("Fehler", str(e))

    def show_analyse(self):
        self.clear_main_frame()

        title = ctk.CTkLabel(self.main_frame, text="Leads analysieren & generieren", font=ctk.CTkFont(size=24, weight="bold"))
        title.pack(pady=20)

        btn_frame = ctk.CTkFrame(self.main_frame)
        btn_frame.pack(padx=20, pady=10, fill="x")

        btn_load = ctk.CTkButton(btn_frame, text="Leads aus leads.csv laden", command=self.load_leads)
        btn_load.pack(side="left", padx=10, pady=10)

        self.scroll_frame = ctk.CTkScrollableFrame(self.main_frame, label_text="Verfügbare Leads")
        self.scroll_frame.pack(padx=20, pady=20, fill="both", expand=True)

        self.load_leads()

    def load_leads(self):
        for widget in self.scroll_frame.winfo_children():
            widget.destroy()

        if not os.path.exists("leads.csv"):
            ctk.CTkLabel(self.scroll_frame, text="Keine leads.csv gefunden.").pack()
            return

        with open("leads.csv", mode='r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                lead_frame = ctk.CTkFrame(self.scroll_frame)
                lead_frame.pack(fill="x", padx=10, pady=5)

                label = ctk.CTkLabel(lead_frame, text=f"{row['name']} ({row['url']}) - Status: {row['status']}")
                label.pack(side="left", padx=10)

                btn_gen = ctk.CTkButton(lead_frame, text="Report generieren", width=120,
                                       command=lambda r=row: self.run_gen_thread(r))
                btn_gen.pack(side="right", padx=10, pady=5)

    def run_gen_thread(self, lead_row):
        threading.Thread(target=self.run_gen, args=(lead_row,), daemon=True).start()

    def run_gen(self, lead_row):
        try:
            print(f"Starte Prozess für {lead_row['name']}...")
            score = analyse(lead_row['url'])
            if not score:
                messagebox.showerror("Fehler", "Analyse fehlgeschlagen.")
                return

            safe_url = lead_row['url'].replace('https://', '').replace('http://', '').replace('/', '_').replace('?', '_').replace('&', '_').replace('=', '_')
            screenshot_alt = f"output/{safe_url}.png"

            branche = "Sonstige"

            html_path = generate(lead_row['url'], branche)
            pdf_path = create_report(lead_row['name'], branche, score, screenshot_alt, html_path)

            messagebox.showinfo("Erfolg", f"Report erstellt: {pdf_path}")
            self.load_leads()
        except Exception as e:
            messagebox.showerror("Fehler", str(e))

    def show_settings(self):
        self.clear_main_frame()

        title = ctk.CTkLabel(self.main_frame, text="Einstellungen (API Keys)", font=ctk.CTkFont(size=24, weight="bold"))
        title.pack(pady=20)

        keys = ["GEMINI_API_KEY", "BIG_PICKLE_API_KEY", "OPENAI_API_KEY", "GOOGLE_PLACES_API_KEY"]
        self.entries = {}

        for key in keys:
            frame = ctk.CTkFrame(self.main_frame)
            frame.pack(padx=20, pady=10, fill="x")

            lbl = ctk.CTkLabel(frame, text=key, width=200, anchor="w")
            lbl.pack(side="left", padx=10)

            entry = ctk.CTkEntry(frame, placeholder_text="Key eingeben...")
            entry.insert(0, os.getenv(key) or "")
            entry.pack(side="right", fill="x", expand=True, padx=10)
            self.entries[key] = entry

        ctk.CTkLabel(self.main_frame, text="*Für den kostenlosen Modus wird nur der GEMINI_API_KEY benötigt.",
                     font=ctk.CTkFont(size=12, slant="italic")).pack(pady=10)

        btn_save = ctk.CTkButton(self.main_frame, text="Speichern", command=self.save_settings)
        btn_save.pack(pady=20)

    def save_settings(self):
        for key, entry in self.entries.items():
            val = entry.get()
            set_key(self.env_path, key, val)
            os.environ[key] = val
        messagebox.showinfo("Erfolg", "Einstellungen gespeichert.")

    def log(self, msg):
        self.log_text.insert("end", f"{msg}\n")
        self.log_text.see("end")

if __name__ == "__main__":
    app = WebScoreGUI()
    app.mainloop()
