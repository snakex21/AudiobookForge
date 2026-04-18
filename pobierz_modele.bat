@echo off
cd /d "C:\Users\ASRock\Desktop\AudiobookForge\piper_models"
echo Pobieranie darkman...
curl -L -o pl_PL-darkman-medium.onnx "https://huggingface.co/rhasspy/piper-voices/resolve/main/pl/pl_PL/darkman/medium/pl_PL-darkman-medium.onnx"
curl -L -o pl_PL-darkman-medium.onnx.json "https://huggingface.co/rhasspy/piper-voices/resolve/main/pl/pl_PL/darkman/medium/pl_PL-darkman-medium.onnx.json"
echo Pobieranie gosia...
curl -L -o pl_PL-gosia-medium.onnx "https://huggingface.co/rhasspy/piper-voices/resolve/main/pl/pl_PL/gosia/medium/pl_PL-gosia-medium.onnx"
curl -L -o pl_PL-gosia-medium.onnx.json "https://huggingface.co/rhasspy/piper-voices/resolve/main/pl/pl_PL/gosia/medium/pl_PL-gosia-medium.onnx.json"
echo Gotowe!
dir
pause