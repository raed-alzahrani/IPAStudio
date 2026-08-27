# IPAStudio

A lightweight, no-nonsense iOS Application Archive (.ipa) toolkit built with Python & CustomTkinter. Designed to quickly spoof metadata, patch hardcoded Unity asset versions, clean expired signature junk, and inject custom tweaks without messing up binary structures.

---

## Features

- **Metadata & Version Spoofing:** Change CFBundleShortVersionString, CFBundleVersion, App Display Name, or Bundle ID on the fly.
- **Unity Asset Version Patcher:** Scans and patches hardcoded version strings embedded inside Unity data files.
- **Dynamic Library Injector:** Inject raw .dylib files or extract and pack .deb tweaks straight into the Frameworks/ folder.
- **Signature Cleaner:** Strips old _CodeSignature folders and expired provisioning profiles for smooth sideloading via ESign, Scarlet, TrollStore, etc.
- **Drag & Drop:** Drop your .ipa, .dylib, or .deb files anywhere on the app window.
- **Themes & Monospace Fonts:** Multiple color themes, dark/light toggle, and clean monospace font profiles.
- **In-App Updater:** Hot-update and test script changes directly without leaving the app.
- **Desktop Shortcut & Icon Builder:** 1-click desktop shortcut creator and automatic image-to-ICO converter.
- **Auto Dependency Installer:** Automatically catches missing libraries and installs them via batch on startup.

---

## Installation & Setup

1. Clone the repo:
   git clone https://github.com/raed-alzahrani/IPAStudio.git
   cd IPAStudio

2. Install dependencies:
   pip install -r requirements.txt

3. Run the app:
   python main.pyw
   (Or just double-click main.pyw on Windows).

---

## Requirements

- Python 3.8+
- customtkinter >= 5.2.0
- pillow >= 10.0.0
- tkinterdnd2 >= 0.3.0

---

## License

Licensed under the MIT License (LICENSE).