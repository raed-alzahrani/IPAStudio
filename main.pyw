import os
import sys
import json
import shutil
import zipfile
import threading
import plistlib
import subprocess
import tkinter as tk
from tkinter import filedialog, messagebox

# 1. Dependency Auto-Installer
REQUIRED_LIBS = {
    "customtkinter": "customtkinter",
    "PIL": "pillow",
    "tkinterdnd2": "tkinterdnd2"
}

missing = []
for mod, pkg in REQUIRED_LIBS.items():
    try:
        __import__(mod)
    except ImportError:
        missing.append(pkg)

if missing:
    root = tk.Tk()
    root.title("Requirements Setup")
    root.geometry("450x260")
    root.resizable(False, False)
    root.configure(bg="#0b0f17")

    ws = root.winfo_screenwidth()
    hs = root.winfo_screenheight()
    root.geometry(f"450x260+{int((ws-450)/2)}+{int((hs-260)/2)}")

    tk.Label(root, text="Missing Packages Detected", font=("Segoe UI", 12, "bold"), fg="#f87171", bg="#0b0f17").pack(pady=(20, 5))
    tk.Label(root, text="Click install to automatically set up dependencies:", font=("Segoe UI", 9), fg="#94a3b8", bg="#0b0f17").pack()

    box = tk.Frame(root, bg="#121926", bd=1, relief="solid")
    box.pack(fill="x", padx=30, pady=10)
    for pkg in missing:
        tk.Label(box, text=f"• {pkg}", font=("Consolas", 10, "bold"), fg="#10b981", bg="#121926").pack(anchor="w", padx=12, pady=2)

    def install_pkgs():
        py_dir = os.path.dirname(sys.executable)
        py_exe = os.path.join(py_dir, "python.exe")
        if not os.path.exists(py_exe):
            py_exe = sys.executable

        script_path = os.path.abspath(__file__)
        pkgs_str = " ".join(missing)
        
        bat_cmd = f"""@echo off
title Installing Dependencies...
"{py_exe}" -m pip install --upgrade pip
"{py_exe}" -m pip install {pkgs_str}
if %ERRORLEVEL% NEQ 0 (
    echo [!] Failed to install dependencies.
    pause
    exit /b %ERRORLEVEL%
)
start "" "{py_exe}" "{script_path}"
exit 0
"""
        bat_file = os.path.join(os.environ.get("TEMP", "."), "_install_ipa_deps.bat")
        with open(bat_file, "w", encoding="utf-8") as f:
            f.write(bat_cmd)
        
        root.destroy()
        subprocess.Popen(f'cmd.exe /c "{bat_file}"', shell=True)
        os._exit(0)

    btns = tk.Frame(root, bg="#0b0f17")
    btns.pack(fill="x", padx=30, pady=(10, 15))
    tk.Button(btns, text="Cancel", font=("Segoe UI", 9), bg="#1e293b", fg="#fff", bd=0, padx=14, pady=5, command=lambda: (root.destroy(), os._exit(0))).pack(side="left")
    tk.Button(btns, text="Install Packages", font=("Segoe UI", 9, "bold"), bg="#10b981", fg="#042f2e", bd=0, padx=14, pady=5, command=install_pkgs).pack(side="right")
    
    root.mainloop()
    sys.exit()

from PIL import Image
import customtkinter as ctk
from tkinterdnd2 import TkinterDnD, DND_FILES

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
CONFIG_PATH = os.path.join(BASE_DIR, "ipa_suite_config.json")
ICON_PATH = os.path.join(BASE_DIR, "app_icon.ico")

IMAGE_FORMATS = (('Images', '*.png;*.jpg;*.jpeg;*.webp;*.bmp;*.ico'), ('All Files', '*.*'))

FONT_PROFILES = {
    "Futuristic (Bahnschrift)": {
        "title": ("Bahnschrift", 14, "bold"),
        "ui_bold": ("Bahnschrift", 11, "bold"),
        "ui_sm": ("Bahnschrift", 10, "bold"),
        "row_main": ("Bahnschrift", 11, "bold"),
        "mono": ("Consolas", 10, "bold")
    },
    "Modern Heavy (Segoe UI)": {
        "title": ("Segoe UI", 14, "bold"),
        "ui_bold": ("Segoe UI", 11, "bold"),
        "ui_sm": ("Segoe UI", 10, "bold"),
        "row_main": ("Segoe UI", 11, "bold"),
        "mono": ("Consolas", 10, "bold")
    },
    "Cyber Terminal (Cascadia Mono)": {
        "title": ("Cascadia Mono", 13, "bold"),
        "ui_bold": ("Cascadia Mono", 10, "bold"),
        "ui_sm": ("Cascadia Mono", 9, "bold"),
        "row_main": ("Cascadia Mono", 10, "bold"),
        "mono": ("Cascadia Mono", 9, "bold")
    }
}

