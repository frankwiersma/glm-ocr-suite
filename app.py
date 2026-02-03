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

# Custom CSS
st.markdown("""
    <style>
    .main {
        padding: 2rem;
    }
    .stButton>button {
        background-color: #FF4B4B;
        color: white;
        border-radius: 5px;
        padding: 0.5rem 1rem;
        font-weight: 600;
    }
    .result-box {
        background-color: #f0f2f6;
        padding: 1.5rem;
        border-radius: 10px;
        margin-top: 1rem;
    }
    .sample-card {
        border: 2px solid #e0e0e0;
        border-radius: 10px;
        padding: 10px;
        margin-bottom: 15px;
        cursor: pointer;
        transition: all 0.3s;
    }
    .sample-card:hover {
        border-color: #FF4B4B;
        box-shadow: 0 4px 8px rgba(0,0,0,0.1);
    }
    </style>
""", unsafe_allow_html=True)

# Sample configurations - maps sample to optimal task type
SAMPLE_CONFIGS = {
    "1_text_recognition.png": {
        "name": "Text Recognition",
        "task": "Text Recognition",
        "prompt": "Text Recognition:",
        "description": "General text extraction"
    },
    "2_table_recognition.png": {
        "name": "Table Recognition",
        "task": "Table Recognition (HTML)",
        "prompt": "Table Recognition:",
        "description": "Extract as HTML table"
    },
    "3_invoice_receipt.png": {
        "name": "Invoice/Receipt",
        "task": "Invoice/Receipt (JSON)",
        "prompt": """Please extract the following information in JSON format:
{
  "invoice_number": "",
  "date": "",
  "bill_to": {
    "name": "",
    "address": ""
  },
  "items": [
    {
      "description": "",
      "quantity": "",
      "price": "",
      "total": ""
    }
  ],
  "subtotal": "",
  "tax": "",
  "tax_rate": "",
  "total": "",
  "payment_terms": "",
  "due_date": ""
}""",
        "description": "Structured JSON extraction"
    },
    "4_math_formulas.png": {
        "name": "Math Formulas",
        "task": "Math Formulas (LaTeX)",
        "prompt": "Extract all mathematical formulas in LaTeX format:",
        "description": "LaTeX notation"
    },
    "5_form_recognition.png": {
        "name": "Form Recognition",
        "task": "Form Fields (JSON)",
        "prompt": """Please extract all form fields in JSON format:
{
  "form_title": "",
  "fields": [
    {
      "field_name": "",
      "field_value": ""
    }
  ],
  "checkboxes": [
    {
      "option": "",
      "checked": false
    }
  ],
  "signature": "",
  "signature_date": ""
}""",
        "description": "Form data as JSON"
    },
    "6_handwriting_sample.png": {
        "name": "Handwriting",
        "task": "Handwriting Recognition",
        "prompt": "Handwriting Recognition:",
        "description": "Handwritten text extraction"
    },
    "7_document_understanding.png": {
        "name": "Document Understanding",
        "task": "Document Understanding",
        "prompt": "Please extract and summarize all key information from this document:",
        "description": "Comprehensive document analysis"
    }
}

def check_server_status():
    """Check if model server is running"""
    try:
        response = requests.get(f"{MODEL_SERVER_URL}/", timeout=2)
        return response.json()
    except:
        return None

