"""
PDF processing module for GLM-OCR
Converts PDF pages to images and processes them
"""

import sys
import io

# Fix Windows console encoding
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

from PIL import Image
import requests

def convert_pdf_to_images(pdf_path, dpi=200):
    """
    Convert PDF pages to images using pdf2image
    Returns list of PIL Images
    """
    try:
        from pdf2image import convert_from_path
        images = convert_from_path(pdf_path, dpi=dpi)
        return images
    except ImportError:
        print("⚠️ pdf2image not installed. Installing...")
        import subprocess
        subprocess.check_call([sys.executable, "-m", "pip", "install", "pdf2image"])
        from pdf2image import convert_from_path
        images = convert_from_path(pdf_path, dpi=dpi)
        return images

def process_pdf_page(image, prompt, server_url="http://localhost:8508"):
    """Process a single PDF page (as image) with GLM-OCR"""
    img_byte_arr = io.BytesIO()
    image.save(img_byte_arr, format='PNG')
    img_byte_arr.seek(0)

    files = {'image': ('page.png', img_byte_arr, 'image/png')}
    data = {'prompt': prompt}

    response = requests.post(
        f"{server_url}/predict",
        files=files,
        data=data,
        timeout=120
    )

    return response.json()

def process_pdf(pdf_path, prompt="Text Recognition:", max_pages=None):
    """
    Process entire PDF with GLM-OCR

    Args:
        pdf_path: Path to PDF file
        prompt: OCR task prompt
        max_pages: Maximum pages to process (None = all)

    Returns:
        List of results, one per page
    """
    print(f"\n{'='*80}")
    print(f"Processing PDF: {pdf_path}")
    print(f"Prompt: {prompt}")
    print(f"{'='*80}\n")

    # Convert PDF to images
    print("📄 Converting PDF to images...")
    images = convert_pdf_to_images(pdf_path)
    total_pages = len(images)
    print(f"✓ Converted {total_pages} pages")

    # Limit pages if specified
    if max_pages:
        images = images[:max_pages]
        print(f"Processing first {max_pages} pages")

    # Process each page
    results = []
    for i, image in enumerate(images, 1):
        print(f"\nProcessing page {i}/{len(images)}...")

        try:
            result = process_pdf_page(image, prompt)

            if result.get('success'):
                output = result['output']
                print(f"✓ Page {i} processed ({len(output)} chars)")
                results.append({
                    'page': i,
                    'success': True,
                    'output': output
                })
            else:
                print(f"✗ Page {i} failed: {result.get('error')}")
                results.append({
                    'page': i,
                    'success': False,
                    'error': result.get('error')
                })

        except Exception as e:
            print(f"✗ Page {i} exception: {str(e)}")
            results.append({
                'page': i,
                'success': False,
                'error': str(e)
            })

    # Summary
    successful = sum(1 for r in results if r.get('success'))
    print(f"\n{'='*80}")
    print(f"PDF Processing Complete")
    print(f"{'='*80}")
    print(f"Total pages: {len(results)}")
    print(f"Successful: {successful}/{len(results)}")
    print(f"{'='*80}\n")

    return results

if __name__ == "__main__":
    # Example usage
    if len(sys.argv) < 2:
        print("Usage: python pdf_processor.py <pdf_file> [prompt] [max_pages]")
        print("\nExample:")
        print('  python pdf_processor.py document.pdf "Text Recognition:" 5')
        sys.exit(1)

    pdf_file = sys.argv[1]
    prompt = sys.argv[2] if len(sys.argv) > 2 else "Text Recognition:"
    max_pages = int(sys.argv[3]) if len(sys.argv) > 3 else None

    results = process_pdf(pdf_file, prompt, max_pages)

    # Save results
    output_file = pdf_file.replace('.pdf', '_ocr_results.txt')
    with open(output_file, 'w', encoding='utf-8') as f:
        for result in results:
            f.write(f"\n{'='*80}\n")
            f.write(f"PAGE {result['page']}\n")
            f.write(f"{'='*80}\n")
            if result.get('success'):
                f.write(result['output'])
            else:
                f.write(f"ERROR: {result.get('error')}\n")
            f.write(f"\n")

    print(f"Results saved to: {output_file}")
