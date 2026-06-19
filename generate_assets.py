import base64

files = {
    'IMG_CAPSULES': 'assets/pharma_capsules.jpeg',
    'IMG_AI_HANDS': 'assets/ai_handshake.jpeg',
    'IMG_HOLOGRAM': 'assets/health_hologram.jpeg',
    'IMG_DNA':      'assets/dna_helix.jpeg',
}

with open('image_assets.py', 'w') as out:
    for var, path in files.items():
        with open(path, 'rb') as f:
            b64 = base64.b64encode(f.read()).decode()
        out.write(f'{var} = "data:image/jpeg;base64,{b64}"\n')

print("Done! image_assets.py created.")