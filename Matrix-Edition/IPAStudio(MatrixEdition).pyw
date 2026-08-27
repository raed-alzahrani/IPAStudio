import os
import sys
import json
import shutil
import zipfile
import threading
import plistlib
import subprocess
import struct
import tkinter as tk
from tkinter import filedialog, messagebox

# 1. Dependency Auto-Installer & Self-Healer
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
    root.title("Matrix Engine // Dependency Resolver")
    root.geometry("500x300")
    root.resizable(False, False)
    root.configure(bg="#080b0e")

    ws = root.winfo_screenwidth()
    hs = root.winfo_screenheight()
    root.geometry(f"500x300+{int((ws-500)/2)}+{int((hs-300)/2)}")

    tk.Label(root, text="[!] MISSING SYSTEM DEPENDENCIES", font=("Consolas", 13, "bold"), fg="#ff3355", bg="#080b0e").pack(pady=(20, 8))
    tk.Label(root, text="The following required Python packages were not located:", font=("Segoe UI", 10), fg="#94a3b8", bg="#080b0e").pack()

    list_frame = tk.Frame(root, bg="#0e161c", bd=1, relief="solid")
    list_frame.pack(fill="x", padx=30, pady=12)
    for pkg in missing:
        tk.Label(list_frame, text=f"• {pkg}", font=("Consolas", 11, "bold"), fg="#00ff66", bg="#0e161c").pack(anchor="w", padx=15, pady=3)

    def install_and_restart():
        py_dir = os.path.dirname(sys.executable)
        py_exe = os.path.join(py_dir, "python.exe")
        if not os.path.exists(py_exe):
            py_exe = sys.executable

        script_path = os.path.abspath(__file__)
        pkgs_str = " ".join(missing)
        
        bat_cmd = f"""@echo off
title Installing IPA Matrix Dependencies...
echo [*] Target Python: "{py_exe}"
echo [*] Installing: {pkgs_str}
echo.

"{py_exe}" -m pip install --upgrade pip
"{py_exe}" -m pip install {pkgs_str}

if %ERRORLEVEL% NEQ 0 (
    echo.
    echo [!] Installation failed. Review error output above.
    pause
    exit /b %ERRORLEVEL%
)

echo.
echo [*] Launching application...
start "" "{py_exe}" "{script_path}"
exit 0
"""
        bat_file = os.path.join(os.environ.get("TEMP", "."), "_install_ipa_matrix_deps.bat")
        with open(bat_file, "w", encoding="utf-8") as f:
            f.write(bat_cmd)
        
        root.destroy()
        subprocess.Popen(f'cmd.exe /c "{bat_file}"', shell=True)
        os._exit(0)

    btn_frame = tk.Frame(root, bg="#080b0e")
    btn_frame.pack(fill="x", padx=30, pady=(10, 15))
    tk.Button(btn_frame, text="EXIT", font=("Segoe UI", 10, "bold"), bg="#1e293b", fg="#ffffff", bd=0, padx=15, pady=6, command=lambda: (root.destroy(), os._exit(0))).pack(side="left")
    tk.Button(btn_frame, text="[► INSTALL DEPENDENCIES & LAUNCH]", font=("Segoe UI", 10, "bold"), bg="#005a24", fg="#00ff66", bd=0, padx=15, pady=6, command=install_and_restart).pack(side="right")

    root.mainloop()
    sys.exit()

from PIL import Image
import customtkinter as ctk
from tkinterdnd2 import TkinterDnD, DND_FILES

SCRIPT_FILE = os.path.abspath(__file__)
SCRIPT_DIR = os.path.dirname(SCRIPT_FILE)
CONFIG_FILE = os.path.join(SCRIPT_DIR, "config.json")
APP_ICON_FILE = os.path.join(SCRIPT_DIR, "app_icon.ico")

IMAGE_EXTS = (('Image Files', '*.png;*.jpg;*.jpeg;*.webp;*.bmp;*.ico'), ('All Files', '*.*'))

FONT_PROFILES = {
    "Retro Matrix (Consolas)": {
        "title": ("Consolas", 16, "bold"), "ui_bold": ("Consolas", 11, "bold"),
        "ui_sm": ("Consolas", 10, "bold"), "console": ("Consolas", 10, "bold")
    },
    "Modern Bold (Segoe UI)": {
        "title": ("Segoe UI", 16, "bold"), "ui_bold": ("Segoe UI", 11, "bold"),
        "ui_sm": ("Segoe UI", 10, "bold"), "console": ("Consolas", 10, "bold")
    },
    "Cyber Terminal (Lucida Console)": {
        "title": ("Lucida Console", 15, "bold"), "ui_bold": ("Lucida Console", 11, "bold"),
        "ui_sm": ("Lucida Console", 10, "bold"), "console": ("Lucida Console", 10, "bold")
    },
    "Developer Mono (Cascadia Mono)": {
        "title": ("Cascadia Mono", 15, "bold"), "ui_bold": ("Cascadia Mono", 11, "bold"),
        "ui_sm": ("Cascadia Mono", 10, "bold"), "console": ("Cascadia Mono", 10, "bold")
    },
    "Futuristic Clean (Bahnschrift)": {
        "title": ("Bahnschrift", 16, "bold"), "ui_bold": ("Bahnschrift", 11, "bold"),
        "ui_sm": ("Bahnschrift", 10, "bold"), "console": ("Consolas", 10, "bold")
    }
}

