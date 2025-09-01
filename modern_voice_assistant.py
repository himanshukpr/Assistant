import tkinter as tk
from tkinter import ttk
import speech_recognition as sr
import pyttsx3
import threading
import time
from google import genai
import json
import os
from dotenv import load_dotenv
import platform
import subprocess
import queue
import re
from tkinter import font

# Load environment
load_dotenv()
operating_system = platform.platform()

class ModernVoiceAssistant:
    def __init__(self):
        self.conversation_history = []
        self.is_listening = False
        self.is_active = False
        self.is_wake_listening = True
        
        # Initialize TTS
        self.setup_tts()
        
        # Initialize Speech Recognition
        self.setup_speech_recognition()
        
        self.create_modern_ui()
        self.start_wake_word_detection()

    def setup_tts(self):
        """Setup Text-to-Speech engine"""
        try:
            self.tts_engine = pyttsx3.init()
            voices = self.tts_engine.getProperty('voices')
            if voices:
                # Try to set a female voice
                for voice in voices:
                    if 'female' in voice.name.lower() or 'zira' in voice.name.lower():
                        self.tts_engine.setProperty('voice', voice.id)
                        break
            self.tts_engine.setProperty('rate', 150)
            self.tts_engine.setProperty('volume', 0.8)
        except Exception as e:
            print(f"TTS setup failed: {e}")
            self.tts_engine = None

    def setup_speech_recognition(self):
        """Setup Speech Recognition"""
        try:
            self.recognizer = sr.Recognizer()
            self.microphone = sr.Microphone()
            with self.microphone as source:
                self.recognizer.adjust_for_ambient_noise(source, duration=1)
            self.recognizer.energy_threshold = 300
            self.recognizer.dynamic_energy_threshold = True
        except Exception as e:
            print(f"Speech recognition setup failed: {e}")

    def create_modern_ui(self):
        """Create modern popup UI similar to Cortana/Siri"""
        self.root = tk.Tk()
        self.root.title("Mia Bhai Assistant")
        self.root.geometry("450x600")
        
        # Modern dark theme
        self.bg_color = "#0d1117"
        self.card_color = "#161b22"
        self.accent_color = "#58a6ff"
        self.text_color = "#f0f6fc"
        self.success_color = "#238636"
        self.warning_color = "#d29922"
        self.error_color = "#da3633"
        
        self.root.configure(bg=self.bg_color)
        
        # Remove window decorations for modern look
        self.root.overrideredirect(True)
        
        # Make window stay on top and semi-transparent
        self.root.attributes('-topmost', True)
        self.root.attributes('-alpha', 0.95)
        
        # Add rounded corners effect with frame
        self.main_frame = tk.Frame(self.root, bg=self.card_color, relief='flat', bd=0)
        self.main_frame.pack(fill='both', expand=True, padx=5, pady=5)
        
        self.create_header()
        self.create_status_section()
        self.create_visualizer()
        self.create_chat_section()
        self.create_controls()
        
        # Hide window initially
        self.root.withdraw()
        
        # Bind drag functionality
        self.main_frame.bind('<Button-1>', self.start_drag)
        self.main_frame.bind('<B1-Motion>', self.drag_window)

    def create_header(self):
        """Create modern header"""
        header_frame = tk.Frame(self.main_frame, bg=self.card_color, height=60)
        header_frame.pack(fill='x', padx=20, pady=(20, 10))
        header_frame.pack_propagate(False)
        
        # Logo and title
        title_frame = tk.Frame(header_frame, bg=self.card_color)
        title_frame.pack(expand=True, fill='both')
        
        logo_label = tk.Label(title_frame, text="🤖", font=('Segoe UI Emoji', 24), 
                             bg=self.card_color, fg=self.accent_color)
        logo_label.pack(side='left', padx=(0, 10))
        
        title_label = tk.Label(title_frame, text="Mia Bhai", 
                              font=('Segoe UI', 18, 'bold'), 
                              bg=self.card_color, fg=self.text_color)
        title_label.pack(side='left', anchor='w')
        
        subtitle_label = tk.Label(title_frame, text="AI Voice Assistant", 
                                 font=('Segoe UI', 10), 
                                 bg=self.card_color, fg='#8b949e')
        subtitle_label.pack(side='left', anchor='w', padx=(10, 0))

    def create_status_section(self):
        """Create status indicator section"""
        status_frame = tk.Frame(self.main_frame, bg=self.card_color)
        status_frame.pack(fill='x', padx=20, pady=10)
        
        # Status indicator with pulsing effect
        indicator_frame = tk.Frame(status_frame, bg=self.card_color)
        indicator_frame.pack()
        
        self.status_indicator = tk.Label(indicator_frame, text="●", 
                                        font=('Arial', 20), 
                                        bg=self.card_color, fg=self.warning_color)
        self.status_indicator.pack()
        
        self.status_text = tk.Label(status_frame, text="Say 'Bhai' to activate", 
                                   font=('Segoe UI', 11), 
                                   bg=self.card_color, fg='#8b949e')
        self.status_text.pack(pady=(5, 0))

    def create_visualizer(self):
        """Create voice visualizer"""
        viz_frame = tk.Frame(self.main_frame, bg=self.card_color)
        viz_frame.pack(fill='x', padx=20, pady=10)
        
        self.voice_canvas = tk.Canvas(viz_frame, width=400, height=80, 
                                     bg=self.card_color, highlightthickness=0)
        self.voice_canvas.pack()

    def create_chat_section(self):
        """Create chat display section"""
        chat_frame = tk.Frame(self.main_frame, bg=self.card_color)
        chat_frame.pack(fill='both', expand=True, padx=20, pady=10)
        
        # Chat header
        chat_header = tk.Label(chat_frame, text="Conversation", 
                              font=('Segoe UI', 12, 'bold'), 
                              bg=self.card_color, fg=self.text_color)
        chat_header.pack(anchor='w', pady=(0, 10))
        
        # Scrollable chat area
        chat_container = tk.Frame(chat_frame, bg=self.bg_color, relief='flat', bd=1)
        chat_container.pack(fill='both', expand=True)
        
        self.chat_text = tk.Text(chat_container, bg=self.bg_color, fg=self.text_color, 
                                font=('Segoe UI', 10), wrap='word', relief='flat', bd=0,
                                selectbackground=self.accent_color, insertbackground=self.text_color)
        
        scrollbar = tk.Scrollbar(chat_container, command=self.chat_text.yview, 
                                bg=self.card_color, troughcolor=self.bg_color)
        self.chat_text.config(yscrollcommand=scrollbar.set)
        
        self.chat_text.pack(side='left', fill='both', expand=True, padx=10, pady=10)
        scrollbar.pack(side='right', fill='y')

    def create_controls(self):
        """Create control buttons"""
        control_frame = tk.Frame(self.main_frame, bg=self.card_color)
        control_frame.pack(fill='x', padx=20, pady=(10, 20))
        
        # Modern buttons
        button_style = {
            'font': ('Segoe UI', 10),
            'relief': 'flat',
            'bd': 0,
            'padx': 20,
            'pady': 8,
            'cursor': 'hand2'
        }
        
        self.minimize_btn = tk.Button(control_frame, text="Minimize", 
                                     bg='#21262d', fg=self.text_color,
                                     command=self.hide_window, **button_style)
        self.minimize_btn.pack(side='left', padx=(0, 10))
        
        self.close_btn = tk.Button(control_frame, text="Close", 
                                  bg=self.error_color, fg='white',
                                  command=self.close_app, **button_style)
        self.close_btn.pack(side='right')

    def start_drag(self, event):
        """Start dragging the window"""
        self.drag_start_x = event.x
        self.drag_start_y = event.y

    def drag_window(self, event):
        """Drag the window"""
        x = self.root.winfo_x() + event.x - self.drag_start_x
        y = self.root.winfo_y() + event.y - self.drag_start_y
        self.root.geometry(f'+{x}+{y}')

    def center_window(self):
        """Center window on screen"""
        self.root.update_idletasks()
        width = self.root.winfo_width()
        height = self.root.winfo_height()
        x = (self.root.winfo_screenwidth() // 2) - (width // 2)
        y = (self.root.winfo_screenheight() // 2) - (height // 2)
        self.root.geometry(f'{width}x{height}+{x}+{y}')

    def show_window(self):
        """Show popup with animation effect"""
        self.center_window()
        self.root.deiconify()
        self.root.lift()
        self.root.attributes('-topmost', True)
        
        # Fade in animation
        for alpha in range(0, 96, 5):
            self.root.attributes('-alpha', alpha/100)
            self.root.update()
            time.sleep(0.01)

    def hide_window(self):
        """Hide window with animation"""
        # Fade out animation
        for alpha in range(95, 0, -5):
            self.root.attributes('-alpha', alpha/100)
            self.root.update()
            time.sleep(0.01)
        
        self.root.withdraw()
        self.is_active = False
        self.update_status("Say 'Bhai' to activate", self.warning_color)

    def close_app(self):
        """Close the application"""
        self.is_wake_listening = False
        self.root.quit()

    def update_status(self, text, color):
        """Update status with color"""
        self.status_text.config(text=text)
        self.status_indicator.config(fg=color)

    def add_to_chat(self, message, sender="Assistant"):
        """Add message to chat with styling"""
        timestamp = time.strftime("%H:%M")
        if sender == "You":
            self.chat_text.insert(tk.END, f"[{timestamp}] You: {message}\n\n", "user")
        else:
            self.chat_text.insert(tk.END, f"[{timestamp}] Mia Bhai: {message}\n\n", "assistant")
        
        # Configure text tags for styling
        self.chat_text.tag_config("user", foreground="#58a6ff")
        self.chat_text.tag_config("assistant", foreground="#238636")
        
        self.chat_text.see(tk.END)

    def animate_listening(self):
        """Animate voice bars while listening"""
        if self.is_listening:
            self.voice_canvas.delete("all")
            for i in range(8):
                height = 10 + (30 * abs(0.5 - ((time.time() * 3 + i * 0.5) % 1)))
                x = 40 + i * 40
                self.voice_canvas.create_rectangle(x, 60, x+20, 60-height, 
                                                 fill=self.accent_color, outline="")
            self.root.after(50, self.animate_listening)
        else:
            self.voice_canvas.delete("all")

    def speak(self, text):
        """Convert text to speech"""
        if self.tts_engine:
            def tts_thread():
                self.tts_engine.say(text)
                self.tts_engine.runAndWait()
            
            thread = threading.Thread(target=tts_thread)
            thread.daemon = True
            thread.start()

    def listen_for_speech(self, timeout=8):
        """Listen for speech with visual feedback"""
        try:
            with self.microphone as source:
                self.update_status("Listening...", self.success_color)
                self.is_listening = True
                self.animate_listening()
                
                audio = self.recognizer.listen(source, timeout=timeout, phrase_time_limit=15)
                
                self.is_listening = False
                self.update_status("Processing...", self.accent_color)
                
                text = self.recognizer.recognize_google(audio)
                return text.lower()
                
        except sr.UnknownValueError:
            self.is_listening = False
            return "Could not understand audio"
        except sr.RequestError as e:
            self.is_listening = False
            return f"Speech recognition error: {e}"
        except Exception as e:
            self.is_listening = False
            return f"Error: {e}"

    def process_command(self, command):
        """Process voice command with AI"""
        try:
            self.conversation_history.append({'role': 'user', 'content': command})
            self.add_to_chat(command, "You")
            
            # Since wake word "bhai" was already detected, process the command directly
            # No need to check for prefix in the actual command
            # Process with AI
            api_key = os.environ.get('GEMINI_API_KEY')
            if not api_key:
                error_msg = "API key not configured. Please check your .env file."
                self.add_to_chat(error_msg)
                self.speak(error_msg)
                return
            
            client = genai.Client(api_key=api_key)
            self.update_status("AI is thinking...", self.accent_color)
            
            response = client.models.generate_content(
                model="gemini-2.5-flash",
                contents=f"""user asked {command},

                user have asked to do something and you have to answer the query
                and if the user have asked to open something that time you just have to provide the commmand to run in the terminal of the {operating_system},
                and also make sure that if you are giving the command to run in terminal that time the response must not include any single markdown text.
                also if the user is commanding to do something in the system that time you need to just provide the terminal command in such a way that they get executed directly and this response should also not include any type of single markdown content
                but make sure that you are returning the dictionary as the response if response is command that time the result must be, all the following stuructures have to follow strictly:
                "type":"command", "command":"command", "fail_audio":"msg to show if command faild"

                if there is only result as response:
                "type":"response", "content":"content"

                one more condition you are also provided with the all the privious conversation history also and all the history is:
                {self.conversation_history} so you need to also respond according to that.
                """,
            )
            
            # Parse response safely
            try:
                result = json.loads(response.text)
            except:
                result = {"type": "response", "content": response.text}
            
            self.conversation_history.append({'role': 'system', 'content': result})
            
            # Handle response
            if result.get('type') == 'command':
                command_text = result.get('command', '')
                self.add_to_chat(f"Executing: {command_text}")
                self.speak(f"Executing: {command_text}")
                
                try:
                    subprocess.run(command_text, shell=True)
                    success_msg = "Command executed successfully"
                    self.add_to_chat(success_msg)
                    self.speak("Done!")
                except Exception as e:
                    error_msg = result.get('fail_audio', 'Command failed')
                    self.add_to_chat(f"Error: {error_msg}")
                    self.speak(error_msg)
            else:
                response_content = result.get('content', 'No response received')
                self.add_to_chat(response_content)
                self.speak(response_content)
                
            self.update_status("Command completed", self.success_color)
            
        except Exception as e:
            error_msg = f"Error: {str(e)}"
            self.add_to_chat(f"System Error: {error_msg}")
            self.speak("Sorry, there was an error processing your request.")
            self.update_status("Error occurred", self.error_color)

    def start_wake_word_detection(self):
        """Background wake word detection"""
        def wake_word_listener():
            print("🎤 Wake word detection started...")
            print("Say 'Bhai' to activate!")
            
            while self.is_wake_listening:
                try:
                    if not self.is_active:
                        with self.microphone as source:
                            # Listen for short phrases
                            audio = self.recognizer.listen(source, timeout=1, phrase_time_limit=4)
                        
                        try:
                            text = self.recognizer.recognize_google(audio).lower()
                            print(f"Heard: {text}")
                            
                            # Check for wake words
                            if any(wake_word in text for wake_word in ['bhai']):
                                print("🚀 Wake word detected!")
                                self.is_active = True
                                self.show_window()
                                self.speak("Yes, I'm listening!")
                                
                                # Listen for the actual command
                                command = self.listen_for_speech(timeout=10)
                                if command and "error" not in command.lower():
                                    print(f"Command: {command}")
                                    self.process_command(command)
                                else:
                                    self.speak("I didn't catch that. Please try again.")
                                    self.update_status("Say 'Bhai' to activate", self.warning_color)
                                
                                # Auto-hide after 5 seconds of inactivity
                                self.root.after(5000, self.hide_window)
                                
                        except sr.UnknownValueError:
                            pass  # Continue listening
                        except sr.RequestError:
                            time.sleep(1)
                            
                except Exception as e:
                    print(f"Wake word detection error: {e}")
                    time.sleep(1)
        
        # Start wake word detection in background
        thread = threading.Thread(target=wake_word_listener)
        thread.daemon = True
        thread.start()

    def run(self):
        """Start the voice assistant"""
        print("🤖 Mia Bhai Voice Assistant Starting...")
        print("💬 Say 'Bhai' anywhere to activate!")
        print("🎯 The popup will appear when activated")
        print("📱 Drag the popup to move it around")
        self.root.mainloop()

if __name__ == "__main__":
    try:
        assistant = ModernVoiceAssistant()
        assistant.run()
    except KeyboardInterrupt:
        print("\n👋 Assistant stopped by user")
    except Exception as e:
        print(f"❌ Error starting assistant: {e}")
        input("Press Enter to exit...")
