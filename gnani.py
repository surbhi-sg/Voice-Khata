import os, subprocess, tempfile
import requests
import imageio_ffmpeg
from dotenv import load_dotenv
load_dotenv()

BASE = "https://api.vachana.ai"
STT_KEY = os.getenv("GNANI_STT_KEY") or os.getenv("GNANI_API_KEY")
TTS_KEY = os.getenv("GNANI_TTS_KEY") or os.getenv("GNANI_API_KEY")


def to_wav16k(data):
    with tempfile.TemporaryDirectory() as d:
        src, dst = os.path.join(d, "in"), os.path.join(d, "out.wav")
        with open(src, "wb") as f:
            f.write(data)
        subprocess.run(
            [imageio_ffmpeg.get_ffmpeg_exe(), "-y", "-loglevel", "error",
             "-i", src, "-ar", "16000", "-ac", "1", dst],
            check=True,
        )
        with open(dst, "rb") as f:
            return f.read()


def stt(audio_bytes, lang="hi-IN"):
    wav = to_wav16k(audio_bytes)

    def call(code):
        return requests.post(
            f"{BASE}/stt/v3",
            headers={"X-API-Key-ID": STT_KEY},
            files={"audio_file": ("clip.wav", wav, "audio/wav")},
            data={"language_code": code},
            timeout=60,
        )

    r = call(lang)
    if not r.ok:
        raise RuntimeError(f"STT {r.status_code}: {r.text}")
    return r.json()["transcript"]


def tts(text, lang="hi-IN"):
    body = {
        "text": text,
        "voice": "Nalini",
        "model": "timbre-v2.5",
        "language": lang,
        "speed": 1.0,
        "audio_config": {
            "sample_rate": 24000, "num_channels": 1, "sample_width": 2,
            "encoding": "linear_pcm", "container": "wav",
        },
    }
    r = requests.post(
        f"{BASE}/api/v1/tts/inference",
        headers={"X-API-Key-ID": TTS_KEY},
        json=body,
        timeout=60,
    )
    r.raise_for_status()
    return r.content