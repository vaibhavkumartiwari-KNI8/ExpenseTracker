"""
OCR Receipt Scanner
"""

import pytesseract
import cv2
import numpy as np
from PIL import Image
import re
from datetime import datetime
import os
import platform
from config import TESSERACT_PATH, RECEIPTS_DIR, CATEGORY_KEYWORDS
import pytesseract
from PIL import Image

# Add this line - adjust path if your installation is different
pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'
class ReceiptScanner:
    """Scans and extracts data from receipt images"""
    
    def __init__(self):
        """Initialize OCR engine"""
        # Set tesseract path based on OS
        system = platform.system()
        if system in TESSERACT_PATH and os.path.exists(TESSERACT_PATH[system]):
            pytesseract.pytesseract.tesseract_cmd = TESSERACT_PATH[system]
    
    def preprocess_image(self, image):
        """Preprocess image for better OCR"""
        # Convert PIL to OpenCV format
        img = cv2.cvtColor(np.array(image), cv2.COLOR_RGB2BGR)
        
        # Convert to grayscale
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        
        # Apply thresholding
        _, thresh = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
        
        # Denoise
        denoised = cv2.fastNlMeansDenoising(thresh, None, 10, 7, 21)
        
        return denoised
    
    def extract_text(self, image):
        """Extract text from image using OCR"""
        try:
            # Preprocess
            processed = self.preprocess_image(image)
            
            # OCR
            text = pytesseract.image_to_string(processed)
            return text
        except Exception as e:
            return f"OCR Error: {str(e)}"
    
    def parse_receipt(self, text):
        """Parse receipt text to extract expense data"""
        data = {
            'amount': None,
            'date': None,
            'merchant': None,
            'items': [],
            'category': 'Other'
        }
        
        # Extract amount (various patterns)
        amount_patterns = [
            r'TOTAL[:\s]+\$?(\d+\.?\d*)',
            r'AMOUNT[:\s]+\$?(\d+\.?\d*)',
            r'GRAND TOTAL[:\s]+\$?(\d+\.?\d*)',
            r'\$(\d+\.\d{2})',
            r'(\d+\.\d{2})\s*$'
        ]
        
        for pattern in amount_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                try:
                    data['amount'] = float(match.group(1))
                    break
                except:
                    pass
        
        # Extract date
        date_patterns = [
            r'(\d{1,2}[/-]\d{1,2}[/-]\d{2,4})',
            r'(\d{4}[/-]\d{1,2}[/-]\d{1,2})',
            r'(Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)\s+\d{1,2},?\s+\d{4}'
        ]
        
        for pattern in date_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                try:
                    from dateutil import parser
                    data['date'] = parser.parse(match.group(0)).date()
                    break
                except:
                    pass
        
        # Default to today if no date found
        if not data['date']:
            data['date'] = datetime.now().date()
        
        # Extract merchant (usually first line)
        lines = text.strip().split('\n')
        if lines:
            data['merchant'] = lines[0].strip()[:50]
        
        # Auto-categorize based on merchant keywords
        merchant_lower = data['merchant'].lower() if data['merchant'] else ''
        for category, keywords in CATEGORY_KEYWORDS.items():
            if any(keyword in merchant_lower for keyword in keywords):
                data['category'] = category
                break
        
        return data
    
    def save_receipt_image(self, image, expense_id):
        """Save receipt image to disk"""
        if not os.path.exists(RECEIPTS_DIR):
            os.makedirs(RECEIPTS_DIR)
        
        filename = f"receipt_{expense_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
        filepath = os.path.join(RECEIPTS_DIR, filename)
        
        image.save(filepath)
        return filepath