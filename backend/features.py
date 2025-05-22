from urllib.parse import urlparse
import re
from collections import Counter
import numpy as np

# Static lookup for TLD legitimacy probability
TLD_PROBABILITY_MAP = {
    'com': 0.95, 'org': 0.90, 'net': 0.90, 'gov': 0.98, 'edu': 0.97,
    'io': 0.85, 'co': 0.85, 'us': 0.80, 'biz': 0.75, 'info': 0.70,
    'xyz': 0.40, 'top': 0.30, 'tk': 0.20, 'ml': 0.20, 'gq': 0.10, 'cf': 0.10
}

def extract_all_features_df(url):
    parsed = urlparse(url)
    domain = parsed.netloc
    features = {}

    # Feature calculations
    features['URLLength'] = len(url)
    features['DomainLength'] = len(domain)
    features['IsDomainIP'] = int(bool(re.match(r'\d+\.\d+\.\d+\.\d+', domain)))

    features['CharContinuationRate'] = len(re.findall(r'(.)\1{2,}', url)) / len(url) if len(url) > 0 else 0

    tld = domain.split('.')[-1].lower() if '.' in domain else ''
    features['TLDLegitimateProb'] = TLD_PROBABILITY_MAP.get(tld, 0.5)

    char_counts = Counter(url)
    total_chars = sum(char_counts.values())
    char_probs = [count / total_chars for count in char_counts.values()]
    features['URLCharProb'] = np.mean(char_probs)

    features['TLDLength'] = len(tld)
    features['NoOfObfuscatedChar'] = url.count('//') + url.count('\\')
    features['HasObfuscation'] = int(features['NoOfObfuscatedChar'] > 0)
    features['ObfuscationRatio'] = features['NoOfObfuscatedChar'] / len(url) if len(url) > 0 else 0

    features['LetterRatioInURL'] = sum(c.isalpha() for c in url) / len(url) if len(url) > 0 else 0
    features['DegitRatioInURL'] = sum(c.isdigit() for c in url) / len(url) if len(url) > 0 else 0

    features['NoOfEqualsInURL'] = url.count('=')
    features['NoOfQMarkInURL'] = url.count('?')
    features['NoOfAmpersandInURL'] = url.count('&')

    special_chars = re.findall(r'[^A-Za-z0-9]', url)
    features['SpacialCharRatioInURL'] = len(special_chars) / len(url) if len(url) > 0 else 0

    features['IsHTTPS'] = int(parsed.scheme == 'https')

    lower_url = url.lower()
    features['Bank'] = int('bank' in lower_url)
    features['Pay'] = int('pay' in lower_url)
    features['Crypto'] = int('crypto' in lower_url)

    # Final feature order (20 features)
    ordered_features = [
        'URLLength', 'DomainLength', 'IsDomainIP', 'HasObfuscation', 'CharContinuationRate',
        'TLDLegitimateProb', 'NoOfObfuscatedChar', 'NoOfEqualsInURL', 'NoOfQMarkInURL', 'NoOfAmpersandInURL',
        'URLCharProb', 'DegitRatioInURL', 'Bank', 'Pay', 'Crypto',
        'SpacialCharRatioInURL', 'IsHTTPS', 'TLDLength', 'LetterRatioInURL', 'ObfuscationRatio'
    ]

    return [round(features[feature], 6) for feature in ordered_features]
