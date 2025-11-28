import json
from pathlib import Path

PASILLOS = {1,4,7,10}
TRANSITIONS = {0,8}

p = Path(r'C:/Users/Admin/Documents/GitHub/Hackaton/simulate_response.json')
if not p.exists():
    raise SystemExit(f'No se encontró {p}')

data = json.loads(p.read_text(encoding='utf-8-sig'))

ruta = data.get('ruta') or data.get('Ruta') or data.get('path')
if ruta is None:
    raise SystemExit('El JSON no contiene la clave "ruta"')

# Normalizar
normalized = []
for pt in ruta:
    if isinstance(pt, (list, tuple)) and len(pt) >= 2:
        try:
            fila = int(pt[0])
            col = int(pt[1])
        except Exception:
            fila = int(float(pt[0]))
            col = int(float(pt[1]))
        normalized.append([fila, col])
    else:
        raise SystemExit(f'Punto de ruta con formato inesperado: {pt}')

violations = []
diagonals = []
for i in range(len(normalized) - 1):
    fila1, col1 = normalized[i]
    fila2, col2 = normalized[i + 1]
    # diagonal if both fila and columna change
    if fila1 != fila2 and col1 != col2:
        diagonals.append((normalized[i], normalized[i + 1]))
    # horizontal segment when fila is equal (same row, change column)
    if fila1 == fila2:
        left, right = min(col1, col2), max(col1, col2)
        crossed = [c for c in PASILLOS if left < c < right]
        if crossed and (col1 not in TRANSITIONS and col2 not in TRANSITIONS):
            violations.append({
                "segment": (normalized[i], normalized[i + 1]),
                "crossed_pasillos": crossed,
            })

print("Route validation report")
print("=======================")
print("Total points:", len(normalized))
print()
print("Diagonal keypoint segments (backend returned non-orthogonal keypoints):")
for d in diagonals:
    print(" -", d)
print()
print("Horizontal segments that cross PASILLOS without starting/ending at transition column (0 or 8):")
for v in violations:
    print(" - segment:", v["segment"], "crosses pasillos:", v["crossed_pasillos"]) 

if not diagonals and not violations:
    print("\nNo issues detected by this validator.")
else:
    print("\nIf there are violations, consider updating the backend to decompose those movements into H/V via a transition column (0 or 8).")
