# 🔍 GLM-OCR Suite

A comprehensive Streamlit application showcasing the powerful capabilities of [GLM-OCR](https://huggingface.co/zai-org/GLM-OCR), the state-of-the-art multilingual OCR model.

[![HuggingFace](https://img.shields.io/badge/🤗-HuggingFace-yellow)](https://huggingface.co/zai-org/GLM-OCR)
[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](https://opensource.org/licenses/MIT)
[![Streamlit](https://img.shields.io/badge/Streamlit-FF4B4B?logo=streamlit&logoColor=white)](https://streamlit.io)

## ✨ Features

- 🏆 **State-of-the-Art**: #1 on OmniDocBench V1.5 (94.62 score)
- 🌍 **Multilingual**: Chinese, English, French, Spanish, Russian, German, Japanese, Korean, and more
- ⚡ **Fast & Efficient**: 0.9B parameters, ~2.5GB VRAM, GPU accelerated
- 🎯 **8+ Specialized Tasks**: Text, tables, formulas, invoices, forms, handwriting, documents
- 📊 **Smart Rendering**: HTML tables, JSON trees, LaTeX formulas, Markdown
- 🚀 **Auto-Detection**: Automatically selects optimal extraction method
- 💾 **Persistent Model**: Stays loaded in memory for instant processing

## 🎯 Supported OCR Tasks

| Task | Output Format | Use Case |
|------|---------------|----------|
| 📄 Text Recognition | Plain Text | General text extraction |
| 📊 Table Recognition | HTML | Structured table data |
| 🧾 Invoice/Receipt | JSON | Billing information |
| 🔢 Math Formulas | LaTeX | Mathematical equations |
| 📋 Form Fields | JSON | Form data extraction |
| ✍️ Handwriting | Text | Handwritten notes |
| 📚 Document Understanding | Markdown | Comprehensive analysis |
| 🎯 Custom Extraction | User-defined | Flexible prompting |

## 🚀 Quick Start

### Prerequisites

```bash
pip install streamlit transformers torch pillow fastapi uvicorn requests
pip install --upgrade git+https://github.com/huggingface/transformers.git
```

### Installation

```bash
git clone https://github.com/YOUR_USERNAME/glm-ocr-suite.git
cd glm-ocr-suite
```

### Run the Application

**Option 1: Two-Process Setup (Recommended for production)**

```bash
# Terminal 1: Start model server
python server.py

# Terminal 2: Start Streamlit app (after model loads)
streamlit run app.py --server.port 8507
```

**Option 2: All-in-One (Simpler for testing)**

```bash
# Start both services
python server.py &
streamlit run app.py --server.port 8507
```

### Access the App

Open your browser to: **http://localhost:8507**

## 📖 Usage

1. **Select a Sample**: Click any sample image from the gallery
2. **Auto-Processing**: The app automatically detects the best extraction method
3. **View Results**: Results are rendered based on type (HTML, JSON, LaTeX, etc.)
4. **Download**: Save results in appropriate format (HTML, JSON, TXT)

## 🖼️ Sample Images

The repository includes 7 sample images demonstrating different OCR capabilities:

- `1_text_recognition.png` - Mixed text with different styles
- `2_table_recognition.png` - Sales report table
- `3_invoice_receipt.png` - Professional invoice
- `4_math_formulas.png` - Mathematical equations
- `5_form_recognition.png` - Application form
- `6_handwriting_sample.png` - Real handwritten sticky notes
- `7_document_understanding.png` - Research paper abstract

## 🔧 Architecture

### Model Server (`server.py`)
- FastAPI-based REST API
- Loads GLM-OCR once on startup
- Keeps model in GPU memory
- Serves predictions via HTTP

### Streamlit App (`app.py`)
- Web interface for easy interaction
- Gallery view with thumbnails
- Auto-detection of extraction method
- Smart rendering based on output type
- No model loading (uses server API)

## 📊 Performance

Based on testing with sample images:

- **Average processing**: ~6.5s per image
- **Fastest**: 2.76s (handwriting)
- **Slowest**: 10.60s (complex forms)
- **Device**: CUDA GPU (cuda:0)
- **Throughput**: 1.86 pages/s (PDF), 0.67 img/s

## 🎨 Output Rendering

### Tables
- Raw HTML code view
- Rendered table display
- Proper structure with headers/rows

### JSON
- Syntax-highlighted code
- Interactive JSON tree viewer
- Downloadable as .json

### LaTeX
- Rendered mathematical formulas
- Source code view
- Copy-paste ready for LaTeX editors

### Text
- Markdown rendering
- Plain text view
- Clean, formatted output

## 🛠️ API Reference

### Health Check

```bash
GET http://localhost:8508/
```

Response:
```json
{
  "status": "ok",
  "model": "zai-org/GLM-OCR",
  "model_loaded": true,
  "device": "cuda:0"
}
```

### Predict

```bash
POST http://localhost:8508/predict
Content-Type: multipart/form-data

Parameters:
- image: Image file
- prompt: Task prompt (e.g., "Text Recognition:", "Table Recognition:")
```

Response:
```json
{
  "success": true,
  "output": "extracted content",
  "prompt": "Text Recognition:"
}
```

## 📝 Custom Prompts

You can use custom prompts for specialized extraction:

### JSON Schema Extraction
```python
prompt = """Please extract in JSON format:
{
  "field1": "",
  "field2": "",
  "items": [{"name": "", "value": ""}]
}"""
```

### Entity Extraction
```python
prompt = "Extract all person names, dates, and locations:"
```

### Code Extraction
```python
prompt = "Extract all code blocks and identify programming languages:"
```

## 🌟 About GLM-OCR

GLM-OCR is developed by [Zhipu AI](https://huggingface.co/zai-org) and represents a breakthrough in efficient, high-quality OCR:

- **Compact**: Only 0.9B parameters
- **Accurate**: State-of-the-art across multiple benchmarks
- **Fast**: Optimized for production deployment
- **Versatile**: Handles text, tables, formulas, handwriting, and more
- **Multilingual**: 8+ languages supported

**Model Card**: https://huggingface.co/zai-org/GLM-OCR
**Documentation**: https://docs.z.ai

## 📜 License

This project is licensed under the MIT License.

The GLM-OCR model is also under MIT License - see https://huggingface.co/zai-org/GLM-OCR

## 🙏 Acknowledgments

- **Zhipu AI** for developing GLM-OCR
- **HuggingFace** for model hosting
- **Streamlit** for the web framework
- **FastAPI** for the API server

## 🤝 Contributing

Contributions are welcome! Feel free to:
- Add new sample images
- Improve the UI/UX
- Add new extraction methods
- Optimize performance
- Fix bugs

## 📧 Support

For issues with this application, please open an issue on GitHub.

For GLM-OCR model questions, visit: https://huggingface.co/zai-org/GLM-OCR

---

**Built with** ❤️ **using GLM-OCR, Streamlit, and FastAPI**