THEME_PALETTES = {
    "Green": {"primary": "#00ff66", "hover": "#00cc52", "border": "#10b981", "dark_bg": "#005a24", "dark_hover": "#008033"},
    "Red": {"primary": "#ff3355", "hover": "#e61e3f", "border": "#f43f5e", "dark_bg": "#7f1d1d", "dark_hover": "#991b1b"},
    "Blue": {"primary": "#38bdf8", "hover": "#0ea5e9", "border": "#0284c7", "dark_bg": "#0369a1", "dark_hover": "#0284c7"},
    "Yellow": {"primary": "#facc15", "hover": "#eab308", "border": "#ca8a04", "dark_bg": "#854d0e", "dark_hover": "#a16207"},
    "Purple": {"primary": "#c084fc", "hover": "#a855f7", "border": "#9333ea", "dark_bg": "#581c87", "dark_hover": "#6b21a8"},
    "Turquoise": {"primary": "#2dd4bf", "hover": "#14b8a6", "border": "#0d9488", "dark_bg": "#115e59", "dark_hover": "#0f766e"}
}

def process_and_save_ico(input_image_path, output_ico_path):
    try:
        img = Image.open(input_image_path).convert("RGBA")
        width, height = img.size
        min_dim = min(width, height)
        left = (width - min_dim) // 2
        top = (height - min_dim) // 2
        cropped_img = img.crop((left, top, left + min_dim, top + min_dim))
        sizes = [(256, 256), (128, 128), (64, 64), (48, 48), (32, 32), (16, 16)]
        cropped_img.save(output_ico_path, format="ICO", sizes=sizes)
        return True
    except Exception: return False

def make_desktop_shortcut(target, link_path, icon_path=None):
    try:
        working_dir = os.path.dirname(target)
        icon_line = f'oLink.IconLocation = "{icon_path}"' if (icon_path and os.path.exists(icon_path)) else ""
        vbs_script = f'''
        Set oWS = WScript.CreateObject("WScript.Shell")
        sLinkFile = "{link_path}"
        Set oLink = oWS.CreateShortcut(sLinkFile)
        oLink.TargetPath = "{target}"
        oLink.WorkingDirectory = "{working_dir}"
        oLink.Description = "Matrix IPA Studio Engine"
        {icon_line}
        oLink.Save
        '''
        vbs_path = os.path.join(os.environ.get("TEMP", os.path.expanduser("~")), "_make_shortcut.vbs")
        with open(vbs_path, "w", encoding="utf-8") as f:
            f.write(vbs_script)
            
        subprocess.run(["wscript", vbs_path], creationflags=0x08000000 if sys.platform == "win32" else 0)
        if os.path.exists(vbs_path): os.remove(vbs_path)
        return os.path.exists(link_path)
    except Exception: return False

