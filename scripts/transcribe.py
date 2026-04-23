#!/usr/bin/env python3
"""
Voice transcription using Azure Speech-to-Text
Usage: python3 transcribe.py <audio_file.ogg>
"""
import sys
import json
import urllib.request
import os

AZURE_KEY = os.getenv("AZURE_SPEECH_KEY", "910be9b8d0c24674af59807d6f1ed2e9")
AZURE_REGION = os.getenv("AZURE_SPEECH_REGION", "swedencentral")

def transcribe(audio_path: str, language: str = "en-US") -> str:
    url = (
        f"https://{AZURE_REGION}.stt.speech.microsoft.com"
        f"/speech/recognition/conversation/cognitiveservices/v1"
        f"?language={language}&format=detailed"
    )

    ext = audio_path.lower().split('.')[-1]
    content_type_map = {
        "ogg": "audio/ogg; codecs=opus",
        "wav": "audio/wav",
        "mp3": "audio/mpeg",
        "mp4": "audio/mp4",
        "m4a": "audio/mp4",
    }
    content_type = content_type_map.get(ext, "audio/ogg; codecs=opus")

    with open(audio_path, "rb") as f:
        audio_data = f.read()

    req = urllib.request.Request(url, data=audio_data, method="POST")
    req.add_header("Ocp-Apim-Subscription-Key", AZURE_KEY)
    req.add_header("Content-Type", content_type)
    req.add_header("Accept", "application/json")

    with urllib.request.urlopen(req, timeout=30) as resp:
        result = json.loads(resp.read())

    status = result.get("RecognitionStatus")
    if status == "Success":
        return result.get("DisplayText", "")
    else:
        return f"[Transcription failed: {status}]"


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: transcribe.py <audio_file>")
        sys.exit(1)
    print(transcribe(sys.argv[1]))
