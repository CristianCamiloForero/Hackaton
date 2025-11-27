# Configuración inicial del almacén (módulo backend)
FILAS = 9
COLUMNAS = 12
PASILLOS = [1, 4, 7, 10]
PAQUETES = [[2,0], [6,3], [0,5], [3,6], [4,8], [1,9], [6,11]]
INICIO = [0, 0]  # [fila, col]
COSTO_CELDA = 2.7
COSTO_PASILLO = 5.0

# Definición de almacenes (zonas) con nombres y colores
ALMACENES = [
    {
        "nombre": "Audio",
        "color": "#3b82f6",  # Azul
        "columnas": [0, 1, 2]
    },
    {
        "nombre": "Cómputo",
        "color": "#10b981",  # Verde
        "columnas": [3, 4, 5]
    },
    {
        "nombre": "Refrigeración",
        "color": "#ef4444",  # Rojo
        "columnas": [6, 7, 8]
    },
    {
        "nombre": "Aire Acondicionado",
        "color": "#8b5cf6",  # Morado
        "columnas": [9, 10, 11]
    }
]

def get_almacen_by_column(col):
    """Retorna el almacén correspondiente a una columna"""
    for almacen in ALMACENES:
        if col in almacen["columnas"]:
            return almacen
    return None