THEMES = {
    "Emerald": {
        "primary": "#10b981", "hover": "#059669", "btn_bg": "#064e3b", "btn_hover": "#047857",
        "menu_bg": "#064e3b"
    },
    "Nordic Blue": {
        "primary": "#38bdf8", "hover": "#0ea5e9", "btn_bg": "#0c4a6e", "btn_hover": "#0369a1",
        "menu_bg": "#0c4a6e"
    },
    "Amethyst": {
        "primary": "#c084fc", "hover": "#9333ea", "btn_bg": "#581c87", "btn_hover": "#6b21a8",
        "menu_bg": "#581c87"
    }
}

def convert_to_icon(src_image, out_icon):
    try:
        img = Image.open(src_image).convert("RGBA")
        dim = min(img.size)
        left = (img.width - dim) // 2
        top = (img.height - dim) // 2
        cropped = img.crop((left, top, left + dim, top + dim))
        cropped.save(out_icon, format="ICO", sizes=[(256, 256), (128, 128), (64, 64), (48, 48), (32, 32), (16, 16)])
        return True
    except Exception: return False

def create_shortcut(target, destination, icon_path=None):
    try:
        working_dir = os.path.dirname(target)
        icon_line = f'oLink.IconLocation = "{icon_path}"' if (icon_path and os.path.exists(icon_path)) else ""
        vbs_script = f'''
        Set oWS = WScript.CreateObject("WScript.Shell")
        sLinkFile = "{destination}"
        Set oLink = oWS.CreateShortcut(sLinkFile)
        oLink.TargetPath = "{target}"
        oLink.WorkingDirectory = "{working_dir}"
        oLink.Description = "IPA Studio"
        {icon_line}
        oLink.Save
        '''
        vbs_path = os.path.join(os.environ.get("TEMP", os.path.expanduser("~")), "_make_shortcut.vbs")
        with open(vbs_path, "w", encoding="utf-8") as f:
            f.write(vbs_script)
            
        subprocess.run(["wscript", vbs_path], creationflags=0x08000000 if sys.platform == "win32" else 0)
        if os.path.exists(vbs_path): os.remove(vbs_path)
        return os.path.exists(destination)
    except Exception: return False

class CodeUpdateDialog(ctk.CTkToplevel):
    def __init__(self, parent, target_file, on_success, theme_name="Emerald", appearance_mode="Dark"):
        super().__init__(parent)
        self.title("Script Updater")
        self.geometry("840x600")
        self.target_file = target_file
        self.on_success = on_success
        self.palette = THEMES.get(theme_name, THEMES["Emerald"])
        
        self.configure(fg_color="#0b0f17" if appearance_mode == "Dark" else "#e2e8f0")
        self.transient(parent)
        self.grab_set()

        pri = self.palette["primary"]
        txt_main = "#ffffff" if appearance_mode == "Dark" else "#0f172a"
        inner_bg = "#080c12" if appearance_mode == "Dark" else "#f1f5f9"

        header_box = ctk.CTkFrame(self, fg_color="transparent")
        header_box.pack(fill="x", padx=20, pady=(15, 6))

        ctk.CTkLabel(header_box, text="Live Code Inspector & In-App Updater:", font=("Segoe UI", 12, "bold"), text_color=pri).pack(side="left")

        actions_box = ctk.CTkFrame(header_box, fg_color="transparent")
        actions_box.pack(side="right")

        ctk.CTkButton(actions_box, text="📋 Copy Code", width=120, height=28, font=("Segoe UI", 11, "bold"), fg_color="#1e293b", hover_color="#334155", text_color="#ffffff", command=self.copy_code).pack(side="left", padx=(0, 6))
        ctk.CTkButton(actions_box, text="📥 Paste Code", width=120, height=28, font=("Segoe UI", 11, "bold"), fg_color=self.palette["btn_bg"], hover_color=self.palette["hover"], text_color="#ffffff", command=self.paste_code).pack(side="left")

        self.editor = ctk.CTkTextbox(self, font=("Consolas", 11), fg_color=inner_bg, border_color=pri, border_width=1, text_color=txt_main, undo=True)
        self.editor.pack(fill="both", expand=True, padx=20, pady=6)

        try:
            with open(self.target_file, "r", encoding="utf-8") as f:
                self.editor.insert("1.0", f.read())
        except Exception: pass

        self.editor.bind("<Control-v>", lambda _: self.paste_code() or "break")
        self.editor.bind("<Control-V>", lambda _: self.paste_code() or "break")

        actions = ctk.CTkFrame(self, fg_color="transparent")
        actions.pack(fill="x", padx=20, pady=(10, 15))

        ctk.CTkButton(actions, text="Cancel", width=90, font=("Segoe UI", 11, "bold"), fg_color="#334155", command=self.destroy).pack(side="left")
        ctk.CTkButton(actions, text="Apply & Restart Application", font=("Segoe UI", 12, "bold"), fg_color=self.palette["btn_bg"], hover_color=self.palette["btn_hover"], border_width=1, border_color=pri, text_color="#ffffff", command=self.apply).pack(side="right", fill="x", expand=True, padx=(10, 0))

    def copy_code(self):
        try:
            with open(self.target_file, "r", encoding="utf-8") as f: code_data = f.read()
            self.clipboard_clear()
            self.clipboard_append(code_data)
            self.update()
            messagebox.showinfo("Clipboard", "Code copied to clipboard!")
        except Exception as e: messagebox.showerror("Error", str(e))

    def paste_code(self):
        try:
            text = self.clipboard_get()
            if text:
                self.editor.delete("1.0", "end")
                self.editor.insert("1.0", text)
        except Exception as e: messagebox.showwarning("Warning", str(e))

    def apply(self):
        new_code = self.editor.get("1.0", "end-1c").strip()
        if len(new_code) < 50 or "import" not in new_code:
            messagebox.showerror("Error", "Invalid script code.")
            return
        try:
            with open(self.target_file, 'w', encoding='utf-8') as f: f.write(new_code)
            self.destroy()
            self.on_success()
        except Exception as e: messagebox.showerror("Write Error", str(e))

