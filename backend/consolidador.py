"""
Módulo consolidador: Recibe múltiples órdenes de pedido y genera una lista
de picking consolidada y optimizada minimizando distancia de recorrido.
"""

from .config import FILAS, COLUMNAS, PASILLOS


class ConsolidadorPicking:
    """Consolida múltiples órdenes en una ruta de picking optimizada"""

    def __init__(self):
        pass

    @staticmethod
    def consolidar_ordenes(ordenes):
        """
        Recibe múltiples órdenes y retorna lista consolidada y optimizada.
        
        Args:
            ordenes: list de dicts, cada uno con:
                {
                    'id_orden': str,
                    'items': [[fila, col, cantidad, sku], ...]
                }
        
        Returns:
            dict con:
                {
                    'picking_list': lista consolidada ordenada,
                    'rutas': rutas optimizadas por zona,
                    'estadisticas': stats de consolidación
                }
        """
        if not ordenes:
            return {
                'picking_list': [],
                'rutas': [],
                'estadisticas': {'total_items': 0, 'ordenes': 0, 'distancia_estimada': 0}
            }

        # 1. Consolidar todos los items de todas las órdenes
        items_consolidados = {}  # key: (fila, col), value: {sku: cantidad, ordenes: []}
        
        for orden in ordenes:
            orden_id = orden.get('id_orden', 'DESCONOCIDA')
            items = orden.get('items', [])
            
            for item in items:
                if len(item) < 3:
                    continue
                fila, col, cantidad = item[0], item[1], item[2]
                sku = item[3] if len(item) > 3 else f"SKU_{fila}_{col}"
                
                key = (fila, col)
                if key not in items_consolidados:
                    items_consolidados[key] = {'cantidad': 0, 'skus': {}, 'ordenes': set()}
                
                items_consolidados[key]['cantidad'] += cantidad
                items_consolidados[key]['skus'][sku] = items_consolidados[key]['skus'].get(sku, 0) + cantidad
                items_consolidados[key]['ordenes'].add(orden_id)

        # 2. Agrupar por columna para recorrido eficiente
        por_columna = {}
        for (fila, col), data in items_consolidados.items():
            if col not in por_columna:
                por_columna[col] = []
            por_columna[col].append({
                'fila': fila,
                'col': col,
                'cantidad': data['cantidad'],
                'skus': data['skus'],
                'ordenes': list(data['ordenes'])
            })

        # 3. Ordenar dentro de cada columna (de arriba a abajo o abajo a arriba)
        for col in por_columna:
            por_columna[col].sort(key=lambda x: x['fila'])

        # 4. Crear picking list ordenada (recorrido por columnas)
        picking_list = []
        columnas_ordenadas = sorted(por_columna.keys())
        
        for col in columnas_ordenadas:
            for item in por_columna[col]:
                picking_list.append(item)

        # 5. Calcular estadísticas
        total_items = sum(item['cantidad'] for item in picking_list)
        distancia_estimada = ConsolidadorPicking._calcular_distancia(picking_list)

        return {
            'picking_list': picking_list,
            'rutas': columnas_ordenadas,
            'estadisticas': {
                'total_items': total_items,
                'ordenes': len(ordenes),
                'ubicaciones_unicas': len(items_consolidados),
                'distancia_estimada': round(distancia_estimada, 2),
                'columnas_visitadas': columnas_ordenadas
            }
        }

    @staticmethod
    def _calcular_distancia(picking_list):
        """Calcula distancia aproximada del recorrido"""
        if not picking_list:
            return 0
        
        distancia = 0
        pos_actual = (0, 0)  # Inicio
        
        for item in picking_list:
            nueva_pos = (item['fila'], item['col'])
            # Manhattan distance
            distancia += abs(nueva_pos[0] - pos_actual[0]) + abs(nueva_pos[1] - pos_actual[1])
            pos_actual = nueva_pos
        
        return distancia

    @staticmethod
    def optimizar_picking(items_ubicaciones):
        """
        Versión mejorada: recibe items y retorna ruta optimizada
        usando agrupación por zonas.
        
        Args:
            items_ubicaciones: list de [fila, col, cantidad, sku]
        
        Returns:
            list ordenada optimizada
        """
        if not items_ubicaciones:
            return []

        # Agrupar por zona (columna como proxy)
        zonas = {}
        for item in items_ubicaciones:
            fila, col = item[0], item[1]
            zona = col // 3  # Dividir en 3 zonas (ajustable)
            
            if zona not in zonas:
                zonas[zona] = []
            zonas[zona].append(item)

        # Ordenar cada zona
        resultado = []
        for zona_id in sorted(zonas.keys()):
            zona_items = zonas[zona_id]
            zona_items.sort(key=lambda x: x[0])  # Ordenar por fila
            resultado.extend(zona_items)

        return resultado

    @staticmethod
    def generar_lista_picking_texto(picking_list):
        """Genera una representación en texto de la lista de picking"""
        if not picking_list:
            return "Lista vacía"
        
        texto = "═" * 80 + "\n"
        texto += "LISTA DE PICKING CONSOLIDADA\n"
        texto += "═" * 80 + "\n"
        texto += f"{'#':<4} {'FILA':<6} {'COL':<6} {'CANT':<6} {'SKUs':<20} {'ÓRDENES':<20}\n"
        texto += "─" * 80 + "\n"
        
        for idx, item in enumerate(picking_list, 1):
            fila = item.get('fila', '?')
            col = item.get('col', '?')
            cantidad = item.get('cantidad', 0)
            skus = ', '.join(item.get('skus', {}).keys()) if item.get('skus') else 'N/A'
            ordenes = ', '.join(item.get('ordenes', []))[:15]
            
            texto += f"{idx:<4} {fila:<6} {col:<6} {cantidad:<6} {skus:<20} {ordenes:<20}\n"
        
        texto += "═" * 80 + "\n"
        return texto
