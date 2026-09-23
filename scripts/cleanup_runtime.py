from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
for folder in [ROOT / 'runtime' / 'uploads', ROOT / 'runtime' / 'reports']:
    folder.mkdir(parents=True, exist_ok=True)
    for path in folder.iterdir():
        if path.is_file():
            path.unlink(missing_ok=True)
print('Runtime artifacts cleaned.')
