"""Multimodal Vision & Document OCR for LogiFlow.

Uses OpenAI gpt-4o-mini vision capabilities to inspect:
- Cargo and package damage photos
- Shipping labels, barcodes, and waybills
- Bills of Lading (BOL) and commercial invoices
"""

import base64
import os
import mimetypes
from pathlib import Path
from typing import Any
from openai import OpenAI


def inspect_shipping_document_or_image(
    file_path_or_url: str,
    prompt_focus: str = "",
) -> dict[str, Any]:
    """Inspect and extract structured logistics data from a document or cargo photo.

    Supports local file paths (PNG, JPG, WEBP) and web image URLs.
    Extracts text, detected barcodes, tracking numbers, damage severity, and recommended actions.

    Args:
        file_path_or_url: Local file path or HTTP(S) image URL.
        prompt_focus: Specific detail to focus on (e.g. 'check for box damage', 'read BOL consignee').

    Returns:
        dict containing document_type, detected_ids, damage_assessment, severity,
        extracted_text_summary, and actionable_recommendation.
    """
    api_key = os.getenv("OPENAI_API_KEY", "")
    if not api_key:
        return {
            "status": "error",
            "error": "OPENAI_API_KEY not configured for multimodal vision inspection.",
        }

    client = OpenAI(api_key=api_key)

    # Determine if URL or local file
    is_url = file_path_or_url.startswith("http://") or file_path_or_url.startswith("https://")

    if is_url:
        image_url_obj = {"url": file_path_or_url}
    else:
        path = Path(file_path_or_url)
        if not path.exists():
            return {
                "status": "error",
                "error": f"Image file not found at: {file_path_or_url}",
            }

        mime_type, _ = mimetypes.guess_type(str(path))
        if not mime_type or not mime_type.startswith("image/"):
            mime_type = "image/jpeg"

        with open(path, "rb") as f:
            encoded = base64.b64encode(f.read()).decode("utf-8")
        image_url_obj = {"url": f"data:{mime_type};base64,{encoded}"}

    focus_instruction = f"Special focus requested: {prompt_focus}" if prompt_focus else ""

    system_prompt = """You are LogiFlow's expert Computer Vision & Logistics Document Inspector.
Analyze the provided image (which could be a damaged package, shipping label, bill of lading, or pallet).

Respond with a clear, structured JSON report containing:
1. "document_or_cargo_type": (e.g. "corrugated carton damage", "bill of lading", "shipping label", "pallet seal")
2. "detected_tracking_or_barcode": string or null
3. "damage_detected": boolean
4. "damage_severity": "none" | "low" | "medium" | "high" | "critical"
5. "visual_findings": detailed bullet summary of what you observe
6. "recommended_action": clear operational next step (e.g., "quarantine unit", "proceed with standard delivery", "re-print label")
"""

    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            response_format={"type": "json_object"},
            messages=[
                {"role": "system", "content": system_prompt},
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "text",
                            "text": f"Please inspect this logistics asset. {focus_instruction}",
                        },
                        {"type": "image_url", "image_url": image_url_obj},
                    ],
                },
            ],
            max_tokens=600,
        )

        import json
        parsed = json.loads(response.choices[0].message.content or "{}")

        return {
            "status": "success",
            "source": file_path_or_url,
            "inspection": parsed,
        }

    except Exception as e:
        return {
            "status": "error",
            "source": file_path_or_url,
            "error": f"Vision inspection failed: {str(e)}",
        }


VISION_TOOLS = [inspect_shipping_document_or_image]
