from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .robot import RobotAlmacen
from .config import PAQUETES, INICIO, COSTO_CELDA, COSTO_PASILLO, PASILLOS, FILAS, COLUMNAS, ALMACENES
from .entrada import GestorEntrada
from .consolidador import ConsolidadorPicking
from .conteo_ciclico import ConteoCiclico
from .exportador import Exportador
import io
from fastapi.responses import StreamingResponse

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get('/defaults')
def get_defaults():
    return {
        'paquetes': PAQUETES,
        'inicio': INICIO,
        'costo_celda': COSTO_CELDA,
        'costo_pasillo': COSTO_PASILLO
    }


@app.post('/simulate')
def simulate(payload: dict):
    data = payload or {}
    paquetes = data.get('paquetes', PAQUETES)
    inicio = GestorEntrada.validar_inicio(data.get('inicio', INICIO))
    costos = data.get('costos', {})
    costos_validos = GestorEntrada.validar_costos(costos) if costos else {'celda': data.get('costo_celda', COSTO_CELDA), 'pasillo': data.get('costo_pasillo', COSTO_PASILLO)}

    paquetes_validos = GestorEntrada.validar_paquetes(paquetes)

    robot = RobotAlmacen(paquetes=paquetes_validos, inicio=inicio, costo_celda=costos_validos['celda'], costo_pasillo=costos_validos['pasillo'])
    resultado = robot.ejecutar_recoleccion()

    # devolver resultado
    return resultado


@app.post('/consolidate')
def consolidate_orders(payload: dict):
    """Consolida múltiples órdenes en una lista de picking optimizada.
    
    payload: {
        'ordenes': [
            {'id_orden': 'ORD001', 'items': [[fila, col, cantidad, sku], ...]},
            {'id_orden': 'ORD002', 'items': [[fila, col, cantidad, sku], ...]},
            ...
        ]
    }
    """
    ordenes = payload.get('ordenes', [])
    
    if not ordenes:
        return {'error': 'No hay órdenes para consolidar'}
    
    consolidador = ConsolidadorPicking()
    resultado = consolidador.consolidar_ordenes(ordenes)
    
    return resultado


@app.get('/warehouse-config')
def get_warehouse_config():
    """Retorna configuración del almacén (incluyendo almacenes/zonas)"""
    return {
        'filas': FILAS,
        'columnas': COLUMNAS,
        'pasillos': PASILLOS,
        'almacenes': ALMACENES,
        'costo_celda': COSTO_CELDA,
        'costo_pasillo': COSTO_PASILLO
    }


@app.post('/cycle-count')
def cycle_count(payload: dict):
    """Genera un plan de conteo cíclico priortizado.

    Payload esperado:
    {
      "ubicaciones": [ {"fila": int, "col": int, "sku": str, "movimientos": int, "conteos_ultimos_365dias": int}, ... ],
      "frecuencia_minima": 5  # opcional
    }
    """
    data = payload or {}
    ubicaciones = data.get('ubicaciones', [])
    frecuencia = int(data.get('frecuencia_minima', 5))
    # Heurísticas opcionales
    weights = data.get('weights', None)  # {'faltantes':100, 'movimientos':1, 'criticidad':50}
    zone_weights = data.get('zone_weights', None)  # {'Audio': 50, ...}

    cc = ConteoCiclico(frecuencia_minima=frecuencia, weights=weights, zone_weights=zone_weights)
    plan = cc.generar_plan(ubicaciones)
    return plan


@app.post('/export-cycle')
def export_cycle(payload: dict):
    """Exporta a Excel/CSV un `plan` (lista) o genera plan desde `ubicaciones` si se pasa.

    Payload aceptado:
      - plan: [...]
    o
      - ubicaciones + frecuencia_minima + weights + zone_weights
    """
    data = payload or {}
    plan = data.get('plan')
    if not plan:
        # generar plan desde ubicaciones si vienen
        ubicaciones = data.get('ubicaciones', [])
        frecuencia = int(data.get('frecuencia_minima', 5))
        weights = data.get('weights', None)
        zone_weights = data.get('zone_weights', None)
        cc = ConteoCiclico(frecuencia_minima=frecuencia, weights=weights, zone_weights=zone_weights)
        plan = cc.generar_plan(ubicaciones).get('plan', [])

    bytes_data = Exportador.export_cycle_plan_bytes(plan)

    # Detectar si es CSV o Excel por contenido (naive): openpyxl produces XLSX binary with PK signature
    filename = 'plan_conteo.xlsx'
    media_type = 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    try:
        # If first bytes start with PK (zip), treat as xlsx
        if isinstance(bytes_data, (bytes, bytearray)) and bytes_data[:2] != b'PK':
            # likely CSV
            filename = 'plan_conteo.csv'
            media_type = 'text/csv'
    except Exception:
        pass

    return StreamingResponse(io.BytesIO(bytes_data), media_type=media_type, headers={
        'Content-Disposition': f'attachment; filename="{filename}"'
    })


if __name__ == '__main__':
    import uvicorn
    uvicorn.run(app, host='0.0.0.0', port=5000)


@app.post('/export')
def export_excel(payload: dict):
    """Genera un Excel desde la simulación y lo devuelve como descarga
    payload: mismos campos que /simulate
    """
    paquetes = payload.get('paquetes', PAQUETES)
    inicio = GestorEntrada.validar_inicio(payload.get('inicio', INICIO))
    costos = payload.get('costos', {})
    costos_validos = GestorEntrada.validar_costos(costos) if costos else {'celda': payload.get('costo_celda', COSTO_CELDA), 'pasillo': payload.get('costo_pasillo', COSTO_PASILLO)}
    paquetes_validos = GestorEntrada.validar_paquetes(paquetes)

    robot = RobotAlmacen(paquetes=paquetes_validos, inicio=inicio, costo_celda=costos_validos['celda'], costo_pasillo=costos_validos['pasillo'])
    resultado = robot.ejecutar_recoleccion()

    # Intentar crear Excel en memoria
    try:
        import pandas as pd
        from io import BytesIO
        df = pd.DataFrame(robot.pasos)
        buffer = BytesIO()
        with pd.ExcelWriter(buffer, engine='openpyxl') as writer:
            df.to_excel(writer, index=False, sheet_name='Pasos')
        buffer.seek(0)
        from fastapi.responses import StreamingResponse
        headers = {'Content-Disposition': 'attachment; filename="reporte_recoleccion.xlsx"'}
        return StreamingResponse(buffer, media_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet', headers=headers)
    except Exception as e:
        # si falla, devolver error
        return {'error': 'No se pudo generar Excel en el servidor', 'detail': str(e)}
