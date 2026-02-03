import streamlit as st
from PIL import Image
import os
import requests
import io
import re
import json

# Page config
st.set_page_config(
    page_title="GLM-OCR Suite",
    page_icon="🔍",
    layout="wide"
)

# Server configuration
MODEL_SERVER_URL = "http://localhost:8508"

# PDF support using PyMuPDF (no poppler needed!)
try:
    import fitz  # PyMuPDF
    PDF_SUPPORT = True
except ImportError:
    PDF_SUPPORT = False

def convert_pdf_to_images(pdf_path, dpi=150):
    """Convert PDF to images using PyMuPDF"""
    doc = fitz.open(pdf_path)
    images = []
    for page_num in range(len(doc)):
        page = doc[page_num]
        mat = fitz.Matrix(dpi/72, dpi/72)
        pix = page.get_pixmap(matrix=mat)
        img_data = pix.tobytes("png")
        img = Image.open(io.BytesIO(img_data))
        images.append(img)
    doc.close()
    return images

# Custom CSS (same as before)
st.markdown("""
    <style>
    .main { padding: 2rem; }
    .stButton>button {
        background-color: #FF4B4B;
        color: white;
        border-radius: 5px;
        padding: 0.5rem 1rem;
        font-weight: 600;
    }
    </style>
""", unsafe_allow_html=True)

# Sample configurations
SAMPLE_CONFIGS = {
    "1_text_recognition.png": {
        "name": "Text Recognition",
        "task": "Text Recognition",
        "prompt": "Text Recognition:",
    },
    "2_table_recognition.png": {
        "name": "Table Recognition",
        "task": "Table Recognition (HTML)",
        "prompt": "Table Recognition:",
    },
    "3_invoice_receipt.png": {
        "name": "Invoice/Receipt",
        "task": "Invoice/Receipt (JSON)",
        "prompt": """Please extract in JSON format:
{
  "invoice_number": "",
  "date": "",
  "bill_to": {"name": "", "address": ""},
  "items": [{"description": "", "quantity": "", "price": "", "total": ""}],
  "subtotal": "", "tax": "", "total": ""
}""",
    },
    "4_math_formulas.png": {
        "name": "Math Formulas",
        "task": "Math Formulas (LaTeX)",
        "prompt": "Extract all mathematical formulas in LaTeX format:",
    },
    "5_form_recognition.png": {
        "name": "Form Recognition",
        "task": "Form Fields (JSON)",
        "prompt": """Extract form fields in JSON:
{
  "form_title": "",
  "fields": [{"field_name": "", "field_value": ""}],
  "checkboxes": [{"option": "", "checked": false}]
}""",
    },
    "6_handwriting_sample.png": {
        "name": "Handwriting",
        "task": "Handwriting Recognition",
        "prompt": "Handwriting Recognition:",
    },
    "7_document_understanding.png": {
        "name": "Document Understanding",
        "task": "Document Understanding",
        "prompt": "Please extract and summarize all key information:",
    }
}

def check_server_status():
    try:
        response = requests.get(f"{MODEL_SERVER_URL}/", timeout=2)
        return response.json()
    except:
        return None

def process_image_api(image, prompt):
    img_byte_arr = io.BytesIO()
    image.save(img_byte_arr, format='PNG')
    img_byte_arr.seek(0)

    files = {'image': ('image.png', img_byte_arr, 'image/png')}
    data = {'prompt': prompt}

    response = requests.post(
        f"{MODEL_SERVER_URL}/predict",
        files=files,
        data=data,
        timeout=120
    )

    return response.json()

def render_result(output, task_type):
    if "Table Recognition" in task_type:
        st.markdown("### 📊 Table Output")
        with st.expander("📝 HTML Source"):
            st.code(output, language="html")
        st.markdown("### Rendered Table")
        try:
            st.markdown(output, unsafe_allow_html=True)
        except:
            st.warning("Could not render HTML")

    elif "(JSON)" in task_type:
        st.markdown("### 📋 JSON Output")
        json_match = re.search(r'```json\s*(.*?)\s*```', output, re.DOTALL)
        if json_match:
            json_str = json_match.group(1)
        else:
            json_match = re.search(r'\{.*\}', output, re.DOTALL)
            json_str = json_match.group(0) if json_match else output

        st.code(json_str, language="json")

        try:
            parsed = json.loads(json_str)
            with st.expander("🌲 JSON Tree"):
                st.json(parsed)
        except:
            pass

    elif "LaTeX" in task_type or "Formula" in task_type:
        st.markdown("### 🔢 Math Formulas")
        st.markdown("### 📐 Rendered")
        lines = output.split('\n')
        for line in lines:
            stripped = line.strip()
            if stripped and any(char in stripped for char in ['=', '^', '∫', '±', 'sqrt', 'frac']):
                try:
                    st.latex(stripped)
                except:
                    st.code(stripped)

        with st.expander("📝 LaTeX Source"):
            st.code(output, language="latex")

    else:
        st.markdown("### 📄 Output")
        with st.expander("📝 Markdown"):
            st.markdown(output)
        st.code(output, language="text")