class IPAToolkitApp(ctk.CTk, TkinterDnD.DnDWrapper):
    def __init__(self):
        super().__init__()
        # Correctly initialize DnD Wrapper for CustomTkinter
        self.TkdndVersion = TkinterDnD._require(self)
        
        self.title("IPA Studio")
        self.minsize(720, 520)

        self.config = self.load_config()
        self.current_theme = self.config.get("theme", "Emerald")
        if self.current_theme not in THEMES: self.current_theme = "Emerald"

        self.current_font = self.config.get("font_profile", "Futuristic (Bahnschrift)")
        if self.current_font not in FONT_PROFILES: self.current_font = "Futuristic (Bahnschrift)"

        self.appearance_mode = self.config.get("appearance", "Dark")
        ctk.set_appearance_mode(self.appearance_mode)
        
        if os.path.exists(ICON_PATH):
            try: self.iconbitmap(ICON_PATH)
            except Exception: pass

        saved_geom = self.config.get("geometry", "780x580")
        try: self.geometry(saved_geom)
        except Exception: self.geometry("780x580")

        self.ipa_path = ""
        self.injected_dylib_path = ""
        self.temp_dir = os.path.join(os.environ.get("TEMP", BASE_DIR), "_ipa_workspace")
        self.app_dir = ""
        self.binary_path = ""
        self.plist_path = ""
        self.plist_data = {}

        self._apply_appearance_backgrounds()
        self.setup_ui()
        self.apply_theme(self.current_theme)
        self.apply_font(self.current_font)

        # Register Drag & Drop on the window
        try:
            self.drop_target_register(DND_FILES)
            self.dnd_bind('<<Drop>>', self.on_global_drop)
        except Exception:
            pass

        self.protocol("WM_DELETE_WINDOW", self.on_close)

    def load_config(self):
        defaults = {
            "geometry": "780x580", "font_profile": "Futuristic (Bahnschrift)",
            "theme": "Emerald", "appearance": "Dark", "patch_unity": True, "clean_sig": True,
            "enable_files": True, "allow_http": False
        }
        if os.path.exists(CONFIG_PATH):
            try:
                with open(CONFIG_PATH, 'r', encoding='utf-8') as f: defaults.update(json.load(f))
            except Exception: pass
        return defaults

    def save_config(self):
        self.config = {
            "geometry": self.geometry(), "font_profile": self.current_font,
            "theme": self.current_theme, "appearance": self.appearance_mode,
            "patch_unity": self.unity_var.get(), "clean_sig": self.sig_var.get(),
            "enable_files": self.files_var.get(), "allow_http": self.http_var.get()
        }
        try:
            with open(CONFIG_PATH, 'w', encoding='utf-8') as f: json.dump(self.config, f, indent=2)
        except Exception: pass

    def on_close(self):
        if os.path.exists(self.temp_dir):
            try: shutil.rmtree(self.temp_dir)
            except Exception: pass
        self.save_config()
        self.destroy()

    def restart_app(self):
        self.save_config()
        script = os.path.abspath(__file__)
        subprocess.Popen([sys.executable.replace("python.exe", "pythonw.exe"), script], creationflags=0x08000000 if sys.platform == "win32" else 0)
        self.destroy()
        sys.exit()

    def _apply_appearance_backgrounds(self):
        if self.appearance_mode == "Dark":
            self.configure(fg_color="#0b0f17")
            self.card_bg = "#121926"
            self.inner_bg = "#080c12"
            self.panel_border = "#1f293d"
            self.text_main = "#f8fafc"
            self.text_muted = "#94a3b8"
        else:
            self.configure(fg_color="#f1f5f9")
            self.card_bg = "#ffffff"
            self.inner_bg = "#f8fafc"
            self.panel_border = "#cbd5e1"
            self.text_main = "#0f172a"
            self.text_muted = "#64748b"

    def setup_ui(self):
        # Header
        self.header = ctk.CTkFrame(self, fg_color=self.card_bg, corner_radius=10, border_width=1, border_color=self.panel_border)
        self.header.pack(fill="x", padx=10, pady=(8, 3))

        top_row = ctk.CTkFrame(self.header, fg_color="transparent")
        top_row.pack(fill="x", padx=8, pady=5)

        self.app_title = ctk.CTkLabel(top_row, text="IPA Studio")
        self.app_title.pack(side="left", padx=4)

        ctrls = ctk.CTkFrame(top_row, fg_color="transparent")
        ctrls.pack(side="right")

        self.btn_shortcut = ctk.CTkButton(ctrls, text="Shortcut", width=70, height=26, fg_color="#1e293b", hover_color="#334155", command=self.create_desktop_shortcut)
        self.btn_shortcut.pack(side="left", padx=2)

        self.btn_icon = ctk.CTkButton(ctrls, text="Icon", width=55, height=26, fg_color="#1e293b", hover_color="#334155", command=self.update_icon)
        self.btn_icon.pack(side="left", padx=2)

        self.btn_update = ctk.CTkButton(ctrls, text="Update", width=65, height=26, fg_color="#0369a1", hover_color="#0284c7", command=lambda: CodeUpdateDialog(self, os.path.abspath(__file__), self.restart_app, self.current_theme, self.appearance_mode))
        self.btn_update.pack(side="left", padx=2)

        self.font_picker = ctk.CTkOptionMenu(ctrls, values=list(FONT_PROFILES.keys()), width=140, height=26, command=self.handle_font_change)
        self.font_picker.set(self.current_font)
        self.font_picker.pack(side="left", padx=2)

        self.theme_picker = ctk.CTkOptionMenu(ctrls, values=list(THEMES.keys()), width=100, height=26, command=self.handle_theme_change)
        self.theme_picker.set(self.current_theme)
        self.theme_picker.pack(side="left", padx=2)

        self.btn_mode_toggle = ctk.CTkButton(ctrls, text="Dark" if self.appearance_mode == "Dark" else "Light", width=55, height=26, fg_color="#1e293b", hover_color="#334155", command=self.toggle_appearance)
        self.btn_mode_toggle.pack(side="left", padx=2)

        # File Selection Bar
        self.file_frame = ctk.CTkFrame(self, fg_color=self.card_bg, corner_radius=8, border_width=1, border_color=self.panel_border)
        self.file_frame.pack(fill="x", padx=10, pady=3)

        self.lbl_file = ctk.CTkLabel(self.file_frame, text="IPA Target:", text_color=self.text_muted)
        self.lbl_file.pack(side="left", padx=(10, 4), pady=5)

        self.entry_ipa = ctk.CTkEntry(self.file_frame, height=28, fg_color=self.inner_bg, border_color=self.panel_border, text_color=self.text_main, placeholder_text="Drag & drop .ipa anywhere in this window...")
        self.entry_ipa.pack(side="left", fill="x", expand=True, padx=4, pady=5)

        self.btn_browse = ctk.CTkButton(self.file_frame, text="Browse", width=80, height=28, fg_color="#1e293b", hover_color="#334155", command=self.choose_ipa)
        self.btn_browse.pack(side="right", padx=(4, 8), pady=5)

        # Config Area
        self.content_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.content_frame.pack(fill="x", padx=10, pady=3)
        self.content_frame.grid_columnconfigure((0, 1), weight=1)

        # Left: Metadata
        self.meta_card = ctk.CTkFrame(self.content_frame, fg_color=self.card_bg, corner_radius=8, border_width=1, border_color=self.panel_border)
        self.meta_card.grid(row=0, column=0, sticky="nsew", padx=(0, 3), pady=0)

        ctk.CTkLabel(self.meta_card, text="Metadata & Version Spoofing:", anchor="w").pack(fill="x", padx=10, pady=(6, 2))

        ver_box = ctk.CTkFrame(self.meta_card, fg_color="transparent")
        ver_box.pack(fill="x", padx=8, pady=2)
        ver_box.grid_columnconfigure((0, 1), weight=1)

        self.ent_curr_ver = ctk.CTkEntry(ver_box, height=26, state="disabled", placeholder_text="Old Version", fg_color=self.inner_bg, border_color=self.panel_border)
        self.ent_curr_ver.grid(row=0, column=0, sticky="ew", padx=(0, 2))
        self.ent_new_ver = ctk.CTkEntry(ver_box, height=26, placeholder_text="New Ver (e.g. 1.1.4)", fg_color=self.inner_bg, border_color=self.panel_border)
        self.ent_new_ver.grid(row=0, column=1, sticky="ew", padx=(2, 0))

        bld_box = ctk.CTkFrame(self.meta_card, fg_color="transparent")
        bld_box.pack(fill="x", padx=8, pady=2)
        bld_box.grid_columnconfigure((0, 1), weight=1)

        self.ent_curr_build = ctk.CTkEntry(bld_box, height=26, state="disabled", placeholder_text="Old Build", fg_color=self.inner_bg, border_color=self.panel_border)
        self.ent_curr_build.grid(row=0, column=0, sticky="ew", padx=(0, 2))
        self.ent_new_build = ctk.CTkEntry(bld_box, height=26, placeholder_text="New Build (101040)", fg_color=self.inner_bg, border_color=self.panel_border)
        self.ent_new_build.grid(row=0, column=1, sticky="ew", padx=(2, 0))

        self.ent_display_name = ctk.CTkEntry(self.meta_card, height=26, placeholder_text="Display Name", fg_color=self.inner_bg, border_color=self.panel_border)
        self.ent_display_name.pack(fill="x", padx=8, pady=2)

        self.ent_bundle_id = ctk.CTkEntry(self.meta_card, height=26, placeholder_text="Bundle ID (Duplicate App)", fg_color=self.inner_bg, border_color=self.panel_border)
        self.ent_bundle_id.pack(fill="x", padx=8, pady=(2, 6))

        # Right: Injection & Options
        self.dylib_card = ctk.CTkFrame(self.content_frame, fg_color=self.card_bg, corner_radius=8, border_width=1, border_color=self.panel_border)
        self.dylib_card.grid(row=0, column=1, sticky="nsew", padx=(3, 0), pady=0)

        ctk.CTkLabel(self.dylib_card, text="Injection & Tweaks:", anchor="w").pack(fill="x", padx=10, pady=(6, 2))

        inj_box = ctk.CTkFrame(self.dylib_card, fg_color="transparent")
        inj_box.pack(fill="x", padx=8, pady=2)
        self.entry_inject = ctk.CTkEntry(inj_box, height=26, placeholder_text="Inject .dylib / .deb (Optional)", fg_color=self.inner_bg, border_color=self.panel_border)
        self.entry_inject.pack(side="left", fill="x", expand=True, padx=(0, 3))

        self.btn_browse_dylib = ctk.CTkButton(inj_box, text="Pick", width=55, height=26, fg_color="#1e293b", hover_color="#334155", command=self.choose_dylib)
        self.btn_browse_dylib.pack(side="right")

        opts_grid = ctk.CTkFrame(self.dylib_card, fg_color="transparent")
        opts_grid.pack(fill="x", padx=8, pady=(6, 2))
        opts_grid.grid_columnconfigure((0, 1), weight=1)

        self.unity_var = ctk.BooleanVar(value=self.config.get("patch_unity", True))
        self.chk_unity = ctk.CTkCheckBox(opts_grid, text="Patch Unity Assets", variable=self.unity_var, command=self.save_config)
        self.chk_unity.grid(row=0, column=0, sticky="w", pady=3)

        self.files_var = ctk.BooleanVar(value=self.config.get("enable_files", True))
        self.chk_files = ctk.CTkCheckBox(opts_grid, text="Enable Files App Sharing", variable=self.files_var, command=self.save_config)
        self.chk_files.grid(row=0, column=1, sticky="w", pady=3)

        self.sig_var = ctk.BooleanVar(value=self.config.get("clean_sig", True))
        self.chk_sig = ctk.CTkCheckBox(opts_grid, text="Clean Signatures & Profiles", variable=self.sig_var, command=self.save_config)
        self.chk_sig.grid(row=1, column=0, sticky="w", pady=3)

        self.http_var = ctk.BooleanVar(value=self.config.get("allow_http", False))
        self.chk_http = ctk.CTkCheckBox(opts_grid, text="Allow HTTP Traffic", variable=self.http_var, command=self.save_config)
        self.chk_http.grid(row=1, column=1, sticky="w", pady=3)

        # Log Window
        self.progress_bar = ctk.CTkProgressBar(self, height=6, corner_radius=3)
        self.progress_bar.set(0)
        self.progress_bar.pack(fill="x", padx=10, pady=(4, 2))

        self.log_view = ctk.CTkTextbox(self, height=120, corner_radius=6, fg_color=self.inner_bg, border_width=1, border_color=self.panel_border, text_color=self.text_main)
        self.log_view.pack(fill="both", expand=True, padx=10, pady=3)

        # Footer
        bottom_bar = ctk.CTkFrame(self, fg_color="transparent")
        bottom_bar.pack(fill="x", padx=10, pady=(2, 8))

        self.btn_clear = ctk.CTkButton(bottom_bar, text="Reset", width=80, height=32, fg_color="#1e293b", hover_color="#334155", command=self.reset_form)
        self.btn_clear.pack(side="left", padx=(0, 4))

        self.btn_execute = ctk.CTkButton(bottom_bar, text="Build & Export IPA", height=32, state="disabled", command=self.start_process_thread)
        self.btn_execute.pack(side="right", fill="x", expand=True, padx=(4, 0))

    def on_global_drop(self, event):
        raw_data = event.data.strip('{}').replace('"', '')
        if not raw_data: return
        file_path = raw_data.split('} {')[0].strip('{}')
        if not os.path.exists(file_path): return

        ext = os.path.splitext(file_path)[1].lower()
        if ext == '.ipa':
            self.ipa_path = os.path.abspath(file_path)
            self.entry_ipa.delete(0, "end")
            self.entry_ipa.insert(0, self.ipa_path)
            self.log(f"Loaded IPA: {os.path.basename(self.ipa_path)}")
            threading.Thread(target=self._inspect_ipa, daemon=True).start()
        elif ext in ('.dylib', '.deb'):
            self.injected_dylib_path = os.path.abspath(file_path)
            self.entry_inject.delete(0, "end")
            self.entry_inject.insert(0, os.path.basename(self.injected_dylib_path))
            self.log(f"Queued Injection: {os.path.basename(file_path)}")

    def create_desktop_shortcut(self):
        desktop_dir = ""
        try:
            import winreg
            key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, r"Software\Microsoft\Windows\CurrentVersion\Explorer\User Shell Folders")
            desktop_dir, _ = winreg.QueryValueEx(key, "Desktop")
            desktop_dir = os.path.expandvars(desktop_dir)
        except Exception: desktop_dir = os.path.join(os.path.expanduser("~"), "Desktop")

        desktop_lnk = os.path.join(desktop_dir, "IPA Studio.lnk")
        icon = ICON_PATH if os.path.exists(ICON_PATH) else None

        if create_shortcut(os.path.abspath(__file__), desktop_lnk, icon):
            messagebox.showinfo("Success", f"Shortcut created on Desktop:\n{desktop_lnk}")
        else: messagebox.showerror("Error", "Could not create shortcut.")

    def update_icon(self):
        file = filedialog.askopenfilename(filetypes=IMAGE_FORMATS)
        if file and convert_to_icon(file, ICON_PATH):
            try: self.iconbitmap(ICON_PATH)
            except Exception: pass
            messagebox.showinfo("Success", "Icon updated successfully.")

    def log(self, text):
        self.log_view.insert("end", text + "\n")
        self.log_view.see("end")

    def handle_font_change(self, font_name):
        self.apply_font(font_name)
        self.save_config()

    def handle_theme_change(self, theme_name):
        if theme_name not in THEMES: theme_name = "Emerald"
        self.apply_theme(theme_name)
        self.save_config()

    def apply_font(self, font_name):
        self.current_font = font_name
        f = FONT_PROFILES.get(font_name, FONT_PROFILES["Futuristic (Bahnschrift)"])

        self.app_title.configure(font=f["title"])
        self.btn_shortcut.configure(font=f["ui_sm"])
        self.btn_icon.configure(font=f["ui_sm"])
        self.btn_update.configure(font=f["ui_sm"])
        self.font_picker.configure(font=f["ui_sm"], dropdown_font=f["ui_sm"])
        self.theme_picker.configure(font=f["ui_sm"], dropdown_font=f["ui_sm"])
        self.btn_mode_toggle.configure(font=f["ui_bold"])
        self.lbl_file.configure(font=f["ui_bold"])
        self.entry_ipa.configure(font=f["mono"])
        self.btn_browse.configure(font=f["ui_bold"])
        self.ent_curr_ver.configure(font=f["mono"])
        self.ent_new_ver.configure(font=f["mono"])
        self.ent_curr_build.configure(font=f["mono"])
        self.ent_new_build.configure(font=f["mono"])
        self.ent_display_name.configure(font=f["mono"])
        self.ent_bundle_id.configure(font=f["mono"])
        self.entry_inject.configure(font=f["mono"])
        self.btn_browse_dylib.configure(font=f["ui_sm"])
        self.chk_unity.configure(font=f["ui_sm"])
        self.chk_files.configure(font=f["ui_sm"])
        self.chk_sig.configure(font=f["ui_sm"])
        self.chk_http.configure(font=f["ui_sm"])
        self.log_view.configure(font=f["mono"])
        self.btn_clear.configure(font=f["ui_bold"])
        self.btn_execute.configure(font=f["ui_bold"])

    def apply_theme(self, theme_name):
        self.current_theme = theme_name
        palette = THEMES.get(theme_name, THEMES["Emerald"])
        pri = palette["primary"]

        self.app_title.configure(text_color=pri)
        self.progress_bar.configure(progress_color=pri)
        self.btn_execute.configure(fg_color=palette["btn_bg"], hover_color=palette["btn_hover"], border_color=pri, border_width=1, text_color="#fff")
        self.font_picker.configure(fg_color=palette["menu_bg"], button_color=pri, button_hover_color=palette["hover"])
        self.theme_picker.configure(fg_color=palette["menu_bg"], button_color=pri, button_hover_color=palette["hover"])
        self.chk_unity.configure(fg_color=pri, hover_color=palette["hover"])
        self.chk_files.configure(fg_color=pri, hover_color=palette["hover"])
        self.chk_sig.configure(fg_color=pri, hover_color=palette["hover"])
        self.chk_http.configure(fg_color=pri, hover_color=palette["hover"])

    def toggle_appearance(self):
        self.appearance_mode = "Light" if self.appearance_mode == "Dark" else "Dark"
        ctk.set_appearance_mode(self.appearance_mode)
        self.btn_mode_toggle.configure(text="Dark" if self.appearance_mode == "Dark" else "Light")
        self._apply_appearance_backgrounds()

        self.header.configure(fg_color=self.card_bg, border_color=self.panel_border)
        self.file_frame.configure(fg_color=self.card_bg, border_color=self.panel_border)
        self.meta_card.configure(fg_color=self.card_bg, border_color=self.panel_border)
        self.dylib_card.configure(fg_color=self.card_bg, border_color=self.panel_border)

        for entry in (self.entry_ipa, self.ent_curr_ver, self.ent_new_ver, self.ent_curr_build,
                      self.ent_new_build, self.ent_display_name, self.ent_bundle_id, self.entry_inject, self.log_view):
            entry.configure(fg_color=self.inner_bg, border_color=self.panel_border, text_color=self.text_main)

        self.apply_theme(self.current_theme)
        self.save_config()

    def choose_ipa(self):
        file_path = filedialog.askopenfilename(filetypes=[("iOS Application Archive", "*.ipa")])
        if not file_path: return

        self.ipa_path = os.path.abspath(file_path)
        self.entry_ipa.delete(0, "end")
        self.entry_ipa.insert(0, self.ipa_path)
        self.log(f"Selected: {os.path.basename(self.ipa_path)}")
        threading.Thread(target=self._inspect_ipa, daemon=True).start()

    def choose_dylib(self):
        file_path = filedialog.askopenfilename(filetypes=[("Dylib or Debian Package", "*.dylib;*.deb")])
        if file_path:
            self.injected_dylib_path = os.path.abspath(file_path)
            self.entry_inject.delete(0, "end")
            self.entry_inject.insert(0, os.path.basename(self.injected_dylib_path))
            self.log(f"Queued Injection: {os.path.basename(file_path)}")

    def _inspect_ipa(self):
        self.log("Inspecting package payload...")
        self.progress_bar.set(0.2)

        if os.path.exists(self.temp_dir):
            shutil.rmtree(self.temp_dir)
        os.makedirs(self.temp_dir, exist_ok=True)

        try:
            with zipfile.ZipFile(self.ipa_path, 'r') as z:
                z.extractall(self.temp_dir)

            payload_path = os.path.join(self.temp_dir, "Payload")
            if not os.path.exists(payload_path):
                self.log("Error: Invalid IPA structure.")
                return

            apps = [f for f in os.listdir(payload_path) if f.endswith(".app")]
            if not apps:
                self.log("Error: No .app bundle found.")
                return

            self.app_dir = os.path.join(payload_path, apps[0])
            self.plist_path = os.path.join(self.app_dir, "Info.plist")

            with open(self.plist_path, "rb") as f:
                self.plist_data = plistlib.load(f)

            curr_ver = str(self.plist_data.get("CFBundleShortVersionString", "N/A"))
            curr_build = str(self.plist_data.get("CFBundleVersion", "N/A"))
            curr_name = str(self.plist_data.get("CFBundleDisplayName", self.plist_data.get("CFBundleName", "")))
            curr_bundle = str(self.plist_data.get("CFBundleIdentifier", ""))

            self.ent_curr_ver.configure(state="normal")
            self.ent_curr_ver.delete(0, "end")
            self.ent_curr_ver.insert(0, curr_ver)
            self.ent_curr_ver.configure(state="disabled")

            self.ent_curr_build.configure(state="normal")
            self.ent_curr_build.delete(0, "end")
            self.ent_curr_build.insert(0, curr_build)
            self.ent_curr_build.configure(state="disabled")

            self.ent_display_name.delete(0, "end")
            self.ent_display_name.insert(0, curr_name)

            self.ent_bundle_id.delete(0, "end")
            self.ent_bundle_id.insert(0, curr_bundle)

            self.log(f"Ready: App loaded ({apps[0]})")
            self.btn_execute.configure(state="normal")
            self.progress_bar.set(0.5)

        except Exception as e:
            self.log(f"Inspection error: {e}")
            self.progress_bar.set(0)

    def start_process_thread(self):
        self.btn_execute.configure(state="disabled")
        self.btn_browse.configure(state="disabled")
        threading.Thread(target=self._process_worker, daemon=True).start()

    def _process_worker(self):
        try:
            self.log("Updating Info.plist metadata...")
            curr_ver = str(self.plist_data.get("CFBundleShortVersionString", ""))
            curr_build = str(self.plist_data.get("CFBundleVersion", ""))

            new_ver = self.ent_new_ver.get().strip() or curr_ver
            new_build = self.ent_new_build.get().strip() or curr_build
            new_name = self.ent_display_name.get().strip()
            new_bundle = self.ent_bundle_id.get().strip()

            if new_ver: self.plist_data["CFBundleShortVersionString"] = new_ver
            if new_build: self.plist_data["CFBundleVersion"] = new_build
            if new_name:
                self.plist_data["CFBundleDisplayName"] = new_name
                self.plist_data["CFBundleName"] = new_name
            if new_bundle: self.plist_data["CFBundleIdentifier"] = new_bundle

            if self.files_var.get():
                self.plist_data["UIFileSharingEnabled"] = True
                self.plist_data["LSSupportsOpeningDocumentsInPlace"] = True

            if self.http_var.get():
                if "NSAppTransportSecurity" not in self.plist_data:
                    self.plist_data["NSAppTransportSecurity"] = {}
                self.plist_data["NSAppTransportSecurity"]["NSAllowsArbitraryLoads"] = True

            with open(self.plist_path, "wb") as f:
                plistlib.dump(self.plist_data, f)

            self.progress_bar.set(0.6)

            # 1. Patch Unity Strings
            if self.unity_var.get() and new_ver and new_build:
                data_dir = os.path.join(self.app_dir, "Data")
                if os.path.exists(data_dir):
                    self.log("Patching Unity binary strings...")
                    for root, _, files in os.walk(data_dir):
                        for file in files:
                            fp = os.path.join(root, file)
                            try:
                                with open(fp, "rb") as bf: content = bf.read()
                                mod = False
                                if curr_ver and curr_ver.encode() in content:
                                    content = content.replace(curr_ver.encode(), new_ver.encode())
                                    mod = True
                                if curr_build and curr_build.encode() in content:
                                    content = content.replace(curr_build.encode(), new_build.encode())
                                    mod = True
                                if mod:
                                    with open(fp, "wb") as bf: bf.write(content)
                                    self.log(f"Patched: {file}")
                            except Exception: continue

            # 2. Clean Signatures & MobileProvision
            if self.sig_var.get():
                self.log("Cleaning old signatures & provisioning profiles...")
                sig_dir = os.path.join(self.app_dir, "_CodeSignature")
                if os.path.exists(sig_dir): shutil.rmtree(sig_dir)
                prov_file = os.path.join(self.app_dir, "embedded.mobileprovision")
                if os.path.exists(prov_file): os.remove(prov_file)

                fw_dir = os.path.join(self.app_dir, "Frameworks")
                if os.path.exists(fw_dir):
                    for root, dirs, files in os.walk(fw_dir):
                        if "_CodeSignature" in dirs:
                            sub_sig = os.path.join(root, "_CodeSignature")
                            try: shutil.rmtree(sub_sig)
                            except Exception: pass

            # 3. Dynamic Library Injection
            if self.injected_dylib_path and os.path.exists(self.injected_dylib_path):
                self.log("Injecting library...")
                fw_dir = os.path.join(self.app_dir, "Frameworks")
                os.makedirs(fw_dir, exist_ok=True)
                
                if self.injected_dylib_path.endswith(".deb"):
                    deb_tmp = os.path.join(self.temp_dir, "_deb_tmp")
                    with zipfile.ZipFile(self.injected_dylib_path, 'r') as z_deb:
                        z_deb.extractall(deb_tmp)
                    for root, _, files in os.walk(deb_tmp):
                        for f in files:
                            if f.endswith(".dylib"):
                                shutil.copy(os.path.join(root, f), fw_dir)
                                self.log(f"Injected from deb: {f}")
                else:
                    dest_dylib = os.path.join(fw_dir, os.path.basename(self.injected_dylib_path))
                    shutil.copy(self.injected_dylib_path, dest_dylib)
                    self.log(f"Injected: {os.path.basename(self.injected_dylib_path)}")

            self.progress_bar.set(0.85)

            # 4. Save Clean IPA
            save_path = filedialog.asksaveasfilename(
                defaultextension=".ipa",
                filetypes=[("iOS Application Archive", "*.ipa")],
                initialfile=f"Clean_{os.path.basename(self.ipa_path)}"
            )

            if not save_path:
                self.log("Build cancelled.")
                return

            self.log("Repackaging Payload...")
            with zipfile.ZipFile(save_path, 'w', zipfile.ZIP_DEFLATED) as zip_out:
                for root, _, files in os.walk(self.temp_dir):
                    for file in files:
                        if "_deb_tmp" in root: continue
                        full_path = os.path.join(root, file)
                        rel_path = os.path.relpath(full_path, self.temp_dir)
                        zip_out.write(full_path, rel_path)

            self.progress_bar.set(1.0)
            self.log(f"Saved: {os.path.basename(save_path)}")
            messagebox.showinfo("Success", "Cleaned IPA exported successfully!")

        except Exception as e:
            self.log(f"Error: {e}")
            messagebox.showerror("Execution Error", str(e))
        finally:
            if os.path.exists(self.temp_dir):
                shutil.rmtree(self.temp_dir)
            self.btn_execute.configure(state="normal")
            self.btn_browse.configure(state="normal")

    def reset_form(self):
        self.entry_ipa.delete(0, "end")
        self.ent_curr_ver.configure(state="normal")
        self.ent_curr_ver.delete(0, "end")
        self.ent_curr_ver.configure(state="disabled")

        self.ent_curr_build.configure(state="normal")
        self.ent_curr_build.delete(0, "end")
        self.ent_curr_build.configure(state="disabled")

        self.ent_new_ver.delete(0, "end")
        self.ent_new_build.delete(0, "end")
        self.ent_display_name.delete(0, "end")
        self.ent_bundle_id.delete(0, "end")
        self.entry_inject.delete(0, "end")
        self.log_view.delete("1.0", "end")
        self.progress_bar.set(0)
        self.btn_execute.configure(state="disabled")

if __name__ == "__main__":
    app = IPAToolkitApp()
    app.mainloop()