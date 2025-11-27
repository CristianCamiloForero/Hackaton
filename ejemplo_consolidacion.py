"""
Ejemplo de uso del consolidador de picking.
Ejecuta esto para probar la funcionalidad de consolidación de múltiples órdenes.
"""

import requests
import json

API_BASE = 'http://127.0.0.1:5000'

# Ejemplo 1: Consolidar múltiples órdenes simples
def ejemplo_consolidacion_simple():
    print("=" * 80)
    print("EJEMPLO 1: Consolidación Simple de Órdenes")
    print("=" * 80)
    
    ordenes = [
        {
            'id_orden': 'ORD001',
            'items': [
                [2, 0, 1, 'SKU-001'],  # fila, col, cantidad, sku
                [6, 3, 2, 'SKU-002']
            ]
        },
        {
            'id_orden': 'ORD002',
            'items': [
                [0, 5, 1, 'SKU-003'],
                [3, 6, 3, 'SKU-004']
            ]
        },
        {
            'id_orden': 'ORD003',
            'items': [
                [4, 8, 2, 'SKU-005'],
                [1, 9, 1, 'SKU-006'],
                [2, 0, 1, 'SKU-007']  # Mismo lugar que ORD001 - se consolidará
            ]
        }
    ]
    
    payload = {'ordenes': ordenes}
    
    try:
        response = requests.post(f'{API_BASE}/consolidate', json=payload)
        result = response.json()
        
        print("\n✓ Respuesta del servidor:")
        print(json.dumps(result, indent=2))
        
        # Mostrar estadísticas
        stats = result.get('estadisticas', {})
        print(f"\n📊 ESTADÍSTICAS:")
        print(f"  • Total de items: {stats.get('total_items')}")
        print(f"  • Órdenes procesadas: {stats.get('ordenes')}")
        print(f"  • Ubicaciones únicas: {stats.get('ubicaciones_unicas')}")
        print(f"  • Distancia estimada: {stats.get('distancia_estimada')} unidades")
        print(f"  • Columnas a visitar: {stats.get('columnas_visitadas')}")
        
        # Mostrar picking list
        picking_list = result.get('picking_list', [])
        print(f"\n📋 LISTA DE PICKING (orden optimizado):")
        print(f"{'#':<4} {'FILA':<6} {'COL':<6} {'CANT':<6} {'SKUS':<20} {'ÓRDENES':<20}")
        print("-" * 70)
        for idx, item in enumerate(picking_list, 1):
            skus = ', '.join(item.get('skus', {}).keys())
            ordenes_str = ', '.join(item.get('ordenes', []))
            print(f"{idx:<4} {item['fila']:<6} {item['col']:<6} {item['cantidad']:<6} {skus:<20} {ordenes_str:<20}")
        
    except Exception as e:
        print(f"❌ Error: {e}")

# Ejemplo 2: Consolidar órdenes con items en la misma ubicación
def ejemplo_consolidacion_con_duplicados():
    print("\n" + "=" * 80)
    print("EJEMPLO 2: Consolidación con Items Duplicados (misma ubicación)")
    print("=" * 80)
    
    ordenes = [
        {
            'id_orden': 'ORD-LUNES-01',
            'items': [[1, 3, 5, 'TORNILLO-M6'], [2, 4, 3, 'TUERCA-M6']]
        },
        {
            'id_orden': 'ORD-LUNES-02',
            'items': [[1, 3, 2, 'TORNILLO-M6'], [2, 4, 4, 'TUERCA-M6']]
        },
        {
            'id_orden': 'ORD-MARTES-01',
            'items': [[1, 3, 1, 'TORNILLO-M6'], [5, 7, 10, 'ARANDELA']]
        }
    ]
    
    payload = {'ordenes': ordenes}
    
    try:
        response = requests.post(f'{API_BASE}/consolidate', json=payload)
        result = response.json()
        
        print("\n✓ Consolidación realizada")
        picking_list = result.get('picking_list', [])
        
        print(f"\nRESULTADO: {len(picking_list)} ubicaciones únicas")
        for item in picking_list:
            col_label = "PASILLO" if item['col'] in [1, 4, 7, 10] else "ALMACÉN"
            print(f"  ({item['fila']},{item['col']}) [{col_label}] - "
                  f"{item['cantidad']} unidades de {list(item['skus'].keys())} "
                  f"(Órdenes: {', '.join(item['ordenes'])})")
        
    except Exception as e:
        print(f"❌ Error: {e}")

# Ejemplo 3: Comparar distancia con y sin consolidación
def ejemplo_comparacion_distancia():
    print("\n" + "=" * 80)
    print("EJEMPLO 3: Comparación de Distancia (con vs sin consolidación)")
    print("=" * 80)
    
    # Generar órdenes sin consolidar
    ordenes = [
        {'id_orden': f'ORD-{i:03d}', 'items': [[i % 9, i % 12, 1, f'SKU-{i}']]}
        for i in range(1, 16)
    ]
    
    payload = {'ordenes': ordenes}
    
    try:
        response = requests.post(f'{API_BASE}/consolidate', json=payload)
        result = response.json()
        
        stats = result.get('estadisticas', {})
        picking_list = result.get('picking_list', [])
        
        # Simulación simple: sin consolidación cada orden tendría distancia similar
        distancia_sin_consolidar = len(ordenes) * 10  # Estimación burda
        distancia_consolidada = stats.get('distancia_estimada', 0)
        
        print(f"\nSin consolidación: ~{distancia_sin_consolidar} unidades (estimado)")
        print(f"Con consolidación: {distancia_consolidada} unidades")
        print(f"Ahorro: ~{distancia_sin_consolidar - distancia_consolidada} unidades "
              f"({100 * (distancia_sin_consolidar - distancia_consolidada) / distancia_sin_consolidar:.1f}%)")
        
        print(f"\nUbicaciones a visitar: {len(picking_list)}")
        print(f"Columnas en orden: {stats.get('columnas_visitadas')}")
        
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == '__main__':
    print("\n🏭 EJEMPLOS DE CONSOLIDACIÓN DE PICKING\n")
    
    # Asegúrate de que el backend esté corriendo en 127.0.0.1:5000
    try:
        response = requests.get(f'{API_BASE}/defaults')
        if response.status_code == 200:
            print("✓ Backend conectado en 127.0.0.1:5000\n")
        else:
            print("❌ Backend no responde correctamente")
            exit(1)
    except requests.exceptions.ConnectionError:
        print("❌ No se puede conectar al backend en 127.0.0.1:5000")
        print("   Por favor, inicia el backend con:")
        print("   python -m uvicorn backend.app:app --reload --host 127.0.0.1 --port 5000")
        exit(1)
    
    ejemplo_consolidacion_simple()
    ejemplo_consolidacion_con_duplicados()
    ejemplo_comparacion_distancia()
    
    print("\n" + "=" * 80)
    print("✓ Ejemplos completados\n")
