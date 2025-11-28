PASILLOS = {1,4,7,10}
TRANSITIONS = {0,8}

route = [
    {"value": [0, 0], "Count": 2},
    {"value": [2, 0], "Count": 2},
    {"value": [6, 0], "Count": 2},
    {"value": [6, 3], "Count": 2},
    {"value": [6, 0], "Count": 2},
    {"value": [0, 0], "Count": 2},
    {"value": [0, 5], "Count": 2},
    {"value": [3, 5], "Count": 2},
    {"value": [3, 6], "Count": 2},
    {"value": [3, 8], "Count": 2},
    {"value": [4, 8], "Count": 2},
    {"value": [1, 8], "Count": 2},
    {"value": [1, 9], "Count": 2},
    {"value": [1, 8], "Count": 2},
    {"value": [6, 8], "Count": 2},
    {"value": [6, 11], "Count": 2},
    {"value": [8, 11], "Count": 2},
]


def _to_point(elem):
    if isinstance(elem, dict):
        coords = elem.get('value') or elem.get('Value')
    else:
        coords = elem
    if not (isinstance(coords, (list, tuple)) and len(coords) >= 2):
        raise ValueError(f"No se pudo interpretar el elemento de ruta: {elem}")
    try:
        x = int(coords[0])
        y = int(coords[1])
    except Exception:
        x = int(float(coords[0]))
        y = int(float(coords[1]))
    return [x, y]

normalized = [_to_point(p) for p in route]

violations = []
diagonals = []
for i in range(len(normalized) - 1):
    # Backend uses [fila, columna]
    fila1, col1 = normalized[i]
    fila2, col2 = normalized[i + 1]
    # diagonal if both fila and columna cambian
    if fila1 != fila2 and col1 != col2:
        diagonals.append((normalized[i], normalized[i + 1]))
    # horizontal segment when fila es igual (misma fila, cambia columna)
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
