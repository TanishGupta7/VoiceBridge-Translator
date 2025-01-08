import ttkbootstrap as ttk
from ttkbootstrap.constants import *
from tkinter import Text, messagebox, filedialog, simpledialog
from googletrans import Translator, LANGUAGES
import pyttsx3
import pyperclip
import speech_recognition as sr
from datetime import datetime
import threading


class TranslatorApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Voice Bridge")
        self.root.geometry("800x800")
        self.root.resizable(False, False)

        # Theme Variables
        self.theme = ttk.Style(theme="superhero")
        self.is_dark_mode = True

        # Initialize Google Translator
        self.translator = Translator()

        # Initialize Text-to-Speech Engine
        self.tts_engine = self.init_tts_engine()

        # Speech Recognition
        self.recognizer = sr.Recognizer()
        self.is_listening = False

        # Translation History
        self.history = []

        # Build UI
        self.create_widgets()

    def init_tts_engine(self):
        try:
            engine = pyttsx3.init()
            return engine
        except Exception as e:
            messagebox.showerror("TTS Error", f"Failed to initialize text-to-speech engine: {str(e)}")
            return None

    def create_widgets(self):
        # Title Label
        ttk.Label(self.root, text="Voice Bridge", font=("Arial", 24, "bold"), anchor=CENTER).pack(pady=10)

        # Source Text Section
        ttk.Label(self.root, text="Source Text:", font=("Arial", 14)).pack(pady=5, anchor=W, padx=20)
        self.source_text = Text(self.root, font=("Arial", 12), wrap="word", height=7)
        self.source_text.pack(padx=20, pady=5, fill=X)
        self.detected_lang_label = ttk.Label(self.root, text="", font=("Arial", 10), foreground="green")
        self.detected_lang_label.pack(pady=2)

        # Language Selection
        language_frame = ttk.Frame(self.root)
        language_frame.pack(pady=10, fill=X, padx=20)

        self.source_lang = ttk.Combobox(language_frame, values=["auto"] + list(LANGUAGES.values()), width=25, state="readonly")
        self.source_lang.grid(row=0, column=0, padx=10)
        self.source_lang.set("auto")

        ttk.Button(language_frame, text="↔", bootstyle=SECONDARY, command=self.swap_languages, width=3).grid(row=0, column=1, padx=10)

        self.dest_lang = ttk.Combobox(language_frame, values=list(LANGUAGES.values()), width=25, state="readonly")
        self.dest_lang.grid(row=0, column=2, padx=10)
        self.dest_lang.set("English")

        ttk.Button(self.root, text="Translate", bootstyle=SUCCESS, command=self.translate_text).pack(pady=5)

        # Destination Text Section
        ttk.Label(self.root, text="Translated Text:", font=("Arial", 14)).pack(pady=5, anchor=W, padx=20)
        self.dest_text = Text(self.root, font=("Arial", 12), wrap="word", height=7)
        self.dest_text.pack(padx=20, pady=5, fill=X)

        # Action Buttons
        action_frame = ttk.Frame(self.root)
        action_frame.pack(pady=10, fill=X, padx=20)

        ttk.Button(action_frame, text="Clear", bootstyle=INFO, command=self.clear_texts, width=10).grid(row=0, column=0, padx=5)
        ttk.Button(action_frame, text="Copy", bootstyle=PRIMARY, command=self.copy_to_clipboard, width=10).grid(row=0, column=1, padx=5)
        ttk.Button(action_frame, text="Speak", bootstyle=WARNING, command=self.text_to_speech, width=10).grid(row=0, column=2, padx=5)
        ttk.Button(action_frame, text="Paste", bootstyle=INFO, command=self.paste_from_clipboard, width=10).grid(row=0, column=3, padx=5)
        ttk.Button(action_frame, text="Start Speaking", bootstyle=DANGER, command=self.start_speech_to_text, width=12).grid(row=0, column=4, padx=5)
        ttk.Button(action_frame, text="Stop Speaking", bootstyle=DANGER, command=self.stop_speech_to_text, width=12).grid(row=0, column=5, padx=5)

        # Listening Status
        self.listening_label = ttk.Label(self.root, text="", font=("Arial", 12), foreground="red")
        self.listening_label.pack(pady=5)

        # Additional Features
        feature_frame = ttk.Frame(self.root)
        feature_frame.pack(pady=10, fill=X, padx=20)

        ttk.Button(feature_frame, text="Export", bootstyle=SECONDARY, command=self.export_translation, width=10).grid(row=0, column=0, padx=5)
        ttk.Button(feature_frame, text="History", bootstyle=SECONDARY, command=self.show_history, width=10).grid(row=0, column=1, padx=5)
        ttk.Button(feature_frame, text="Font Size", bootstyle=SECONDARY, command=self.change_font_size, width=10).grid(row=0, column=2, padx=5)
        ttk.Button(feature_frame, text="Toggle Theme", bootstyle=SECONDARY, command=self.switch_theme, width=13).grid(row=0, column=3, padx=5)

    def translate_text(self):
        src_lang = self.source_lang.get()
        dest_lang = self.dest_lang.get()
        text = self.source_text.get(1.0, "end").strip()

        if not text:
            messagebox.showwarning("Input Error", "Please enter text to translate.")
            return

        try:
            translated = self.translator.translate(text, src=src_lang, dest=dest_lang)
            self.dest_text.delete(1.0, "end")
            self.dest_text.insert("end", translated.text)

            if src_lang == "auto":
                detected_lang = LANGUAGES.get(translated.src, "Unknown")
                self.detected_lang_label.config(text=f"Detected Language: {detected_lang.capitalize()}")

            self.history.append({
                "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "source": text,
                "translation": translated.text,
                "languages": f"{src_lang} → {dest_lang}"
            })
        except Exception as e:
            messagebox.showerror("Translation Error", f"Error: {str(e)}")

    def swap_languages(self):
        src_lang = self.source_lang.get()
        dest_lang = self.dest_lang.get()
        self.source_lang.set(dest_lang)
        self.dest_lang.set(src_lang)

    def clear_texts(self):
        self.source_text.delete(1.0, "end")
        self.dest_text.delete(1.0, "end")
        self.detected_lang_label.config(text="")

    def copy_to_clipboard(self):
        text = self.dest_text.get(1.0, "end").strip()
        if text:
            pyperclip.copy(text)
            messagebox.showinfo("Copied", "Translated text copied to clipboard!")
        else:
            messagebox.showwarning("Copy Error", "No text to copy.")

    def paste_from_clipboard(self):
        text = pyperclip.paste()
        self.source_text.insert("end", text)

    def text_to_speech(self):
        if self.tts_engine is None:
            messagebox.showerror("TTS Error", "Text-to-speech engine is not initialized.")
            return

        text = self.dest_text.get(1.0, "end").strip()
        if text:
            try:
                # Set a specific voice
                voices = self.tts_engine.getProperty('voices')
                selected_voice = "male"  # Replace with user choice
                for voice in voices:
                    if selected_voice in voice.name.lower():
                        self.tts_engine.setProperty('voice', voice.id)
                        break

                self.tts_engine.say(text)
                self.tts_engine.runAndWait()
            except Exception as e:
                messagebox.showerror("TTS Error", f"Error: {str(e)}")
        else:
            messagebox.showwarning("Speak Error", "No text to speak.")

    def start_speech_to_text(self):
        if not self.is_listening:
            self.is_listening = True
            self.listening_label.config(text="Listening...")
            threading.Thread(target=self.listen_for_speech, daemon=True).start()

    def stop_speech_to_text(self):
        self.is_listening = False
        self.listening_label.config(text="")

    def listen_for_speech(self):
        while self.is_listening:
            try:
                with sr.Microphone() as source:
                    self.recognizer.adjust_for_ambient_noise(source)
                    audio = self.recognizer.listen(source)
                    text = self.recognizer.recognize_google(audio)
                    self.source_text.insert("end", text + " ")
            except sr.UnknownValueError:
                pass
            except Exception as e:
                if self.is_listening:
                    messagebox.showerror("Voice Input Error", f"Error: {str(e)}")
                    self.stop_speech_to_text()

    def switch_theme(self):
        new_theme = "flatly" if self.is_dark_mode else "superhero"
        self.theme = ttk.Style(theme=new_theme)
        self.theme.master = self.root
        self.is_dark_mode = not self.is_dark_mode

    def export_translation(self):
        text = self.dest_text.get(1.0, "end").strip()
        if text:
            file_path = filedialog.asksaveasfilename(defaultextension=".txt", filetypes=[("Text Files", "*.txt")])
            if file_path:
                with open(file_path, "w", encoding="utf-8") as file:
                    file.write(text)
                messagebox.showinfo("Export Success", "Translation exported successfully!")
        else:
            messagebox.showwarning("Export Error", "No text to export.")

    def show_history(self):
        history_window = ttk.Toplevel(self.root)
        history_window.title("Translation History")
        history_window.geometry("600x400")

        history_text = Text(history_window, font=("Arial", 12), wrap="word")
        history_text.pack(fill=BOTH, expand=True, padx=10, pady=10)

        for entry in self.history:
            history_text.insert("end", f"{entry['timestamp']} - {entry['languages']}\n")
            history_text.insert("end", f"Source: {entry['source']}\n")
            history_text.insert("end", f"Translation: {entry['translation']}\n\n")

        ttk.Button(history_window, text="Export History", command=self.export_history).pack(pady=10)

    def export_history(self):
        if self.history:
            file_path = filedialog.asksaveasfilename(defaultextension=".txt", filetypes=[("Text Files", "*.txt")])
            if file_path:
                with open(file_path, "w", encoding="utf-8") as file:
                    for entry in self.history:
                        file.write(f"{entry['timestamp']} - {entry['languages']}\n")
                        file.write(f"Source: {entry['source']}\n")
                        file.write(f"Translation: {entry['translation']}\n\n")
                messagebox.showinfo("Export Success", "History exported successfully!")
        else:
            messagebox.showwarning("Export Error", "No history to export.")

    def change_font_size(self):
        new_size = simpledialog.askinteger("Font Size", "Enter font size:", minvalue=8, maxvalue=32)
        if new_size:
            self.source_text.config(font=("Arial", new_size))
            self.dest_text.config(font=("Arial", new_size))


if __name__ == "__main__":
    root = ttk.Window(themename="superhero")
    app = TranslatorApp(root)
    root.mainloop()
