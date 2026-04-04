import json
import base64

from flask import Blueprint, request, jsonify

from auth import login_required
import config

bp = Blueprint("receipt", __name__, url_prefix="/api")


@bp.route("/parse-receipt", methods=["POST"])
@login_required
def parse_receipt():
    if not config.GEMINI_API_KEY:
        return jsonify({"error": "Receipt scanning is not configured"}), 501

    data = request.get_json(silent=True) or {}
    image_b64 = data.get("image")
    mime_type = data.get("mimeType", "image/jpeg")

    if not image_b64:
        return jsonify({"error": "No image provided"}), 400

    # Strip data URL prefix if present (e.g. "data:image/jpeg;base64,...")
    if "," in image_b64:
        header, image_b64 = image_b64.split(",", 1)
        if "image/" in header:
            mime_type = header.split("image/")[1].split(";")[0]
            mime_type = f"image/{mime_type}"

    # Validate it's actual base64
    try:
        img_bytes = base64.b64decode(image_b64)
        if len(img_bytes) > 10 * 1024 * 1024:  # 10MB limit
            return jsonify({"error": "Image too large (max 10MB)"}), 400
    except Exception:
        return jsonify({"error": "Invalid image data"}), 400

    try:
        from google import genai

        client = genai.Client(api_key=config.GEMINI_API_KEY)

        prompt = (
            "Parse this receipt image. Extract each line item with its name, price, and category. "
            "Return ONLY valid JSON in this exact format, no markdown, no explanation:\n"
            '{"items": [{"name": "item name", "price": 12.50, "category": "groceries"}], "total": 99.99, "category": "groceries"}\n'
            "Rules:\n"
            "- price must be a number (not a string)\n"
            "- total is the receipt total if visible, otherwise sum of item prices\n"
            "- category for each item must be one of: groceries, rent, utilities, fun, food, transport, other\n"
            "- top-level category should be the most common category among items\n"
            "- If you cannot parse the receipt, return: {\"items\": [], \"total\": 0, \"error\": \"Could not parse receipt\"}"
        )

        model_name = config.GEMINI_MODEL or "gemini-2.0-flash-lite"
        response = client.models.generate_content(
            model=model_name,
            contents=[
                prompt,
                {"inline_data": {"mime_type": mime_type, "data": image_b64}},
            ],
        )

        text = response.text.strip()
        # Strip markdown code fences if Gemini wraps the response
        if text.startswith("```"):
            text = text.split("\n", 1)[1] if "\n" in text else text[3:]
        if text.endswith("```"):
            text = text[:-3].strip()
        if text.startswith("json"):
            text = text[4:].strip()

        parsed = json.loads(text)
        items = parsed.get("items", [])
        total = parsed.get("total", 0)

        # Build description string: item1(₹val), item2(₹val)
        desc_parts = []
        computed_total = 0
        for item in items:
            name = str(item.get("name", "")).strip()
            price = float(item.get("price", 0))
            computed_total += price
            if name:
                desc_parts.append(f"{name}({price:.2f})")

        # Use receipt total if available, otherwise computed
        if total and float(total) > 0:
            final_total = round(float(total), 2)
        else:
            final_total = round(computed_total, 2)

        return jsonify({
            "items": items,
            "total": final_total,
            "description": ", ".join(desc_parts),
            "category": parsed.get("category", "other"),
            "error": parsed.get("error"),
        }), 200

    except json.JSONDecodeError:
        return jsonify({"error": "Failed to parse AI response"}), 502
    except ImportError:
        return jsonify({"error": "google-genai package not installed"}), 501
    except Exception as e:
        err_str = str(e)
        if "429" in err_str or "RESOURCE_EXHAUSTED" in err_str:
            return jsonify({"error": "AI quota exceeded — try again later or check your Gemini plan"}), 429
        return jsonify({"error": f"Receipt parsing failed: {err_str}"}), 500
