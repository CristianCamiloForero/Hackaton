"""Ejemplo de uso del Sistema de Conteo Cíclico.

Este script puede ejecutarse localmente para probar la clase `ConteoCiclico`.
"""
from backend.conteo_ciclico import ConteoCiclico

def main():
    ubicaciones = [
        {'fila': 0, 'col': 0, 'sku': 'AUDIO-001', 'movimientos': 12, 'conteos_ultimos_365dias': 1},
        {'fila': 2, 'col': 4, 'sku': 'COMP-101', 'movimientos': 5, 'conteos_ultimos_365dias': 3},
        {'fila': 5, 'col': 7, 'sku': 'REFR-555', 'movimientos': 2, 'conteos_ultimos_365dias': 0},
        {'fila': 8, 'col': 10, 'sku': 'AC-900', 'movimientos': 0, 'conteos_ultimos_365dias': 4},
    ]

    cc = ConteoCiclico(frecuencia_minima=5)
    plan = cc.generar_plan(ubicaciones)

    from pprint import pprint
    pprint(plan)

if __name__ == '__main__':
    main()
