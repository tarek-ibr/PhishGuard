import pandas as pd
import requests
from urllib.parse import urlparse, urljoin
from bs4 import BeautifulSoup
import re
from collections import Counter
import numpy as np

def extract_all_features_df(url):
    parsed = urlparse(url)
    domain = parsed.netloc
    features = {}

    # Total number of characters in the URL.
    features['URLLength'] = len(url)

    # The domain part of the URL.
    features['Domain'] = domain

    # Length of the domain name.
    features['DomainLength'] = len(domain)

    # Indicates if the domain is an IP address.
    features['IsDomainIP'] = int(bool(re.match(r'\d+\.\d+\.\d+\.\d+', domain)))

    # Top-level domain, e.g., com, org.
    features['TLD'] = domain.split('.')[-1] if '.' in domain else ''

    # Length of the top-level domain.
    features['TLDLength'] = len(features['TLD'])

    # Number of subdomains in the domain.
    features['NoOfSubDomain'] = domain.count('.') - 1

    # Rate of consecutive repeated characters in the URL.
    features['CharContinuationRate'] = len(re.findall(r'(.)\1{2,}', url)) / len(url) if len(url) > 0 else 0

    # Estimated legitimacy of the TLD (placeholder).
    features['TLDLegitimateProb'] = 0.5

    # Average character frequency in the URL.
    char_counts = Counter(url)
    total_chars = sum(char_counts.values())
    char_probs = [count / total_chars for count in char_counts.values()]
    features['URLCharProb'] = np.mean(char_probs)

    # Checks if obfuscation (e.g., // or \\) is used.
    features['HasObfuscation'] = int('//' in url or '\\' in url)

    # Count of obfuscation characters in URL.
    features['NoOfObfuscatedChar'] = url.count('//') + url.count('\\')

    # Ratio of obfuscation characters to URL length.
    features['ObfuscationRatio'] = features['NoOfObfuscatedChar'] / len(url) if len(url) > 0 else 0

    # Count of alphabetic characters in the URL.
    features['NoOfLettersInURL'] = sum(c.isalpha() for c in url)

    # Ratio of alphabetic characters to total URL length.
    features['LetterRatioInURL'] = features['NoOfLettersInURL'] / len(url) if len(url) > 0 else 0

    # Count of numeric characters in the URL.
    features['NoOfDegitsInURL'] = sum(c.isdigit() for c in url)

    # Ratio of digits to total URL length.
    features['DegitRatioInURL'] = features['NoOfDegitsInURL'] / len(url) if len(url) > 0 else 0

    # Number of "=" characters in the URL.
    features['NoOfEqualsInURL'] = url.count('=')

    # Number of "?" characters in the URL.
    features['NoOfQMarkInURL'] = url.count('?')

    # Number of "&" characters in the URL.
    features['NoOfAmpersandInURL'] = url.count('&')

    # Count of other special characters not including =, ?, &.
    special_chars = re.findall(r'[^A-Za-z0-9]', url)
    features['NoOfOtherSpecialCharsInURL'] = len(special_chars) - (
        features['NoOfEqualsInURL'] + features['NoOfQMarkInURL'] + features['NoOfAmpersandInURL']
    )

    # Ratio of special characters to total URL length.
    features['SpacialCharRatioInURL'] = len(special_chars) / len(url) if len(url) > 0 else 0

    # Indicates if the URL uses HTTPS protocol.
    features['IsHTTPS'] = int(parsed.scheme == 'https')

    # Attempt to extract HTML-based features
    try:
        response = requests.get(url, timeout=5)
        soup = BeautifulSoup(response.text, 'html.parser')

        # Number of lines in the HTML response.
        features['LineOfCode'] = len(response.text.split('\n'))

        # Length of the longest line in the HTML response.
        features['LargestLineLength'] = max((len(line) for line in response.text.split('\n')), default=0)

        # Indicates if the HTML contains a <title> tag.
        title_tag = soup.title.string.strip() if soup.title and soup.title.string else ''
        features['HasTitle'] = int(bool(title_tag))

        # The actual title text from the HTML.
        features['Title'] = title_tag

        # Checks if domain is found in the page title.
        features['DomainTitleMatchScore'] = int(domain.lower() in title_tag.lower()) if title_tag else 0

        # Checks if page title is found in the URL.
        features['URLTitleMatchScore'] = int(title_tag.lower() in url.lower()) if title_tag else 0

        # Indicates presence of a favicon link tag.
        features['HasFavicon'] = int(bool(soup.find('link', rel='icon')))

        # Presence of a robots meta tag.
        features['Robots'] = int(bool(soup.find('meta', attrs={'name': 'robots'})))

        # Presence of a viewport meta tag (responsiveness).
        features['IsResponsive'] = int(bool(soup.find('meta', attrs={'name': 'viewport'})))

        # Number of meta refresh redirect tags.
        features['NoOfURLRedirect'] = len(soup.find_all('meta', attrs={'http-equiv': 'refresh'}))

        # Number of links that point back to the same domain.
        features['NoOfSelfRedirect'] = sum(1 for tag in soup.find_all('a', href=True) if domain in tag['href'])

        # Presence of a description meta tag.
        features['HasDescription'] = int(bool(soup.find('meta', attrs={'name': 'description'})))

        # Count of "popup" mentions in the HTML.
        features['NoOfPopup'] = response.text.lower().count('popup')

        # Number of iframe tags.
        features['NoOfiFrame'] = len(soup.find_all('iframe'))

        # Form submissions to external domains.
        features['HasExternalFormSubmit'] = int(any(domain not in form.get('action', '') for form in soup.find_all('form') if form.get('action')))

        # Presence of common social network links.
        features['HasSocialNet'] = int(any(net in response.text.lower() for net in ['facebook', 'twitter', 'linkedin']))

        # Presence of submit input fields.
        features['HasSubmitButton'] = int(bool(soup.find('input', {'type': 'submit'})))

        # Presence of hidden input fields.
        features['HasHiddenFields'] = int(bool(soup.find('input', {'type': 'hidden'})))

        # Presence of password input fields.
        features['HasPasswordField'] = int(bool(soup.find('input', {'type': 'password'})))

        # Mentions of the word "bank".
        features['Bank'] = int('bank' in response.text.lower())

        # Mentions of the word "pay".
        features['Pay'] = int('pay' in response.text.lower())

        # Mentions of the word "crypto".
        features['Crypto'] = int('crypto' in response.text.lower())

        # Mentions of copyright or ©.
        features['HasCopyrightInfo'] = int('©' in response.text or 'copyright' in response.text.lower())

        # Count of image tags.
        features['NoOfImage'] = len(soup.find_all('img'))

        # Count of CSS styles and linked stylesheets.
        features['NoOfCSS'] = len(soup.find_all('link', rel='stylesheet')) + len(soup.find_all('style'))

        # Count of JavaScript script tags.
        features['NoOfJS'] = len(soup.find_all('script'))

        # Count of resources referring to the same domain, empty, or external.
        resources = soup.find_all(['a', 'script', 'img', 'link'])
        features['NoOfSelfRef'] = 0
        features['NoOfEmptyRef'] = 0
        features['NoOfExternalRef'] = 0
        for tag in resources:
            src = tag.get('href') or tag.get('src')
            if not src:
                features['NoOfEmptyRef'] += 1
                continue
            src_domain = urlparse(urljoin(url, src)).netloc
            if src_domain == '':
                features['NoOfEmptyRef'] += 1
            elif src_domain == domain:
                features['NoOfSelfRef'] += 1
            else:
                features['NoOfExternalRef'] += 1

    except Exception as e:
        # Fill in default values if an error occurs
        html_keys = [
            'LineOfCode', 'LargestLineLength', 'HasTitle', 'Title', 'DomainTitleMatchScore', 'URLTitleMatchScore',
            'HasFavicon', 'Robots', 'IsResponsive', 'NoOfURLRedirect', 'NoOfSelfRedirect', 'HasDescription',
            'NoOfPopup', 'NoOfiFrame', 'HasExternalFormSubmit', 'HasSocialNet', 'HasSubmitButton',
            'HasHiddenFields', 'HasPasswordField', 'Bank', 'Pay', 'Crypto', 'HasCopyrightInfo',
            'NoOfImage', 'NoOfCSS', 'NoOfJS', 'NoOfSelfRef', 'NoOfEmptyRef', 'NoOfExternalRef'
        ]
        for key in html_keys:
            features[key] = 0 if key != 'Title' else ""

    return pd.DataFrame([features])

