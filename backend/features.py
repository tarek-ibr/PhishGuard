import pandas as pd
from urllib.parse import urlparse
import re
from collections import Counter
import numpy as np

# Static lookup for TLD legitimacy probability
TLD_PROBABILITY_MAP = {
    'com': 0.95,
    'org': 0.90,
    'net': 0.90,
    'gov': 0.98,
    'edu': 0.97,
    'io': 0.85,
    'co': 0.85,
    'us': 0.80,
    'biz': 0.75,
    'info': 0.70,
    'xyz': 0.40,
    'top': 0.30,
    'tk': 0.20,
    'ml': 0.20,
    'gq': 0.10,
    'cf': 0.10
}

def extract_all_features_df(url):
    parsed = urlparse(url)
    domain = parsed.netloc
    features = {}

    features['URLLength'] = len(url)
    features['DomainLength'] = len(domain)
    features['IsDomainIP'] = int(bool(re.match(r'\d+\.\d+\.\d+\.\d+', domain)))

    features['CharContinuationRate'] = len(re.findall(r'(.)\1{2,}', url)) / len(url) if len(url) > 0 else 0

    features['TLD'] = domain.split('.')[-1] if '.' in domain else ''

    tld = features['TLD'].lower()

    features['TLDLegitimateProb'] = TLD_PROBABILITY_MAP.get(tld, 0.5)  # Default 0.5 if unknown

    char_counts = Counter(url)
    total_chars = sum(char_counts.values())
    char_probs = [count / total_chars for count in char_counts.values()]

    features['URLCharProb'] = np.mean(char_probs)

    features['TLDLength'] = len(features['TLD'])

    features['HasObfuscation'] = int('//' in url or '\\' in url)

    features['NoOfObfuscatedChar'] = url.count('//') + url.count('\\')

    features['ObfuscationRatio'] = features['NoOfObfuscatedChar'] / len(url) if len(url) > 0 else 0

    features['LetterRatioInURL'] = sum(c.isalpha() for c in url) / len(url) if len(url) > 0 else 0

    features['DegitRatioInURL'] = sum(c.isdigit() for c in url) / len(url) if len(url) > 0 else 0

    features['NoOfEqualsInURL'] = url.count('=')

    features['NoOfQMarkInURL'] = url.count('?')

    features['NoOfAmpersandInURL'] = url.count('&')

    special_chars = re.findall(r'[^A-Za-z0-9]', url)

    features['SpacialCharRatioInURL'] = len(special_chars) / len(url) if len(url) > 0 else 0

    features['IsHTTPS'] = int(parsed.scheme == 'https')



    # Keyword flags
    lower_url = url.lower()
    features['Bank'] = int('bank' in lower_url)
    features['Pay'] = int('pay' in lower_url)
    features['Crypto'] = int('crypto' in lower_url)




    # Drop helper keys
    features.pop('TLD')  # Remove intermediate 'TLD' column if not used in your model

    return pd.DataFrame([features])
