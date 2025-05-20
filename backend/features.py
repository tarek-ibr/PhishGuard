import pandas as pd
from urllib.parse import urlparse
import re
from collections import Counter
import numpy as np

def extract_all_features_df(url):
    parsed = urlparse(url)
    domain = parsed.netloc
    features = {}

    # --- Basic structural features ---
    features['URLLength'] = len(url)
    features['DomainLength'] = len(domain)
    features['IsDomainIP'] = int(bool(re.match(r'\d+\.\d+\.\d+\.\d+', domain)))
    features['TLD'] = domain.split('.')[-1] if '.' in domain else ''
    features['TLDLength'] = len(features['TLD'])
    features['CharContinuationRate'] = len(re.findall(r'(.)\1{2,}', url)) / len(url) if len(url) > 0 else 0

    # --- Obfuscation ---
    features['HasObfuscation'] = int('//' in url or '\\' in url)
    features['NoOfObfuscatedChar'] = url.count('//') + url.count('\\')
    features['ObfuscationRatio'] = features['NoOfObfuscatedChar'] / len(url) if len(url) > 0 else 0

    # --- Character composition ---
    features['LetterRatioInURL'] = sum(c.isalpha() for c in url) / len(url) if len(url) > 0 else 0
    features['DegitRatioInURL'] = sum(c.isdigit() for c in url) / len(url) if len(url) > 0 else 0

    # --- Special characters ---
    features['NoOfEqualsInURL'] = url.count('=')
    features['NoOfQMarkInURL'] = url.count('?')
    features['NoOfAmpersandInURL'] = url.count('&')

    special_chars = re.findall(r'[^A-Za-z0-9]', url)
    known_specials = features['NoOfEqualsInURL'] + features['NoOfQMarkInURL'] + features['NoOfAmpersandInURL']
    features['SpacialCharRatioInURL'] = len(special_chars) / len(url) if len(url) > 0 else 0

    # --- Character probability ---
    char_counts = Counter(url)
    total_chars = sum(char_counts.values())
    char_probs = [count / total_chars for count in char_counts.values()]
    features['URLCharProb'] = np.mean(char_probs)

    # --- Protocol ---
    features['IsHTTPS'] = int(parsed.scheme == 'https')

    # --- Keyword indicators ---
    lower_url = url.lower()
    features['Bank'] = int('bank' in lower_url)
    features['Pay'] = int('pay' in lower_url)
    features['Crypto'] = int('crypto' in lower_url)

    return pd.DataFrame([features])