# Main UI
st.title("🔍 GLM-OCR Suite")
st.markdown("### Demo & Testing App")
st.markdown("---")

# Sidebar
with st.sidebar:
    st.header("⚙️ Status")

    server_status = check_server_status()

    if server_status and server_status.get('model_loaded'):
        st.success("✅ Server Online")
        st.info(f"🎮 GPU: {server_status.get('device')}")
    else:
        st.error("❌ Server Offline")
        st.code("python server.py")

    st.markdown("---")

    with st.expander("ℹ️ About", expanded=True):
        st.markdown("""
        **GLM-OCR** by Zhipu AI

        Released: **February 3, 2026** 🆕

        - 🏆 #1 OmniDocBench (94.62)
        - ⚡ 0.9B params, ~2.5GB VRAM
        - 🌍 Multilingual: CN, EN, FR, ES, RU, DE, JP, KR...
        - 📊 Output: HTML, JSON, LaTeX, MD
        - 📄 PDF: Up to 100 pages, 50MB
        - 🚀 Speed: 1.86 pages/s

        [HuggingFace](https://huggingface.co/zai-org/GLM-OCR) | [Docs](https://docs.z.ai)
        """)

# Main content
col1, col2 = st.columns([1, 1])

with col1:
    st.header("📤 Input")

    input_type = st.radio(
        "Choose input type:",
        ["Sample Gallery", "Upload Image", "Upload PDF"],
        horizontal=True
    )

    uploaded_image = None
    selected_config = None
    pdf_mode = False

    if input_type == "Upload Image":
        uploaded_file = st.file_uploader(
            "Upload an image",
            type=["png", "jpg", "jpeg", "bmp", "tiff"]
        )
        if uploaded_file:
            uploaded_image = Image.open(uploaded_file)

    elif input_type == "Upload PDF":
        if not PDF_SUPPORT:
            st.warning("⚠️ PDF support requires PyMuPDF")
            st.code("pip install PyMuPDF")
            st.info("PyMuPDF works out-of-the-box on Windows (no poppler needed!)")
        else:
            # Sample or upload option
            pdf_option = st.radio(
                "Choose PDF:",
                ["Sample PDF (3 pages)", "Upload Your PDF"],
                horizontal=True
            )

            temp_pdf = None

            if pdf_option == "Sample PDF (3 pages)":
                sample_pdf = "samples/sample_document.pdf"
                if os.path.exists(sample_pdf):
                    temp_pdf = sample_pdf
                    st.success("✓ Using sample: Text, Tables, Formulas")
                else:
                    st.error("Sample PDF not found")
            else:
                pdf_file = st.file_uploader(
                    "Upload PDF (max 50MB, 100 pages)",
                    type=["pdf"]
                )
                if pdf_file:
                    temp_pdf = "temp_upload.pdf"
                    with open(temp_pdf, 'wb') as f:
                        f.write(pdf_file.read())

            if temp_pdf:
                pdf_mode = True

                # Convert PDF to images
                try:
                    images = convert_pdf_to_images(temp_pdf, dpi=150)
                    st.success(f"✓ PDF loaded: {len(images)} pages")

                    max_pages = st.slider("Pages to process:", 1, min(len(images), 100), min(5, len(images)))

                    # Show first page preview
                    st.markdown("### Preview (Page 1)")
                    st.image(images[0], use_column_width=True)

                    # Select task
                    task_type = st.selectbox("Task:", [
                        "Text Recognition",
                        "Table Recognition (HTML)",
                        "Document Understanding"
                    ])

                    if st.button("🚀 Process PDF"):
                        with col2:
                            st.header("📋 Results")
                            progress = st.progress(0)

                            for i, img in enumerate(images[:max_pages]):
                                progress.progress((i + 1) / max_pages)
                                st.markdown(f"### 📄 Page {i+1}/{max_pages}")

                                # Get prompt
                                prompts = {
                                    "Text Recognition": "Text Recognition:",
                                    "Table Recognition (HTML)": "Table Recognition:",
                                    "Document Understanding": "Extract all key information:"
                                }
                                prompt = prompts.get(task_type, "Text Recognition:")

                                result = process_image_api(img, prompt)
                                if result.get('success'):
                                    # Simple display without nested expanders
                                    output = result['output']
                                    if "Table" in task_type:
                                        st.markdown(output, unsafe_allow_html=True)
                                    else:
                                        st.code(output, language="text")
                                    st.markdown("---")

                except Exception as e:
                    st.error(f"Error processing PDF: {str(e)}")

    else:  # Sample Gallery
        samples_dir = "samples"
        if os.path.exists(samples_dir):
            sample_files = sorted([f for f in os.listdir(samples_dir)
                          if f.lower().endswith(('.png', '.jpg', '.jpeg'))])

            if sample_files:
                st.markdown("#### 🖼️ Gallery - Click to Process")

                cols_per_row = 2
                for i in range(0, len(sample_files), cols_per_row):
                    cols = st.columns(cols_per_row)
                    for j, col in enumerate(cols):
                        idx = i + j
                        if idx < len(sample_files):
                            with col:
                                sample_file = sample_files[idx]
                                config = SAMPLE_CONFIGS.get(sample_file, {
                                    "name": sample_file,
                                    "task": "Text Recognition",
                                    "prompt": "Text Recognition:"
                                })

                                sample_path = os.path.join(samples_dir, sample_file)
                                img = Image.open(sample_path)
                                img.thumbnail((300, 300))

                                st.image(img, use_column_width=True)
                                st.markdown(f"**{config['name']}**")

                                if st.button(f"🚀 Process", key=f"btn_{idx}"):
                                    st.session_state.current_image = Image.open(sample_path)
                                    st.session_state.current_config = config
                                    st.session_state.trigger_process = True
                                    st.rerun()

                if 'current_image' in st.session_state and 'current_config' in st.session_state:
                    uploaded_image = st.session_state.current_image
                    selected_config = st.session_state.current_config

                    st.markdown("---")
                    st.success(f"✓ Selected: {selected_config['name']}")
                    st.info(f"🎯 Task: {selected_config['task']}")

    # Display and process
    if uploaded_image and not pdf_mode:
        st.markdown("### 🖼️ Input Image")
        st.image(uploaded_image, use_column_width=True)

        if server_status and server_status.get('model_loaded'):
            if st.session_state.get('trigger_process', False):
                st.session_state.trigger_process = False

                prompt = selected_config['prompt'] if selected_config else "Text Recognition:"
                task_name = selected_config['task'] if selected_config else "Text Recognition"

                with col2:
                    st.header("📋 Results")
                    with st.spinner(f"Processing..."):
                        try:
                            result = process_image_api(uploaded_image, prompt)

                            if result.get('success'):
                                render_result(result['output'], task_name)

                                file_ext = "json" if "(JSON)" in task_name else "html" if "Table" in task_name else "txt"
                                st.download_button(
                                    "💾 Download",
                                    result['output'],
                                    file_name=f"result.{file_ext}"
                                )
                            else:
                                st.error(f"Error: {result.get('error')}")

                        except Exception as e:
                            st.error(f"Error: {str(e)}")

with col2:
    if 'current_image' not in st.session_state and not pdf_mode:
        st.header("📋 Results")
        st.info("👈 Select a sample to process")

        st.markdown("### 🎯 Capabilities")
        st.markdown("""
        - 📄 **Text**: General extraction
        - 📊 **Tables**: HTML structure
        - 🧾 **Invoices**: JSON with items/totals
        - 📋 **Forms**: JSON fields/checkboxes
        - 🔢 **Math**: LaTeX formulas
        - ✍️ **Handwriting**: Sticky notes, letters
        - 📚 **Documents**: Comprehensive analysis
        - 📄 **PDF**: Multi-page processing
        """)

st.markdown("---")
st.markdown("""
<div style='text-align: center; color: #666;'>
    <p>Powered by <a href="https://huggingface.co/zai-org/GLM-OCR">GLM-OCR</a> | GPU Accelerated</p>
</div>
""", unsafe_allow_html=True)
