"""Generate an image of a decorated cup using the course LLM gateway.

Uses the `text-to-image` model on https://llm.alem.ai (OpenAI-compatible
images endpoint). The response may carry the image as a URL or as a
base64-encoded payload; both cases are handled.
"""

import base64
import json
import os
import sys
import urllib.request

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from env_loader import require_env

API_URL = "https://llm.alem.ai/v1/images/generations"
API_KEY = require_env("LLM_IMAGE_API_KEY")

PROMPT = (
    "A beautiful ceramic coffee cup on a wooden table, with a nice "
    "picture printed on its side: a scenic painting of snow-capped "
    "mountains and a lake at sunset, soft studio lighting, "
    "highly detailed, photorealistic product photography"
)


def generate_image(prompt: str, size: str = "512x512") -> bytes:
    """Call the text-to-image endpoint and return the raw image bytes."""
    payload = json.dumps(
        {"model": "text-to-image", "prompt": prompt, "size": size}
    ).encode("utf-8")

    request = urllib.request.Request(
        API_URL,
        data=payload,
        headers={
            "Authorization": f"Bearer {API_KEY}",
            "Content-Type": "application/json",
        },
        method="POST",
    )

    with urllib.request.urlopen(request) as response:
        body = json.loads(response.read().decode("utf-8"))

    item = body["data"][0]

    if item.get("b64_json"):
        return base64.b64decode(item["b64_json"])

    if item.get("url"):
        with urllib.request.urlopen(item["url"]) as image_response:
            return image_response.read()

    raise ValueError(f"Unexpected response format: {body}")


def main() -> None:
    output_path = os.path.join(os.path.dirname(__file__), "cup.png")
    print("Generating image of a decorated cup...")
    image_bytes = generate_image(PROMPT)
    with open(output_path, "wb") as f:
        f.write(image_bytes)
    print(f"Saved image to {output_path} ({len(image_bytes)} bytes)")


if __name__ == "__main__":
    main()
