# validate_route.py
PASILLOS = {1,4,7,10}
TRANSITIONS = {0,8}

# Pega aquí la ruta tal cual la recibes; ejemplo tomado de tu salida:
route = [
    {
        "value":  [
                      0,
                      0
                  ],
        "Count":  2
    },
    {
        "value":  [
                      2,
                      0
                  ],
        "Count":  2
    },
    {
        "value":  [
                      6,
                      0
                  ],
        "Count":  2
    },
    {
        "value":  [
                      6,
                      3
                  ],
        "Count":  2
    },
    {
        "value":  [
                      6,
                      0
                  ],
        "Count":  2
    },
    {
        "value":  [
                      0,
                      0
                  ],
        "Count":  2
    },
    {
        "value":  [
                      0,
                      5
                  ],
        "Count":  2
    },
    {
        "value":  [
                      3,
                      6
                  ],
        "Count":  2
    },
    {
        "value":  [
                      3,
                      8
                  ],
        "Count":  2
    },
    {
        "value":  [
                      4,
                      8
                  ],
        "Count":  2
    },
    {
        "value":  [
                      1,
                      8
                  ],
        "Count":  2
    },
    {
        "value":  [
                      1,
                      9
                  ],
        "Count":  2
    },
    {
        "value":  [
                      1,
                      8
                  ],
        "Count":  2
    },
    {
        "value":  [
                      6,
                      8
                  ],
        "Count":  2
    },
    {
        "value":  [
                      6,
                      11
                  ],
        "Count":  2
    },
    {
        "value":  [
                      8,
                      11
                  ],
        "Count":  2
    }
]
def _to_point(elem):
    """Normaliza un elemento de ruta a [x:int, y:int].

    Soporta:
    - listas/tuplas: [x, y]
    - dicts con clave 'value' que contiene la lista [x, y]
    """
    if isinstance(elem, dict):
        # soporte flex: 'value' o 'Value'
        coords = elem.get('value') or elem.get('Value')
    else:
        coords = elem

    if not (isinstance(coords, (list, tuple)) and len(coords) >= 2):
        raise ValueError(f"No se pudo interpretar el elemento de ruta: {elem}")

    try:
        x = int(coords[0])
        y = int(coords[1])
    except Exception:
        # intentar convertir desde float-like strings
        x = int(float(coords[0]))
        y = int(float(coords[1]))
    return [x, y]


# Normalizar la ruta a una lista de puntos [x,y]
try:
    normalized = [_to_point(p) for p in route]
except Exception as e:
    print("Error al normalizar la ruta:", e)
    raise

violations = []
diagonals = []
for i in range(len(normalized) - 1):
    x1, y1 = normalized[i]
    x2, y2 = normalized[i + 1]
    if x1 != x2 and y1 != y2:
        diagonals.append((normalized[i], normalized[i + 1]))
    if y1 == y2:  # horizontal segment
        left, right = min(x1, x2), max(x1, x2)
        # check pasillos in the open interval between endpoints
        crossed = [c for c in PASILLOS if left < c < right]
        if crossed and (x1 not in TRANSITIONS and x2 not in TRANSITIONS):
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