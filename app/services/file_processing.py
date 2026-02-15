import os
import re
import tempfile
from typing import Optional, Dict, Any
from fastapi import UploadFile, HTTPException
import pandas as pd
from pathlib import Path
from datetime import datetime

# Optional: OCR via pytesseract (requires Tesseract-OCR installed)
try:
    import pytesseract
    from pdf2image import convert_from_path
    HAS_OCR = True
except ImportError:
    HAS_OCR = False

# Optional: AI extraction via OpenAI
try:
    import openai
    HAS_AI = True
except ImportError:
    HAS_AI = False


def calculate_delay(dfc) -> Optional[int]:
    """
    Dynamically calculate the delay in days between reception and response dates.
    
    Args:
        dfc: DFC instance with date_reception and date_reponse attributes
    
    Returns:
        Number of days between dates, or None if dates are missing
    """
    if dfc.date_reception and dfc.date_reponse:
        return (dfc.date_reponse - dfc.date_reception).days
    return None


async def extract_pdf_text(file_path: str) -> str:
    """Extract text from PDF using OCR or native extraction."""
    if not HAS_OCR:
        raise HTTPException(status_code=400, detail="OCR not available. Install pytesseract and poppler.")
    
    try:
        images = convert_from_path(file_path)
        text = ""
        for image in images:
            text += pytesseract.image_to_string(image) + "\n"
        return text
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"PDF extraction failed: {str(e)}")


def extract_excel_data(file_path: str) -> Dict[str, Any]:
    """Extract data from Excel file."""
    try:
        xls = pd.ExcelFile(file_path)
        data = {}
        for sheet in xls.sheet_names:
            df = pd.read_excel(file_path, sheet_name=sheet)
            data[sheet] = df.to_dict(orient="records")
        return data
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Excel extraction failed: {str(e)}")


def parse_dfc_fields(text: str) -> Dict[str, Optional[str]]:
    """
    Parse DFC fields from extracted text using regex patterns.
    Maps common DFC document fields to schema.
    """
    fields = {
        "numero_dfc": None,
        "projet": None,
        "famille": None,
        "phase": None,
        "description": None,
        "faisabilite": None,
        "type_dfc": None,
    }
    
    # Simple regex patterns for common DFC format
    patterns = {
        "numero_dfc": r"(?:N°|No|Numero|Nº)\s*DFC\s*:?\s*(\d+)",
        "projet": r"(?:Projet|Project)\s*:?\s*([A-Za-z\s]+?)(?:\n|,|$)",
        "famille": r"(?:Famille|Family)\s*:?\s*([A-Za-z\s]+?)(?:\n|,|$)",
        "phase": r"(?:Phase|Stage)\s*:?\s*([A-Z]{2,4})",
        "description": r"(?:Sujet|Subject|Description)\s*:?\s*([^\n]+)",
        "faisabilite": r"(?:Faisabilité|Feasibility)\s*:?\s*(Oui|Non|Yes|No|OG|NC)",
        "type_dfc": r"(?:Type)\s*:?\s*(T[1-3]|Mistaked)",
    }
    
    for field, pattern in patterns.items():
        match = re.search(pattern, text, re.IGNORECASE | re.MULTILINE)
        if match:
            fields[field] = match.group(1).strip()
    
    return fields


async def use_ai_to_extract_fields(text: str) -> Dict[str, Optional[str]]:
    """
    Use OpenAI GPT to extract and map DFC fields.
    Requires OPENAI_API_KEY environment variable.
    """
    if not HAS_AI:
        raise HTTPException(status_code=400, detail="AI extraction not available. Install openai.")
    
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise HTTPException(status_code=400, detail="OPENAI_API_KEY not configured.")
    
    # Use new OpenAI client if available
    try:
        from openai import OpenAI
        client = OpenAI(api_key=api_key)
    except Exception:
        # fallback to legacy openai module if present
        openai.api_key = api_key
        client = None

    prompt = f"""
    Extract DFC (Design Feasibility Change) fields from the following document text.
    Return a JSON object with these fields (use null if not found):
    - numero_dfc (integer)
    - projet (string)
    - famille (string)
    - phase (string)
    - description (string)
    - faisabilite (string: Oui/Non/OG/NC)
    - type_dfc (string: T1/T2/T3/Mistaked)
    
    Document text:
    {text[:2000]}
    
    Return only valid JSON, no markdown.
    """
    
    try:
        if client:
            response = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[{"role": "user", "content": prompt}],
                temperature=0.3,
            )
            content = response.choices[0].message.content
        else:
            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=[{"role": "user", "content": prompt}],
                temperature=0.3,
            )
            content = response.choices[0].message.content

        import json
        result = json.loads(content)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"AI extraction failed: {str(e)}")


async def process_uploaded_file(file: UploadFile, use_ai: bool = False) -> Dict[str, Any]:
    """
    Process uploaded file (PDF, Excel, CSV) and extract DFC fields.
    """
    allowed_types = {".pdf", ".xlsx", ".xls", ".csv"}
    file_ext = Path(file.filename).suffix.lower()
    
    if file_ext not in allowed_types:
        raise HTTPException(status_code=400, detail=f"File type {file_ext} not supported. Use {allowed_types}")
    
    # Save file temporarily
    with tempfile.NamedTemporaryFile(delete=False, suffix=file_ext) as tmp:
        contents = await file.read()
        tmp.write(contents)
        tmp_path = tmp.name
    
    try:
        extracted_text = ""
        raw_data = {}
        
        if file_ext == ".pdf":
            extracted_text = await extract_pdf_text(tmp_path)
        elif file_ext in [".xlsx", ".xls"]:
            raw_data = extract_excel_data(tmp_path)
            # Convert to text for pattern matching
            extracted_text = str(raw_data)
        elif file_ext == ".csv":
            df = pd.read_csv(tmp_path)
            extracted_text = df.to_string()
        
        # Parse fields using regex
        parsed_fields = parse_dfc_fields(extracted_text)
        
        # Optionally use AI for better extraction
        if use_ai:
            try:
                ai_fields = await use_ai_to_extract_fields(extracted_text)
                # Merge AI results with regex results (AI takes priority)
                parsed_fields.update({k: v for k, v in ai_fields.items() if v is not None})
            except Exception as e:
                # Fall back to regex if AI fails
                pass
        
        return {
            "filename": file.filename,
            "extracted_fields": parsed_fields,
            "raw_text_length": len(extracted_text),
            "raw_data_keys": list(raw_data.keys()) if raw_data else None,
        }
    
    finally:
        # Clean up temp file
        os.unlink(tmp_path)

