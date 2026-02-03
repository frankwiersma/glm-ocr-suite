"""
GLM-OCR Model Server
Keeps the model loaded in memory and serves predictions via HTTP API
Run this separately from the Streamlit app for optimal performance
"""

from fastapi import FastAPI, File, UploadFile, Form
from fastapi.responses import JSONResponse
from transformers import AutoProcessor, AutoModelForImageTextToText
import torch
from PIL import Image
import io
import uvicorn
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(title="GLM-OCR Server", version="1.0")

# Global model and processor
MODEL = None
PROCESSOR = None
MODEL_PATH = "zai-org/GLM-OCR"

@app.on_event("startup")
async def load_model():
    """Load model on server startup"""
    global MODEL, PROCESSOR

    logger.info("="*80)
    logger.info("Loading GLM-OCR Model...")
    logger.info(f"Model: {MODEL_PATH}")
    logger.info("="*80)

    try:
        PROCESSOR = AutoProcessor.from_pretrained(MODEL_PATH)
        MODEL = AutoModelForImageTextToText.from_pretrained(
            pretrained_model_name_or_path=MODEL_PATH,
            torch_dtype="auto",
            device_map="auto",
        )

        logger.info(f"Model loaded successfully!")
        logger.info(f"Device: {MODEL.device}")
        logger.info(f"Dtype: {MODEL.dtype}")
        logger.info("="*80)
        logger.info("Server is ready to accept requests!")

    except Exception as e:
        logger.error(f"Failed to load model: {str(e)}")
        raise

@app.get("/")
async def root():
    """Health check endpoint"""
    return {
        "status": "ok",
        "model": MODEL_PATH,
        "model_loaded": MODEL is not None,
        "device": str(MODEL.device) if MODEL else None
    }

@app.post("/predict")
async def predict(
    image: UploadFile = File(...),
    prompt: str = Form("Text Recognition:")
):
    """
    Perform OCR prediction on uploaded image

    Parameters:
    - image: Image file
    - prompt: Task prompt (e.g., "Text Recognition:", "Table Recognition:")

    Returns:
    - JSON with prediction result
    """
    try:
        # Read image
        image_bytes = await image.read()
        pil_image = Image.open(io.BytesIO(image_bytes))

        # Save temporarily
        temp_path = "temp_server_image.png"
        pil_image.save(temp_path)

        # Prepare message
        messages = [
            {
                "role": "user",
                "content": [
                    {
                        "type": "image",
                        "url": temp_path
                    },
                    {
                        "type": "text",
                        "text": prompt
                    }
                ],
            }
        ]

        # Process
        inputs = PROCESSOR.apply_chat_template(
            messages,
            tokenize=True,
            add_generation_prompt=True,
            return_dict=True,
            return_tensors="pt"
        ).to(MODEL.device)

        inputs.pop("token_type_ids", None)

        # Generate
        logger.info(f"Processing image with prompt: {prompt}")
        generated_ids = MODEL.generate(**inputs, max_new_tokens=8192)
        output_text = PROCESSOR.decode(
            generated_ids[0][inputs["input_ids"].shape[1]:],
            skip_special_tokens=True
        )

        logger.info("Prediction completed successfully")

        return JSONResponse({
            "success": True,
            "output": output_text,
            "prompt": prompt
        })

    except Exception as e:
        logger.error(f"Prediction error: {str(e)}")
        return JSONResponse(
            status_code=500,
            content={
                "success": False,
                "error": str(e)
            }
        )

if __name__ == "__main__":
    print("\n" + "="*80)
    print("GLM-OCR Model Server")
    print("="*80)
    print("\nStarting server on http://localhost:8508")
    print("\nEndpoints:")
    print("  GET  /          - Health check")
    print("  POST /predict   - OCR prediction")
    print("\nThe model will load once and stay in memory.")
    print("Use this server with the Streamlit app for fast inference!")
    print("="*80 + "\n")

    uvicorn.run(app, host="0.0.0.0", port=8508, log_level="info")
