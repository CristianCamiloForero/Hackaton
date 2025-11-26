from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .robot import RobotAlmacen
from .config import PAQUETES, INICIO, COSTO_CELDA, COSTO_PASILLO
from .entrada import GestorEntrada

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


if __name__ == '__main__':
    import uvicorn
    uvicorn.run(app, host='0.0.0.0', port=5000)
