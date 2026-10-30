"""
Quick demonstration script for the Phishing URL Awareness Checker.
Run this file to test the checker on sample URLs.
"""
from phishing_checker import analyze_url, format_report

sample_urls = [
    "https://www.google.com",
    "http://login-google.com@evil-phish.net/account",
    "http://192.168.1.1/admin-login",
]

print("Running Phishing URL Awareness Checker test...")
print("=" * 60)

for url in sample_urls:
    print(f"\nAnalyzing: {url}")
    result = analyze_url(url)
    print(format_report(result, use_colors=False))
