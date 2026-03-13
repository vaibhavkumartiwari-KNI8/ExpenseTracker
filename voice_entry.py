"""
Voice-based expense data entry
"""

import re
from datetime import datetime
from config import CATEGORIES, PAYMENT_METHODS

class VoiceDataEntry:
    """Handles voice-based expense entry"""
    
    def __init__(self, voice_assistant):
        self.va = voice_assistant
    
    def collect_expense_by_voice(self):
        """Collect all expense details via voice"""
        expense_data = {
            'amount': None,
            'category': None,
            'description': None,
            'payment_method': None,
            'date': datetime.now().date()
        }
        
        # Collect amount
        self.va.speak("Please say the expense amount. For example, say fifteen dollars and fifty cents")
        amount_text = self.listen_with_retry()
        expense_data['amount'] = self.parse_amount(amount_text)
        
        if expense_data['amount']:
            self.va.speak(f"Got it. {expense_data['amount']} dollars")
        else:
            self.va.speak("I couldn't understand the amount. Please enter it manually.")
            return None
        
        # Collect category
        self.va.speak("What category is this expense? Options are: " + 
                     ", ".join(CATEGORIES[:4]) + ", and others")
        category_text = self.listen_with_retry()
        expense_data['category'] = self.match_category(category_text, CATEGORIES)
        
        if expense_data['category']:
            self.va.speak(f"Category set to {expense_data['category']}")
        else:
            expense_data['category'] = 'Other'
            self.va.speak("Category set to Other")
        
        # Collect description
        self.va.speak("Please describe this expense briefly")
        description = self.listen_with_retry()
        expense_data['description'] = description if description not in ['timeout', 'error'] else ''
        
        # Collect payment method
        self.va.speak("How did you pay? Say credit card, debit card, cash, digital wallet, or bank transfer")
        payment_text = self.listen_with_retry()
        expense_data['payment_method'] = self.match_payment_method(payment_text)
        
        self.va.speak(f"Payment method: {expense_data['payment_method']}")
        
        return expense_data
    
    def listen_with_retry(self, max_retries=2):
        """Listen with retry mechanism"""
        for attempt in range(max_retries):
            result = self.va.listen()
            if result not in ['timeout', 'could not understand', 'service unavailable']:
                return result
            
            if attempt < max_retries - 1:
                self.va.speak("I didn't catch that. Please try again.")
        
        return 'error'
    
    def parse_amount(self, text):
        """Parse amount from voice text"""
        if not text or text in ['timeout', 'error']:
            return None
        
        # Remove common words
        text = text.lower().replace('dollars', '').replace('dollar', '')
        text = text.replace('cents', '').replace('cent', '')
        text = text.replace('and', '').strip()
        
        # Try direct number extraction
        match = re.search(r'(\d+\.?\d*)', text)
        if match:
            return float(match.group(1))
        
        # Number words to digits
        number_words = {
            'zero': 0, 'one': 1, 'two': 2, 'three': 3, 'four': 4,
            'five': 5, 'six': 6, 'seven': 7, 'eight': 8, 'nine': 9,
            'ten': 10, 'eleven': 11, 'twelve': 12, 'thirteen': 13,
            'fourteen': 14, 'fifteen': 15, 'sixteen': 16, 'seventeen': 17,
            'eighteen': 18, 'nineteen': 19, 'twenty': 20, 'thirty': 30,
            'forty': 40, 'fifty': 50, 'sixty': 60, 'seventy': 70,
            'eighty': 80, 'ninety': 90, 'hundred': 100, 'thousand': 1000
        }
        
        words = text.split()
        total = 0
        current = 0
        
        for word in words:
            if word in number_words:
                num = number_words[word]
                if num >= 100:
                    current *= num
                    total += current
                    current = 0
                else:
                    current += num
        
        total += current
        return float(total) if total > 0 else None
    
    def match_category(self, text, categories):
        """Match voice input to category"""
        if not text or text in ['timeout', 'error']:
            return None
        
        text = text.lower()
        
        # Direct matches
        for category in categories:
            if category.lower() in text:
                return category
        
        # Keyword matching
        category_keywords = {
            'Food & Dining': ['food', 'eat', 'restaurant', 'dining', 'lunch', 'dinner', 'breakfast'],
            'Transportation': ['transport', 'gas', 'fuel', 'taxi', 'uber', 'drive', 'car'],
            'Shopping': ['shop', 'store', 'buy', 'purchase', 'clothes', 'retail'],
            'Entertainment': ['fun', 'movie', 'game', 'entertainment', 'cinema', 'concert'],
            'Bills & Utilities': ['bill', 'utility', 'electric', 'water', 'internet', 'phone'],
            'Healthcare': ['health', 'medical', 'doctor', 'hospital', 'medicine', 'pharmacy'],
            'Education': ['education', 'school', 'book', 'course', 'tuition', 'study'],
            'Travel': ['travel', 'trip', 'hotel', 'flight', 'vacation', 'tourism']
        }
        
        for category, keywords in category_keywords.items():
            if any(keyword in text for keyword in keywords):
                return category
        
        return None
    
    def match_payment_method(self, text):
        """Match voice input to payment method"""
        if not text or text in ['timeout', 'error']:
            return 'Cash'
        
        text = text.lower()
        
        if 'credit' in text:
            return 'Credit Card'
        elif 'debit' in text:
            return 'Debit Card'
        elif 'cash' in text:
            return 'Cash'
        elif 'digital' in text or 'wallet' in text or 'paypal' in text or 'venmo' in text:
            return 'Digital Wallet'
        elif 'bank' in text or 'transfer' in text:
            return 'Bank Transfer'
        else:
            return 'Cash'