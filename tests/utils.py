PASILLOS = {1,4,7,10}
TRANSITIONS = {0,8}


def normalize_route(ruta):
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
            raise ValueError(f'Punto de ruta con formato inesperado: {pt}')
    return normalized


def validate_route(ruta):
    """Return (diagonals, violations).

    - diagonals: list of ((f1,c1),(f2,c2)) where both fila and col change
    - violations: list of dicts with keys 'segment' and 'crossed_pasillos'
    """
    normalized = normalize_route(ruta)
    diagonals = []
    violations = []
    for i in range(len(normalized) - 1):
        fila1, col1 = normalized[i]
        fila2, col2 = normalized[i + 1]
        if fila1 != fila2 and col1 != col2:
            diagonals.append((normalized[i], normalized[i + 1]))
        if fila1 == fila2:
            left, right = min(col1, col2), max(col1, col2)
            crossed = [c for c in PASILLOS if left < c < right]
            if crossed and (col1 not in TRANSITIONS and col2 not in TRANSITIONS):
                violations.append({
                    'segment': (normalized[i], normalized[i + 1]),
                    'crossed_pasillos': crossed,
                })
    return diagonals, violations
