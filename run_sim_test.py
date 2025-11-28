import sys
sys.path.append('.')
from backend.robot import RobotAlmacen
from backend.config import PAQUETES, INICIO

try:
    r = RobotAlmacen(paquetes=PAQUETES, inicio=INICIO)
    res = r.ejecutar_recoleccion()
    import json
    print(json.dumps(res['ruta'], indent=2))
    print('OK')
except Exception as e:
    import traceback
    traceback.print_exc()
    print('ERROR:', e)
