import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from pipeline import generate_audio_with_piper, resolve_ffmpeg_path


PROJECT_DIR = Path(__file__).resolve().parent
MODELS_DIR = PROJECT_DIR / "piper_models"
OUTPUT_DIR = PROJECT_DIR / "tts_test"
OUTPUT_DIR.mkdir(exist_ok=True)

TEST_TEXTS = [
    "Człowiek jest w zasadzie nieśmiertelny, chyba że zatraci swój instynkt samozachowawczy.",
    "Stwardnienie rozsiane, łuszczyca i alergie kpią z naszych leków.",
    "Współczesne narody usiłują rozwój techniki wznieść do granic cudów.",
    "Przedłużamy w czasach dzisiejszych życie ludzkie o kilkanaście lat.",
    "Szczątki oraz fragmenty murów świątyń i pałaców Paryża.",
]

models = list(MODELS_DIR.glob("*.onnx"))

if not models:
    print("Brak modeli w piper_models/")
    sys.exit(1)

for model_path in models:
    model_name = model_path.stem
    print(f"\n=== Testuję: {model_name} ===")
    for i, text in enumerate(TEST_TEXTS):
        out = OUTPUT_DIR / f"{model_name}_test{i+1}.mp3"
        try:
            generate_audio_with_piper(text, out, model_path=model_path)
            print(f"  OK test{i+1}: {out.name}")
        except Exception as e:
            print(f"  ERR test{i+1}: {e}")

print(f"\nGotowe! Pliki w: {OUTPUT_DIR}")
