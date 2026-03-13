"""
Configuration settings for Smart Expense Tracker
"""

import os

# Database Configuration
DATABASE_PATH = 'expenses.db'

# Receipt Storage
RECEIPTS_DIR = 'receipts'
if not os.path.exists(RECEIPTS_DIR):
    os.makedirs(RECEIPTS_DIR)

# Tesseract OCR Path
TESSERACT_PATH = {
    'Windows': r'C:\Program Files\Tesseract-OCR\tesseract.exe',
    'Darwin': '/usr/local/bin/tesseract',  # Mac
    'Linux': '/usr/bin/tesseract'
}

# Categories
CATEGORIES = [
    "Food & Dining",
    "Transportation",
    "Shopping",
    "Entertainment",
    "Bills & Utilities",
    "Healthcare",
    "Education",
    "Travel",
    "Other"
]

# Payment Methods
PAYMENT_METHODS = [
    "Credit Card",
    "Debit Card",
    "Cash",
    "Digital Wallet",
    "Bank Transfer"
]

# Voice Settings
DEFAULT_VOICE_SPEED = 150
DEFAULT_VOICE_VOLUME = 0.9

# OCR Settings
OCR_LANGUAGE = 'eng'

# Category Keywords for Auto-categorization
CATEGORY_KEYWORDS = {
    'Food & Dining': ['restaurant', 'cafe', 'pizza', 'burger', 'starbucks', 
                      'mcdonald', 'food', 'kitchen', 'dining', 'bakery'],
    'Shopping': ['store', 'mart', 'shop', 'retail', 'walmart', 'target', 
                 'amazon', 'mall', 'boutique'],
    'Transportation': ['gas', 'fuel', 'uber', 'lyft', 'taxi', 'parking', 
                      'metro', 'bus', 'train'],
    'Entertainment': ['cinema', 'movie', 'theatre', 'netflix', 'spotify', 
                     'game', 'concert', 'ticket'],
    'Healthcare': ['pharmacy', 'hospital', 'clinic', 'medical', 'cvs', 
                   'walgreens', 'doctor', 'health'],
    'Bills & Utilities': ['electric', 'water', 'internet', 'phone', 'utility', 
                         'bill', 'subscription'],
    'Education': ['school', 'college', 'university', 'book', 'course', 
                  'tuition', 'academy'],
    'Travel': ['hotel', 'flight', 'airbnb', 'booking', 'travel', 'tourism', 
              'airline']
}