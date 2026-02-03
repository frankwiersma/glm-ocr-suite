"""
Quick demo of GLM-OCR capabilities
Run this after starting the model server to see all capabilities in action
"""

import sys
import io

# Fix Windows console encoding
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

import requests
import os
from datetime import datetime

SERVER_URL = "http://localhost:8508"
SAMPLES_DIR = "samples"

TESTS = [
    ("1_text_recognition.png", "Text Recognition:", "📄 Text"),
    ("2_table_recognition.png", "Table Recognition:", "📊 Table → HTML"),
    ("3_invoice_receipt.png", "Please extract in JSON format:\n{\"invoice_number\": \"\", \"date\": \"\", \"items\": [], \"total\": \"\"}", "🧾 Invoice → JSON"),
    ("4_math_formulas.png", "Extract formulas in LaTeX:", "🔢 Math → LaTeX"),
    ("5_form_recognition.png", "Extract form fields in JSON format:", "📋 Form → JSON"),
    ("6_handwriting_sample.png", "Handwriting Recognition:", "✍️ Handwriting"),
    ("7_document_understanding.png", "Extract and summarize:", "📚 Document Analysis"),
]

def test_sample(filename, prompt, name):
    print(f"\n{name}")
    print("-" * 60)

    try:
        filepath = os.path.join(SAMPLES_DIR, filename)
        with open(filepath, 'rb') as f:
            files = {'image': ('image.png', f, 'image/png')}
            data = {'prompt': prompt}

            start = datetime.now()
            response = requests.post(f"{SERVER_URL}/predict", files=files, data=data, timeout=60)
            elapsed = (datetime.now() - start).total_seconds()

            result = response.json()
            if result.get('success'):
                output = result['output'][:200]  # First 200 chars
                print(f"✓ Success ({elapsed:.2f}s)")
                print(output + "...")
                return True
            else:
                print(f"✗ Failed: {result.get('error')}")
                return False
    except Exception as e:
        print(f"✗ Error: {str(e)}")
        return False

def main():
    print("\n" + "="*60)
    print("🔍 GLM-OCR DEMO - All Capabilities")
    print("="*60)

    # Check server
    try:
        status = requests.get(f"{SERVER_URL}/", timeout=2).json()
        print(f"\n✓ Server: {status.get('device')}")
    except:
        print("\n❌ Server offline! Start with: python server.py")
        return

    # Run tests
    results = []
    for filename, prompt, name in TESTS:
        results.append(test_sample(filename, prompt, name))

    # Summary
    print("\n" + "="*60)
    print(f"Results: {sum(results)}/{len(results)} successful")
    print("="*60)
    print("\n🌐 Try the app: http://localhost:8507")
    print("📁 Repository: https://github.com/frankwiersma/glm-ocr-suite\n")

if __name__ == "__main__":
    main()