class HotCodeUpdaterModal(ctk.CTkToplevel):
    def __init__(self, parent, target_file, restart_callback, theme_color="Green", appearance_mode="Dark"):
        super().__init__(parent)
        self.title("Matrix Hot-Code Engine Overhaul")
        self.geometry("860x620")
        self.target_file = target_file
        self.restart_callback = restart_callback
        self.palette = THEME_PALETTES.get(theme_color, THEME_PALETTES["Green"])
        
        bg_color = "#080b0e" if appearance_mode == "Dark" else "#e2e8f0"
        self.configure(fg_color=bg_color)
        self.transient(parent)
        self.grab_set()

        pri = self.palette["primary"]
        txt_main = "#ffffff" if appearance_mode == "Dark" else "#0f172a"
        inner_bg = "#050709" if appearance_mode == "Dark" else "#f1f5f9"

        header_box = ctk.CTkFrame(self, fg_color="transparent")
        header_box.pack(fill="x", padx=20, pady=(16, 6))

        lbl = ctk.CTkLabel(header_box, text="[❖] CODE PAYLOAD INJECTION / EXPORT:", font=("Consolas", 13, "bold"), text_color=pri)
        lbl.pack(side="left")

        actions_box = ctk.CTkFrame(header_box, fg_color="transparent")
        actions_box.pack(side="right")

        ctk.CTkButton(
            actions_box, text="📋 COPY CODE", width=120, height=28,
            font=("Segoe UI", 11, "bold"), fg_color="#1e293b",
            hover_color="#334155", text_color="#ffffff", command=self.copy_current_code
        ).pack(side="left", padx=(0, 6))

        ctk.CTkButton(
            actions_box, text="📥 PASTE CODE", width=120, height=28,
            font=("Segoe UI", 11, "bold"), fg_color=self.palette["dark_bg"],
            hover_color=self.palette["hover"], text_color=pri if appearance_mode == "Dark" else "#ffffff", command=self.paste_from_clipboard
        ).pack(side="left")

        self.txt_code = ctk.CTkTextbox(
            self, font=("Consolas", 11), fg_color=inner_bg,
            border_color=pri, border_width=1, text_color=txt_main, undo=True
        )
        self.txt_code.pack(fill="both", expand=True, padx=20, pady=8)

        try:
            with open(self.target_file, "r", encoding="utf-8") as f:
                self.txt_code.insert("1.0", f.read())
        except Exception: pass

        self.txt_code.bind("<Control-v>", lambda _: self.paste_from_clipboard() or "break")
        self.txt_code.bind("<Control-V>", lambda _: self.paste_from_clipboard() or "break")

        btn_box = ctk.CTkFrame(self, fg_color="transparent")
        btn_box.pack(fill="x", padx=20, pady=(0, 16))

        ctk.CTkButton(btn_box, text="CANCEL", width=110, font=("Segoe UI", 11, "bold"), fg_color="#1e293b", command=self.destroy).pack(side="left")
        ctk.CTkButton(
            btn_box, text="[► INJECT CODE & RESTART INSTANCE]", font=("Segoe UI", 12, "bold"),
            fg_color=self.palette["dark_bg"], hover_color=self.palette["dark_hover"],
            border_width=1, border_color=pri, text_color=pri if appearance_mode == "Dark" else "#ffffff",
            command=self.apply_update
        ).pack(side="right", fill="x", expand=True, padx=(10, 0))

    def copy_current_code(self):
        try:
            with open(self.target_file, "r", encoding="utf-8") as f: code_data = f.read()
            self.clipboard_clear()
            self.clipboard_append(code_data)
            self.update()
            messagebox.showinfo("Clipboard", "Code copied to clipboard!")
        except Exception as e: messagebox.showerror("Error", str(e))

    def paste_from_clipboard(self):
        try:
            text = self.clipboard_get()
            if text:
                self.txt_code.delete("1.0", "end")
                self.txt_code.insert("1.0", text)
        except Exception as e: messagebox.showwarning("Warning", str(e))

    def apply_update(self):
        code = self.txt_code.get("1.0", "end-1c").strip()
        if len(code) < 50 or "import" not in code:
            messagebox.showerror("Payload Error", "Invalid script payload provided.")
            return

        try:
            with open(self.target_file, 'w', encoding='utf-8') as f: f.write(code)
            messagebox.showinfo("Success", "Engine updated! Restarting...")
            self.destroy()
            self.restart_callback()
        except Exception as e: messagebox.showerror("Write Error", str(e))

