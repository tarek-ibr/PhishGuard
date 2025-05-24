from urllib.parse import urlparse
import re
from collections import Counter
import numpy as np
import pandas as pd

# Static lookup for TLD legitimacy probability
TLD_PROBABILITY_MAP = {
    'com': 0.95, 'org': 0.0799628, 'net': 0.90, 'gov': 0.98, 'edu': 0.97,
    'io': 0.85, 'co': 0.85, 'us': 0.80, 'biz': 0.75, 'info': 0.70,
    'xyz': 0.40, 'top': 0.30, 'tk': 0.20, 'ml': 0.20, 'gq': 0.10, 'cf': 0.10
}


def extract_all_features_df(url):
    parsed = urlparse(url)
    domain = parsed.netloc
    path = parsed.path
    url_for_stats = domain + path

    features = {}

    # Feature calculations
    clean_url = url.rstrip('/')
    features['URLLength'] = len(clean_url) - 1
    features['DomainLength'] = len(domain)
    features['IsDomainIP'] = int(bool(re.match(r'^\d+\.\d+\.\d+\.\d+$', domain)))

    features['CharContinuationRate'] = len(re.findall(r'(.)\1{2,}', url_for_stats))

    # TLD
    tld = domain.split('.')[-1].lower() if '.' in domain else ''
    features['TLDLegitimateProb'] = TLD_PROBABILITY_MAP.get(tld, 0.5)

    # URLCharProb -> 1 / char_count
    if len(url_for_stats) > 0:
        unique_chars = len(list(url_for_stats))
        features['URLCharProb'] = 1.0 / unique_chars if unique_chars > 0 else 0.0
    else:
        features['URLCharProb'] = 0.0

    features['TLDLength'] = len(tld)

    # build the regex just as you did
    OBF_PATTERNS = [
        r'\\',  # back-slash
        r'%[0-9a-fA-F]{2}',  # %xx URL-encoded byte
        r'&#x[0-9a-fA-F]+;',  # &#xHH;
        r'&#\d+;',  # &#NNN;
        r'0x[0-9a-fA-F]{2,}',  # 0xHH…
        r'xn--[A-Za-z0-9\-]{2,}',  # punycode
        r'@',  # user-info trick
        r'\b\d{1,3}(?:\.\d{1,3}){3}\b',  # dotted-decimal IP
        r'\b0[0-7]+\b',  # octal IP
        r'\b\d{8,10}\b',  # dword IP
    ]
    OBF_REGEX = re.compile('|'.join(OBF_PATTERNS), flags=re.IGNORECASE)

    # ── Scalar (per-URL) calculations – no “.str” accessors needed ────────────────────
    no_of_obf = len(OBF_REGEX.findall(url_for_stats))
    features['NoOfObfuscatedChar'] = no_of_obf
    features['HasObfuscation'] = int(no_of_obf > 0)
    features['ObfuscationRatio'] = no_of_obf / len(url_for_stats) if url_for_stats else 0

    features['LetterRatioInURL'] = sum(c.isalpha() for c in url_for_stats) / len(url_for_stats) if len(
        url_for_stats) > 0 else 0
    features['DegitRatioInURL'] = sum(c.isdigit() for c in url_for_stats) / len(url_for_stats) if len(
        url_for_stats) > 0 else 0

    features['NoOfEqualsInURL'] = url.count('=')
    features['NoOfQMarkInURL'] = url.count('?')
    features['NoOfAmpersandInURL'] = url.count('&')

    # SpacialCharRatioInURL - calculate actual special character ratio
    special_chars = re.findall(r'[^A-Za-z0-9]', url_for_stats)
    features['SpacialCharRatioInURL'] = len(special_chars) / len(url_for_stats) if len(url_for_stats) > 0 else 0

    features['IsHTTPS'] = int(parsed.scheme == 'https')

    lower_url = url.lower()
    features['Bank'] = int('bank' in lower_url)
    features['Pay'] = int('pay' in lower_url)
    features['Crypto'] = int('crypto' in lower_url)

    ordered_features = [
        'URLLength', 'DomainLength', 'IsDomainIP', 'CharContinuationRate',
        'TLDLegitimateProb', 'URLCharProb', 'TLDLength', 'HasObfuscation',
        'NoOfObfuscatedChar', 'ObfuscationRatio', 'LetterRatioInURL',
        'DegitRatioInURL', 'NoOfEqualsInURL', 'NoOfQMarkInURL',
        'NoOfAmpersandInURL', 'SpacialCharRatioInURL', 'IsHTTPS',
        'Bank', 'Pay', 'Crypto'
    ]

    return pd.DataFrame([[round(features[feature], 6) for feature in ordered_features]],
                        columns=ordered_features)


