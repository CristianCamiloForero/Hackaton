from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .robot import RobotAlmacen
from .config import PAQUETES, INICIO, COSTO_CELDA, COSTO_PASILLO, PASILLOS, FILAS, COLUMNAS, ALMACENES
from .entrada import GestorEntrada
from .consolidador import ConsolidadorPicking
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


if __name__ == '__main__':
    import uvicorn
    uvicorn.run(app, host='0.0.0.0', port=5000)