class MatrixIPAStudio(ctk.CTk, TkinterDnD.DnDWrapper):
    def __init__(self):
        super().__init__()
        self.TkdndVersion = TkinterDnD._require(self)

        self.title("MATRIX // IPA_STUDIO_ENGINE_V6.0")
        self.minsize(820, 600)

        self.config = self.load_config()

        if os.path.exists(APP_ICON_FILE):
            try: self.iconbitmap(APP_ICON_FILE)
            except Exception: pass

        saved_geom = self.config.get("window_geometry", "860x640")
        try: self.geometry(saved_geom)
        except Exception: self.geometry("860x640")

        if self.config.get("is_maximized", False):
            self.after(100, lambda: self.state("zoomed"))

        self.current_font_profile = self.config.get("font_profile", "Retro Matrix (Consolas)")
        if self.current_font_profile not in FONT_PROFILES: self.current_font_profile = "Retro Matrix (Consolas)"

        self.current_theme_color = self.config.get("theme_color", "Green")
        if self.current_theme_color not in THEME_PALETTES: self.current_theme_color = "Green"

        self.current_appearance = self.config.get("appearance_mode", "Dark")
        ctk.set_appearance_mode(self.current_appearance)

        self.ipa_path = ""
        self.injected_dylib_path = ""
        self.temp_dir = os.path.join(os.environ.get("TEMP", SCRIPT_DIR), "_matrix_ipa_workspace")
        self.app_dir = ""
        self.plist_path = ""
        self.plist_data = {}

        self._apply_appearance_backgrounds()
        self._build_matrix_ui()
        self.apply_theme(self.current_theme_color)
        self.apply_font_profile(self.current_font_profile)

        try:
            self.drop_target_register(DND_FILES)
            self.dnd_bind('<<Drop>>', self.on_global_drop)
        except Exception: pass

        self.protocol("WM_DELETE_WINDOW", self.on_app_close)

    def load_config(self):
        default_cfg = {
            "window_geometry": "860x640", "is_maximized": False,
            "font_profile": "Retro Matrix (Consolas)", "theme_color": "Green",
            "appearance_mode": "Dark", "patch_unity": True,
            "clean_sig": True, "enable_files": True, "allow_http": False
        }
        if os.path.exists(CONFIG_FILE):
            try:
                with open(CONFIG_FILE, 'r', encoding='utf-8') as f: default_cfg.update(json.load(f))
            except Exception: pass
        return default_cfg

    def save_config(self):
        try:
            is_max = (self.state() == "zoomed")
            current_geom = self.config.get("window_geometry", "860x640") if is_max else self.geometry()
            self.config = {
                "window_geometry": current_geom, "is_maximized": is_max,
                "font_profile": self.current_font_profile, "theme_color": self.current_theme_color,
                "appearance_mode": self.current_appearance,
                "patch_unity": self.unity_var.get(), "clean_sig": self.sig_var.get(),
                "enable_files": self.files_var.get(), "allow_http": self.http_var.get()
            }
            with open(CONFIG_FILE, 'w', encoding='utf-8') as f: json.dump(self.config, f, indent=4)
        except Exception: pass

    def on_app_close(self):
        if os.path.exists(self.temp_dir):
            try: shutil.rmtree(self.temp_dir)
            except Exception: pass
        self.save_config()
        self.destroy()

    def restart_application(self):
        self.save_config()
        subprocess.Popen([sys.executable.replace("python.exe", "pythonw.exe"), SCRIPT_FILE], creationflags=0x08000000 if sys.platform == "win32" else 0)
        self.destroy()
        sys.exit()

    def open_hot_updater(self):
        HotCodeUpdaterModal(self, SCRIPT_FILE, self.restart_application, self.current_theme_color, self.current_appearance)

    def create_desktop_shortcut_now(self):
        desktop_dir = ""
        try:
            import winreg
            key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, r"Software\Microsoft\Windows\CurrentVersion\Explorer\User Shell Folders")
            desktop_dir, _ = winreg.QueryValueEx(key, "Desktop")
            desktop_dir = os.path.expandvars(desktop_dir)
        except Exception: desktop_dir = os.path.join(os.path.expanduser("~"), "Desktop")

        desktop_lnk = os.path.join(desktop_dir, "Matrix IPA Studio.lnk")
        icon_arg = APP_ICON_FILE if os.path.exists(APP_ICON_FILE) else None
        
        if make_desktop_shortcut(SCRIPT_FILE, desktop_lnk, icon_path=icon_arg):
            messagebox.showinfo("Success", f"[❖] SHORTCUT GENERATED:\n{desktop_lnk}")
        else: messagebox.showerror("Error", "[!] Failed to establish shortcut link.")

    def change_app_icon_live(self):
        img_p = filedialog.askopenfilename(title="Select Icon / Image File", filetypes=IMAGE_EXTS)
        if img_p and process_and_save_ico(img_p, APP_ICON_FILE):
            try:
                self.iconbitmap(APP_ICON_FILE)
                messagebox.showinfo("Icon Updated", "App icon generated and applied!")
            except Exception: pass

    def _apply_appearance_backgrounds(self):
        if self.current_appearance == "Dark":
            self.configure(fg_color="#080b0e")
            self.card_bg = "#0d1318"
            self.inner_bg = "#050709"
            self.panel_border = "#1e2d38"
            self.text_main = "#ffffff"
            self.text_muted = "#94a3b8"
        else:
            self.configure(fg_color="#e2e8f0")
            self.card_bg = "#cbd5e1"
            self.inner_bg = "#f1f5f9"
            self.panel_border = "#94a3b8"
            self.text_main = "#0f172a"
            self.text_muted = "#334155"

    def _build_matrix_ui(self):
        f = FONT_PROFILES.get(self.current_font_profile, FONT_PROFILES["Retro Matrix (Consolas)"])

        # 1. Header Frame
        self.header_frame = ctk.CTkFrame(self, fg_color=self.card_bg, corner_radius=10, border_width=1, border_color=self.panel_border)
        self.header_frame.pack(fill="x", padx=16, pady=(10, 4))

        top_bar = ctk.CTkFrame(self.header_frame, fg_color="transparent")
        top_bar.pack(fill="x", padx=10, pady=6)

        self.title_lbl = ctk.CTkLabel(top_bar, text="[❖] MATRIX IPA STUDIO", font=f["title"], text_color="#00ff66")
        self.title_lbl.pack(side="left", padx=4)

        ctrl_box = ctk.CTkFrame(top_bar, fg_color="transparent")
        ctrl_box.pack(side="right")

        self.btn_shortcut = ctk.CTkButton(ctrl_box, text="📌 SHORTCUT", width=95, height=28, font=f["ui_sm"], fg_color="#1e293b", hover_color="#334155", command=self.create_desktop_shortcut_now)
        self.btn_shortcut.pack(side="left", padx=2)

        self.btn_change_icon = ctk.CTkButton(ctrl_box, text="🖼️ ICON", width=65, height=28, font=f["ui_sm"], fg_color="#581c87", hover_color="#6b21a8", command=self.change_app_icon_live)
        self.btn_change_icon.pack(side="left", padx=2)

        self.btn_update = ctk.CTkButton(ctrl_box, text="⚡ UPDATE", width=75, height=28, font=f["ui_sm"], fg_color="#0369a1", hover_color="#0284c7", command=self.open_hot_updater)
        self.btn_update.pack(side="left", padx=2)

        self.font_menu = ctk.CTkOptionMenu(ctrl_box, values=list(FONT_PROFILES.keys()), command=self.on_font_selected, width=155, height=28, font=f["ui_sm"], dropdown_font=f["ui_sm"])
        self.font_menu.set(self.current_font_profile)
        self.font_menu.pack(side="left", padx=2)

        self.theme_menu = ctk.CTkOptionMenu(ctrl_box, values=list(THEME_PALETTES.keys()), command=self.on_theme_selected, width=95, height=28, font=f["ui_sm"], dropdown_font=f["ui_sm"])
        self.theme_menu.set(self.current_theme_color)
        self.theme_menu.pack(side="left", padx=2)

        self.btn_toggle_mode = ctk.CTkButton(ctrl_box, text="🌙 DARK" if self.current_appearance == "Dark" else "☀️ LIGHT", width=75, height=28, font=f["ui_sm"], fg_color="#1e293b", hover_color="#334155", command=self.toggle_appearance_mode)
        self.btn_toggle_mode.pack(side="left", padx=2)

        # 2. File Selection Bar
        self.file_frame = ctk.CTkFrame(self, fg_color=self.card_bg, corner_radius=8, border_width=1, border_color=self.panel_border)
        self.file_frame.pack(fill="x", padx=16, pady=4)

        self.lbl_file = ctk.CTkLabel(self.file_frame, text="TARGET_PAYLOAD:", font=f["ui_bold"], text_color=self.text_muted)
        self.lbl_file.pack(side="left", padx=(12, 6), pady=6)

        self.entry_ipa = ctk.CTkEntry(self.file_frame, height=30, font=f["console"], fg_color=self.inner_bg, border_color=self.panel_border, text_color=self.text_main, placeholder_text="Drag & drop .ipa anywhere...")
        self.entry_ipa.pack(side="left", fill="x", expand=True, padx=4, pady=6)

        self.btn_browse = ctk.CTkButton(self.file_frame, text="[📁 BROWSE]", width=110, height=30, font=f["ui_bold"], fg_color="#1e293b", hover_color="#334155", command=self.choose_ipa)
        self.btn_browse.pack(side="right", padx=(4, 10), pady=6)

        # 3. Two-Column Configuration Panels
        self.content_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.content_frame.pack(fill="x", padx=16, pady=4)
        self.content_frame.grid_columnconfigure((0, 1), weight=1)

        # Left Panel: Versioning & Spoofing
        self.meta_card = ctk.CTkFrame(self.content_frame, fg_color=self.card_bg, corner_radius=8, border_width=1, border_color=self.panel_border)
        self.meta_card.grid(row=0, column=0, sticky="nsew", padx=(0, 4), pady=0)

        ctk.CTkLabel(self.meta_card, text="[❖] METADATA & VERSION INJECTION:", font=f["ui_bold"], anchor="w").pack(fill="x", padx=10, pady=(6, 2))

        ver_box = ctk.CTkFrame(self.meta_card, fg_color="transparent")
        ver_box.pack(fill="x", padx=8, pady=2)
        ver_box.grid_columnconfigure((0, 1), weight=1)

        self.ent_curr_ver = ctk.CTkEntry(ver_box, height=26, state="disabled", placeholder_text="Current Ver", font=f["console"], fg_color=self.inner_bg, border_color=self.panel_border)
        self.ent_curr_ver.grid(row=0, column=0, sticky="ew", padx=(0, 2))
        self.ent_new_ver = ctk.CTkEntry(ver_box, height=26, placeholder_text="Target Ver (1.1.4)", font=f["console"], fg_color=self.inner_bg, border_color=self.panel_border)
        self.ent_new_ver.grid(row=0, column=1, sticky="ew", padx=(2, 0))

        bld_box = ctk.CTkFrame(self.meta_card, fg_color="transparent")
        bld_box.pack(fill="x", padx=8, pady=2)
        bld_box.grid_columnconfigure((0, 1), weight=1)

        self.ent_curr_build = ctk.CTkEntry(bld_box, height=26, state="disabled", placeholder_text="Current Build", font=f["console"], fg_color=self.inner_bg, border_color=self.panel_border)
        self.ent_curr_build.grid(row=0, column=0, sticky="ew", padx=(0, 2))
        self.ent_new_build = ctk.CTkEntry(bld_box, height=26, placeholder_text="Target Build (101040)", font=f["console"], fg_color=self.inner_bg, border_color=self.panel_border)
        self.ent_new_build.grid(row=0, column=1, sticky="ew", padx=(2, 0))

        self.ent_display_name = ctk.CTkEntry(self.meta_card, height=26, placeholder_text="Display Name Override", font=f["console"], fg_color=self.inner_bg, border_color=self.panel_border)
        self.ent_display_name.pack(fill="x", padx=8, pady=2)

        self.ent_bundle_id = ctk.CTkEntry(self.meta_card, height=26, placeholder_text="Bundle ID (Duplicate App)", font=f["console"], fg_color=self.inner_bg, border_color=self.panel_border)
        self.ent_bundle_id.pack(fill="x", padx=8, pady=(2, 6))

        # Right Panel: Dylib Injection & Flags
        self.dylib_card = ctk.CTkFrame(self.content_frame, fg_color=self.card_bg, corner_radius=8, border_width=1, border_color=self.panel_border)
        self.dylib_card.grid(row=0, column=1, sticky="nsew", padx=(4, 0), pady=0)

        ctk.CTkLabel(self.dylib_card, text="[❖] DYNAMIC LIBRARIES & FLAGS:", font=f["ui_bold"], anchor="w").pack(fill="x", padx=10, pady=(6, 2))

        inj_box = ctk.CTkFrame(self.dylib_card, fg_color="transparent")
        inj_box.pack(fill="x", padx=8, pady=2)
        self.entry_inject = ctk.CTkEntry(inj_box, height=26, placeholder_text="Inject .dylib / .deb (Optional)", font=f["console"], fg_color=self.inner_bg, border_color=self.panel_border)
        self.entry_inject.pack(side="left", fill="x", expand=True, padx=(0, 3))

        self.btn_browse_dylib = ctk.CTkButton(inj_box, text="Pick", width=55, height=26, font=f["ui_sm"], fg_color="#1e293b", hover_color="#334155", command=self.choose_dylib)
        self.btn_browse_dylib.pack(side="right")

        opts_grid = ctk.CTkFrame(self.dylib_card, fg_color="transparent")
        opts_grid.pack(fill="x", padx=8, pady=(4, 2))
        opts_grid.grid_columnconfigure((0, 1), weight=1)

        self.unity_var = ctk.BooleanVar(value=self.config.get("patch_unity", True))
        self.chk_unity = ctk.CTkCheckBox(opts_grid, text="Patch Unity Assets", variable=self.unity_var, font=f["ui_sm"], command=self.save_config)
        self.chk_unity.grid(row=0, column=0, sticky="w", pady=2)

        self.files_var = ctk.BooleanVar(value=self.config.get("enable_files", True))
        self.chk_files = ctk.CTkCheckBox(opts_grid, text="Enable Files Sharing", variable=self.files_var, font=f["ui_sm"], command=self.save_config)
        self.chk_files.grid(row=0, column=1, sticky="w", pady=2)

        self.sig_var = ctk.BooleanVar(value=self.config.get("clean_sig", True))
        self.chk_sig = ctk.CTkCheckBox(opts_grid, text="Clean Signatures", variable=self.sig_var, font=f["ui_sm"], command=self.save_config)
        self.chk_sig.grid(row=1, column=0, sticky="w", pady=2)

        self.http_var = ctk.BooleanVar(value=self.config.get("allow_http", False))
        self.chk_http = ctk.CTkCheckBox(opts_grid, text="Allow HTTP Traffic", variable=self.http_var, font=f["ui_sm"], command=self.save_config)
        self.chk_http.grid(row=1, column=1, sticky="w", pady=2)

        # 4. Progress & Activity Console
        self.progress = ctk.CTkProgressBar(self, height=10, corner_radius=4)
        self.progress.set(0)
        self.progress.pack(fill="x", padx=16, pady=(6, 4))

        self.console = ctk.CTkTextbox(self, height=140, font=f["console"], corner_radius=8, fg_color=self.inner_bg, border_width=1, border_color=self.panel_border, text_color=self.text_main)
        self.console.pack(fill="both", expand=True, padx=16, pady=4)

        self.console.tag_config("primary", foreground="#00ff66")
        self.console.tag_config("cyan", foreground="#00f0ff")
        self.console.tag_config("crimson", foreground="#ff3366")
        self.console.tag_config("gold", foreground="#facc15")
        self.console.tag_config("ghost", foreground="#94a3b8")

        # 5. Bottom Controls Bar
        btn_frame = ctk.CTkFrame(self, fg_color="transparent")
        btn_frame.pack(fill="x", padx=16, pady=(4, 12))

        self.btn_reset = ctk.CTkButton(btn_frame, text="[↺ RESET]", width=110, font=f["ui_bold"], fg_color="#1e293b", hover_color="#334155", command=self.reset_form, height=38)
        self.btn_reset.pack(side="left", padx=(0, 6))

        self.btn_execute = ctk.CTkButton(btn_frame, text="[► INITIALIZE REPACK ENGINE]", font=f["ui_bold"], state="disabled", command=self.start_thread, height=38)
        self.btn_execute.pack(side="right", fill="x", expand=True, padx=(6, 0))

    def on_font_selected(self, font_name):
        self.apply_font_profile(font_name)
        self.save_config()

    def on_theme_selected(self, theme_name):
        self.apply_theme(theme_name)
        self.save_config()

    def apply_font_profile(self, profile_name):
        self.current_font_profile = profile_name
        f = FONT_PROFILES.get(profile_name, FONT_PROFILES["Retro Matrix (Consolas)"])

        self.title_lbl.configure(font=f["title"])
        self.btn_shortcut.configure(font=f["ui_sm"])
        self.btn_change_icon.configure(font=f["ui_sm"])
        self.btn_update.configure(font=f["ui_sm"])
        self.font_menu.configure(font=f["ui_sm"], dropdown_font=f["ui_sm"])
        self.theme_menu.configure(font=f["ui_sm"], dropdown_font=f["ui_sm"])
        self.btn_toggle_mode.configure(font=f["ui_sm"])
        self.lbl_file.configure(font=f["ui_bold"])
        self.entry_ipa.configure(font=f["console"])
        self.btn_browse.configure(font=f["ui_bold"])
        self.ent_curr_ver.configure(font=f["console"])
        self.ent_new_ver.configure(font=f["console"])
        self.ent_curr_build.configure(font=f["console"])
        self.ent_new_build.configure(font=f["console"])
        self.ent_display_name.configure(font=f["console"])
        self.ent_bundle_id.configure(font=f["console"])
        self.entry_inject.configure(font=f["console"])
        self.btn_browse_dylib.configure(font=f["ui_sm"])
        self.chk_unity.configure(font=f["ui_sm"])
        self.chk_files.configure(font=f["ui_sm"])
        self.chk_sig.configure(font=f["ui_sm"])
        self.chk_http.configure(font=f["ui_sm"])
        self.console.configure(font=f["console"])
        self.btn_reset.configure(font=f["ui_bold"])
        self.btn_execute.configure(font=f["ui_bold"])

    def toggle_appearance_mode(self):
        if self.current_appearance == "Dark":
            self.current_appearance = "Light"
            ctk.set_appearance_mode("Light")
            self.btn_toggle_mode.configure(text="☀️ LIGHT")
        else:
            self.current_appearance = "Dark"
            ctk.set_appearance_mode("Dark")
            self.btn_toggle_mode.configure(text="🌙 DARK")

        self._apply_appearance_backgrounds()
        self.header_frame.configure(fg_color=self.card_bg, border_color=self.panel_border)
        self.file_frame.configure(fg_color=self.card_bg, border_color=self.panel_border)
        self.meta_card.configure(fg_color=self.card_bg, border_color=self.panel_border)
        self.dylib_card.configure(fg_color=self.card_bg, border_color=self.panel_border)

        for entry in (self.entry_ipa, self.ent_curr_ver, self.ent_new_ver, self.ent_curr_build,
                      self.ent_new_build, self.ent_display_name, self.ent_bundle_id, self.entry_inject):
            entry.configure(fg_color=self.inner_bg, border_color=self.panel_border, text_color=self.text_main)

        self.console.configure(fg_color=self.inner_bg, border_color=self.panel_border, text_color=self.text_main)
        self.apply_theme(self.current_theme_color)
        self.save_config()

    def apply_theme(self, theme_name):
        self.current_theme_color = theme_name
        palette = THEME_PALETTES.get(theme_name, THEME_PALETTES["Green"])
        pri = palette["primary"]

        self.title_lbl.configure(text_color=pri)
        self.header_frame.configure(border_color=pri)
        self.progress.configure(progress_color=pri)
        self.console.configure(border_color=pri)
        self.console.tag_config("primary", foreground=pri)

        self.theme_menu.configure(fg_color=palette["dark_bg"], button_color=pri, button_hover_color=palette["hover"])
        self.font_menu.configure(fg_color=palette["dark_bg"], button_color=pri, button_hover_color=palette["hover"])
        self.btn_execute.configure(fg_color=palette["dark_bg"], hover_color=palette["dark_hover"], border_width=1, border_color=pri, text_color=pri if self.current_appearance == "Dark" else "#ffffff")

        self.chk_unity.configure(fg_color=pri, hover_color=palette["hover"])
        self.chk_files.configure(fg_color=pri, hover_color=palette["hover"])
        self.chk_sig.configure(fg_color=pri, hover_color=palette["hover"])
        self.chk_http.configure(fg_color=pri, hover_color=palette["hover"])

    def log(self, text, color_tag="primary"):
        self.console.insert("end", text + "\n", color_tag)
        self.console.see("end")

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
            self.log(f"[PAYLOAD] Loaded IPA Archive: {os.path.basename(self.ipa_path)}", "cyan")
            threading.Thread(target=self._inspect_ipa, daemon=True).start()
        elif ext in ('.dylib', '.deb'):
            self.injected_dylib_path = os.path.abspath(file_path)
            self.entry_inject.delete(0, "end")
            self.entry_inject.insert(0, os.path.basename(self.injected_dylib_path))
            self.log(f"[INJECT] Dynamic Library Target: {os.path.basename(file_path)}", "gold")

    def choose_ipa(self):
        file_path = filedialog.askopenfilename(filetypes=[("iOS Application Archive", "*.ipa")])
        if not file_path: return

        self.ipa_path = os.path.abspath(file_path)
        self.entry_ipa.delete(0, "end")
        self.entry_ipa.insert(0, self.ipa_path)
        self.log(f"[PAYLOAD] Loaded: {os.path.basename(self.ipa_path)}", "cyan")
        threading.Thread(target=self._inspect_ipa, daemon=True).start()

    def choose_dylib(self):
        file_path = filedialog.askopenfilename(filetypes=[("Dylib or Debian Package", "*.dylib;*.deb")])
        if file_path:
            self.injected_dylib_path = os.path.abspath(file_path)
            self.entry_inject.delete(0, "end")
            self.entry_inject.insert(0, os.path.basename(self.injected_dylib_path))
            self.log(f"[INJECT] Queued Library: {os.path.basename(file_path)}", "gold")

    def _inspect_ipa(self):
        self.log("[SYS] Inspecting package payload...", "ghost")
        self.progress.set(0.2)

        if os.path.exists(self.temp_dir):
            try: shutil.rmtree(self.temp_dir)
            except Exception: pass
        os.makedirs(self.temp_dir, exist_ok=True)

        try:
            with zipfile.ZipFile(self.ipa_path, 'r') as z:
                z.extractall(self.temp_dir)

            payload_path = os.path.join(self.temp_dir, "Payload")
            if not os.path.exists(payload_path):
                self.log("[FAIL] Invalid IPA Archive structure.", "crimson")
                return

            apps = [f for f in os.listdir(payload_path) if f.endswith(".app")]
            if not apps:
                self.log("[FAIL] No valid .app bundle found in payload.", "crimson")
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

            self.log(f"[OK] App Loaded: {apps[0]} | Ver: {curr_ver} | Build: {curr_build}", "primary")
            self.btn_execute.configure(state="normal")
            self.progress.set(0.5)

        except Exception as e:
            self.log(f"[FAIL] Inspection Error: {e}", "crimson")
            self.progress.set(0)

    def start_thread(self):
        self.btn_execute.configure(state="disabled")
        self.btn_browse.configure(state="disabled")
        threading.Thread(target=self._process_worker, daemon=True).start()

    def _process_worker(self):
        try:
            self.log("[EXEC] Updating Info.plist headers & metadata...", "cyan")
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

            self.progress.set(0.6)

            # 1. Patch Unity Assets
            if self.unity_var.get() and new_ver and new_build:
                data_dir = os.path.join(self.app_dir, "Data")
                if os.path.exists(data_dir):
                    self.log("[EXEC] Patching Unity binary assets strings...", "ghost")
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
                                    self.log(f"  └─► [PATCHED] Asset: {file}", "primary")
                            except Exception: continue

            # 2. Clean Signatures & Provisioning Profiles
            if self.sig_var.get():
                self.log("[EXEC] Purging old CodeSignature blobs & mobileprovision...", "ghost")
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
                self.log(f"[EXEC] Injecting Library: {os.path.basename(self.injected_dylib_path)}", "gold")
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
                                self.log(f"  └─► [INJECTED] Deb Payload: {f}", "primary")
                else:
                    dest_dylib = os.path.join(fw_dir, os.path.basename(self.injected_dylib_path))
                    shutil.copy(self.injected_dylib_path, dest_dylib)
                    self.log(f"  └─► [INJECTED] Dylib: {os.path.basename(self.injected_dylib_path)}", "primary")

            self.progress.set(0.85)

            # 4. Save Clean IPA
            save_path = filedialog.asksaveasfilename(
                defaultextension=".ipa",
                filetypes=[("iOS Application Archive", "*.ipa")],
                initialfile=f"Clean_{os.path.basename(self.ipa_path)}"
            )

            if not save_path:
                self.log("[WARN] Repack aborted by user.", "crimson")
                return

            self.log("[EXEC] Building clean Payload archive...", "cyan")
            with zipfile.ZipFile(save_path, 'w', zipfile.ZIP_DEFLATED) as zip_out:
                for root, _, files in os.walk(self.temp_dir):
                    for file in files:
                        if "_deb_tmp" in root: continue
                        full_path = os.path.join(root, file)
                        rel_path = os.path.relpath(full_path, self.temp_dir)
                        zip_out.write(full_path, rel_path)

            self.progress.set(1.0)
            self.log(f"[SUCCESS] Exported: {os.path.basename(save_path)}", "primary")
            messagebox.showinfo("Matrix Engine", "Cleaned IPA exported successfully!")

        except Exception as e:
            self.log(f"[FAIL] Execution Error: {e}", "crimson")
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
        self.console.delete("1.0", "end")
        self.progress.set(0)
        self.btn_execute.configure(state="disabled")

if __name__ == "__main__":
    app = MatrixIPAStudio()
    app.mainloop()