def process_image_api(image, prompt):
    """Send image to model server for processing"""
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
    """Render output based on task type"""
    if "Table Recognition" in task_type:
        st.markdown("### 📊 Table Output")

        with st.expander("📝 View HTML Source"):
            st.code(output, language="html")

        st.markdown("### Rendered Table")
        try:
            st.markdown(output, unsafe_allow_html=True)
        except:
            st.warning("Could not render HTML")

    elif "(JSON)" in task_type:
        st.markdown("### 📋 Structured JSON Output")

        # Extract JSON from markdown code blocks
        json_match = re.search(r'```json\s*(.*?)\s*```', output, re.DOTALL)
        if json_match:
            json_str = json_match.group(1)
        else:
            json_match = re.search(r'\{.*\}', output, re.DOTALL)
            json_str = json_match.group(0) if json_match else output

        # Display formatted JSON
        st.code(json_str, language="json")

        # Parse and display as interactive tree
        try:
            parsed = json.loads(json_str)
            with st.expander("🌲 Interactive JSON Tree"):
                st.json(parsed)
        except:
            pass

    elif "LaTeX" in task_type or "Formula" in task_type:
        st.markdown("### 🔢 Math Formulas")

        # Show rendered LaTeX
        st.markdown("### 📐 Rendered Formulas")

        # Extract formulas (look for lines with math symbols)
        lines = output.split('\n')
        for line in lines:
            stripped = line.strip()
            # Skip empty lines and headers
            if not stripped or any(x in stripped.lower() for x in ['test:', 'formula', 'theorem', 'equation']):
                continue

            # If line contains math, try to render it
            if any(char in stripped for char in ['=', '^', '∫', '±', 'sqrt', 'frac']):
                try:
                    st.latex(stripped)
                except:
                    st.code(stripped, language="latex")

        # Show raw LaTeX code
        st.markdown("---")
        with st.expander("📝 View LaTeX Source Code"):
            st.code(output, language="latex")

    else:
        st.markdown("### 📄 Extracted Content")

        # Show as markdown
        with st.expander("📝 Markdown View"):
            st.markdown(output)

        # Show raw text
        st.code(output, language="text")

# Main UI
st.title("🔍 GLM-OCR Suite")
st.markdown("### High-Performance OCR with Auto-Detection")
st.markdown("---")

# Sidebar
with st.sidebar:
    st.header("⚙️ Status")

    # Server status
    server_status = check_server_status()

    if server_status and server_status.get('model_loaded'):
        st.success("✅ Model Server Online")
        st.info(f"🎮 GPU: {server_status.get('device', 'Unknown')}")
    else:
        st.error("❌ Server Offline")
        st.code("python glm_ocr_server.py", language="bash")

    st.markdown("---")

    # Manual task override
    st.header("🎯 Advanced Options")

    use_auto_detect = st.checkbox(
        "Auto-detect task type",
        value=True,
        help="Automatically select the best extraction method based on the sample"
    )

    manual_task = None
    if not use_auto_detect:
        manual_task = st.selectbox(
            "Manual task override:",
            [
                "Text Recognition",
                "Table Recognition (HTML)",
                "Invoice/Receipt (JSON)",
                "Form Fields (JSON)",
                "Math Formulas (LaTeX)",
                "Handwriting Recognition",
                "Document Understanding"
            ]
        )

    st.markdown("---")

    # Info
    with st.expander("ℹ️ About", expanded=True):
        st.markdown("""
        **GLM-OCR** - State-of-the-art OCR

        - 🏆 #1 on OmniDocBench V1.5 (94.62)
        - ⚡ 0.9B params, ~2.5GB VRAM
        - 🎯 Multiple specialized tasks
        - 🌍 **Multilingual**: Chinese, English, French, Spanish, Russian, German, Japanese, Korean, etc.
        - 📊 Output: HTML, JSON, LaTeX, Markdown
        - 🚀 Fast: 1.86 pages/s (PDF), 0.67 img/s
        - 💰 Cost: $0.03 per million tokens

        **Model:** zai-org/GLM-OCR (0.9B)
        **License:** MIT
        **Docs:** https://docs.z.ai
        """)

# Main content
col1, col2 = st.columns([1, 1])

