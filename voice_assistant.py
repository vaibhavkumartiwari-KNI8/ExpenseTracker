"""
Voice Assistant for command processing and text-to-speech
"""

import speech_recognition as sr
import pyttsx3
import re
from datetime import datetime

class VoiceAssistant:
    """AI Voice Assistant for expense tracking"""
    
    def __init__(self, voice_speed=150, voice_volume=0.9):
        self.recognizer = sr.Recognizer()
        self.engine = pyttsx3.init()
        self.engine.setProperty('rate', voice_speed)
        self.engine.setProperty('volume', voice_volume)
        
        # Set voice preference (female voice if available)
        voices = self.engine.getProperty('voices')
        if voices:
            for voice in voices:
                if 'female' in voice.name.lower() or 'zira' in voice.name.lower():
                    self.engine.setProperty('voice', voice.id)
                    break
    
    def speak(self, text, pause_duration=0.5):
        """Convert text to speech"""
        try:
            clean_text = self.clean_text_for_speech(text)
            sentences = re.split(r'[.!?]\s+', clean_text)
            
            for sentence in sentences:
                if sentence.strip():
                    self.engine.say(sentence)
                    self.engine.runAndWait()
            
            return True
        except Exception as e:
            print(f"Voice output error: {e}")
            return False
    
    def clean_text_for_speech(self, text):
        """Clean and format text for natural speech"""
        # Remove markdown formatting
        text = re.sub(r'[*#_`]', '', text)
        
        # Replace symbols with words
        replacements = {
            '$': 'dollars ',
            '%': ' percent',
            '&': ' and ',
            '@': ' at ',
            '€': 'euros ',
            '£': 'pounds ',
            '₹': 'rupees ',
            '📊': '', '💰': '', '📈': '', '📉': '',
            '⚠️': 'Warning: ', '✅': '', 'ℹ️': '',
            '💡': '', '🏆': '', '💳': '', '📅': '', '⚡': 'Alert: '
        }
        
        for symbol, word in replacements.items():
            text = text.replace(symbol, word)
        
        return text
    
    def listen(self, timeout=5):
        """Listen to user voice input"""
        try:
            with sr.Microphone() as source:
                self.recognizer.adjust_for_ambient_noise(source, duration=0.5)
                audio = self.recognizer.listen(source, timeout=timeout)
                text = self.recognizer.recognize_google(audio)
                return text.lower()
        except sr.WaitTimeoutError:
            return "timeout"
        except sr.UnknownValueError:
            return "could not understand"
        except sr.RequestError:
            return "service unavailable"
        except Exception as e:
            return "error"
    
    def process_voice_command(self, command, expenses_df):
        """Process voice commands and generate responses"""
        command = command.lower()
        
        # Voice entry
        if "add expense" in command or "record expense" in command or "new expense" in command:
            return "voice_entry", "Let me help you add an expense. I'll ask you a few questions."
        
        # Scan receipt
        if "scan receipt" in command or "upload receipt" in command:
            return "scan_receipt", "Please upload a receipt image to scan."
        
        # Read report
        if "read report" in command or "speak report" in command:
            return "read_full_report", "I'll read your complete expense report now."
        
        elif "summarize" in command or "summary" in command:
            return "read_summary", "Here's a brief summary of your expenses."
        
        # Show total
        elif "total spending" in command or "how much spent" in command:
            if expenses_df.empty:
                return "info", "You haven't recorded any expenses yet."
            total = expenses_df['amount'].sum()
            return "info", f"Your total spending is {total:.2f} dollars"
        
        # Categories
        elif "spending by category" in command or "categories" in command:
            if expenses_df.empty:
                return "info", "No expenses recorded yet."
            category_totals = expenses_df.groupby('category')['amount'].sum().sort_values(ascending=False).to_dict()
            response = "Here's your spending by category. "
            for i, (cat, amt) in enumerate(category_totals.items(), 1):
                response += f"{i}. {cat}: {amt:.2f} dollars. "
            return "info", response
        
        # This month
        elif "this month" in command:
            if expenses_df.empty:
                return "info", "No expenses recorded for this month."
            current_month = datetime.now().month
            month_expenses = expenses_df[expenses_df['date'].dt.month == current_month]
            total = month_expenses['amount'].sum()
            count = len(month_expenses)
            return "info", f"This month you've spent {total:.2f} dollars across {count} transactions"
        
        # Help
        elif "help" in command:
            return "help", """I can help you with:
            Say 'add expense' to record a new expense by voice.
            Say 'scan receipt' to upload and scan a receipt.
            Say 'read report' for a complete expense report.
            Say 'total spending' to hear your total expenses.
            Say 'spending by category' for category breakdown."""
        
        else:
            return "unknown", "I didn't understand that. Try saying 'help' to see what I can do."
    
    def set_voice_properties(self, speed, volume):
        """Update voice speed and volume"""
        self.engine.setProperty('rate', speed)
        self.engine.setProperty('volume', volume)