with col1:
    st.header("📤 Input")

    # Image source selection
    upload_method = st.radio(
        "Choose source:",
        ["Sample Gallery", "Upload Image"],
        horizontal=True
    )

    uploaded_image = None
    selected_config = None

    if upload_method == "Upload Image":
        uploaded_file = st.file_uploader(
            "Upload an image",
            type=["png", "jpg", "jpeg", "bmp", "tiff"]
        )
        if uploaded_file:
            uploaded_image = Image.open(uploaded_file)

            # Auto-process on upload
            if server_status and server_status.get('model_loaded'):
                # Use default text recognition for uploaded images
                if 'last_uploaded' not in st.session_state or st.session_state.last_uploaded != uploaded_file.name:
                    st.session_state.last_uploaded = uploaded_file.name
                    st.session_state.trigger_process = True
                    st.session_state.process_prompt = "Text Recognition:"
                    st.session_state.process_task = "Text Recognition"

    else:  # Sample Gallery
        samples_dir = "samples"
        if os.path.exists(samples_dir):
            sample_files = sorted([f for f in os.listdir(samples_dir)
                          if f.lower().endswith(('.png', '.jpg', '.jpeg'))])

            if sample_files:
                st.markdown("#### 🖼️ Sample Gallery - Click to Process")

                # Display gallery
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
                                    "prompt": "Text Recognition:",
                                    "description": "Text extraction"
                                })

                                sample_path = os.path.join(samples_dir, sample_file)
                                img = Image.open(sample_path)
                                img.thumbnail((300, 300))

                                st.image(img, use_column_width=True)
                                st.markdown(f"**{config['name']}**")
                                st.caption(config['description'])

                                # One-click process button
                                if st.button(f"🚀 Process", key=f"btn_{idx}"):
                                    # Load image
                                    st.session_state.current_image = Image.open(sample_path)
                                    st.session_state.current_config = config
                                    # Trigger processing
                                    st.session_state.trigger_process = True
                                    st.rerun()

                # Show selected image if any
                if 'current_image' in st.session_state and 'current_config' in st.session_state:
                    uploaded_image = st.session_state.current_image
                    selected_config = st.session_state.current_config

                    st.markdown("---")
                    st.success(f"✓ Selected: {selected_config['name']}")
                    st.info(f"🎯 Task: {selected_config['task']}")

    # Display image
    if uploaded_image:
        st.markdown("### 🖼️ Input Image")
        st.image(uploaded_image, use_column_width=True)

        # Auto-process if triggered
        if server_status and server_status.get('model_loaded'):
            if st.session_state.get('trigger_process', False):
                # Get prompt
                if selected_config:
                    # Use auto-detected prompt unless manual override
                    if use_auto_detect or not manual_task:
                        prompt = selected_config['prompt']
                        task_name = selected_config['task']
                    else:
                        # Manual override - need to map to prompt
                        task_name = manual_task
                        # Get prompt from config (reuse logic)
                        prompt = "Text Recognition:"  # Default
                else:
                    prompt = st.session_state.get('process_prompt', "Text Recognition:")
                    task_name = st.session_state.get('process_task', "Text Recognition")

                # Clear trigger
                st.session_state.trigger_process = False

                # Process
                with col2:
                    st.header("📋 Results")
                    with st.spinner(f"Processing with {task_name}..."):
                        try:
                            result = process_image_api(uploaded_image, prompt)

                            if result.get('success'):
                                output = result['output']
                                render_result(output, task_name)

                                # Download button
                                file_ext = "json" if "(JSON)" in task_name else "html" if "Table" in task_name else "txt"
                                st.download_button(
                                    "💾 Download",
                                    output,
                                    file_name=f"result.{file_ext}",
                                    mime="application/json" if file_ext == "json" else "text/plain"
                                )
                            else:
                                st.error(f"❌ Error: {result.get('error')}")

                        except Exception as e:
                            st.error(f"❌ Error: {str(e)}")
        else:
            st.warning("⚠️ Start model server first: `python glm_ocr_server.py`")

with col2:
    if 'current_image' not in st.session_state:
        st.header("📋 Results")
        st.info("👈 Select a sample to see results")

        st.markdown("### 🎯 Available Tasks")

        tasks = {
            "📄 Text Recognition": "Extract all text content",
            "📊 Table → HTML": "Tables as structured HTML",
            "🧾 Invoice → JSON": "Invoices with structured fields",
            "📋 Forms → JSON": "Form fields and values",
            "🔢 Math → LaTeX": "Formulas in LaTeX notation",
            "✍️ Handwriting": "Handwritten text recognition",
            "📚 Documents": "Comprehensive understanding"
        }

        for task, desc in tasks.items():
            st.markdown(f"**{task}**: {desc}")

# Footer
st.markdown("---")
st.markdown("""
<div style='text-align: center; color: #666;'>
    <p>Powered by GLM-OCR (zai-org) | Auto-Task Detection | GPU Accelerated</p>
</div>
""", unsafe_allow_html=True)
