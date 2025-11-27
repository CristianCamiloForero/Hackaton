from datetime import date, timedelta
import math

from .config import get_almacen_by_column


class ConteoCiclico:
    """Generador de planes de conteo cíclico.

    Entradas esperadas:
      - ubicaciones: lista de dicts con claves: 'fila', 'col', 'sku'
          opcionales: 'movimientos' (int), 'conteos_ultimos_365dias' (int)
      - frecuencia_minima: cuántas veces por año debe contarse cada referencia

    Salida:
      - lista priorizada con fechas planificadas (ISO) para los conteos necesarios
    """

    def __init__(self, frecuencia_minima: int = 5, periodo_dias: int = 365, weights: dict = None, zone_weights: dict = None):
        self.frecuencia_minima = int(frecuencia_minima)
        self.periodo_dias = int(periodo_dias)
        # Weights for scoring: keys: 'faltantes', 'movimientos', 'criticidad'
        self.weights = weights or {'faltantes': 100, 'movimientos': 1, 'criticidad': 50}
        # Optional additional bonus per almacen (by nombre)
        self.zone_weights = zone_weights or {}

    def generar_plan(self, ubicaciones, historial=None):
        """Genera un plan priorizado de conteos.

        ubicaciones: list[dict]
        historial: no usado actualmente, reservado para futuras mejoras
        """
        hoy = date.today()

        # Enriquecer y calcular prioridad
        enriched = []
        for item in ubicaciones:
            sku = item.get('sku') or item.get('ref') or f"{item.get('fila')}-{item.get('col')}"
            movimientos = int(item.get('movimientos', 0) or 0)
            conteos_365 = int(item.get('conteos_ultimos_365dias', 0) or 0)
            criticidad = float(item.get('criticidad', 0) or 0)

            # Cuántos conteos faltan para llegar a la frecuencia mínima
            faltantes = max(0, self.frecuencia_minima - conteos_365)

            # Determinar zona (almacén) y posible bonus
            almacen = None
            zona_bonus = 0
            try:
                almacen = get_almacen_by_column(int(item.get('col'))) if item.get('col') is not None else None
                if almacen and almacen.get('nombre') in self.zone_weights:
                    zona_bonus = float(self.zone_weights.get(almacen.get('nombre'), 0) or 0)
            except Exception:
                almacen = None

            # Puntuación usando pesos configurables
            score = (
                faltantes * float(self.weights.get('faltantes', 100)) +
                movimientos * float(self.weights.get('movimientos', 1)) +
                criticidad * float(self.weights.get('criticidad', 50)) +
                zona_bonus
            )

            enriched.append({
                'sku': sku,
                'fila': item.get('fila'),
                'col': item.get('col'),
                'movimientos': movimientos,
                'conteos_ultimos_365dias': conteos_365,
                'faltantes': faltantes,
                'score': score,
            })

        # Ordenar por score descendente (más urgente primero), luego por sku
        enriched.sort(key=lambda x: (-x['score'], x['sku']))

        # Generar fechas de conteo para cada elemento
        plan = []
        total_counts_scheduled = 0
        for idx, it in enumerate(enriched):
            needed = it['faltantes']
            fechas = []
            if needed > 0:
                # repartir los conteos faltantes uniformemente en el periodo
                interval = max(1, math.floor(self.periodo_dias / needed))
                for k in range(needed):
                    planned_date = hoy + timedelta(days=k * interval)
                    fechas.append(planned_date.isoformat())
                total_counts_scheduled += needed
            else:
                # No necesita conteos extra: programamos un conteo de mantenimiento cada periodo (opcional)
                planned_date = hoy + timedelta(days=math.floor(self.periodo_dias / 2))
                fechas.append(planned_date.isoformat())

            plan.append({
                'sku': it['sku'],
                'fila': it['fila'],
                'col': it['col'],
                'conteos_ultimos_365dias': it['conteos_ultimos_365dias'],
                'faltantes': it['faltantes'],
                'score': it['score'],
                'fechas_planificadas': fechas
            })

        estadisticas = {
            'total_items': len(enriched),
            'items_con_faltantes': sum(1 for x in enriched if x['faltantes'] > 0),
            'total_counts_scheduled': total_counts_scheduled
        }

        return {
            'plan': plan,
            'estadisticas': estadisticas
        }


if __name__ == '__main__':
    # Ejemplo rápido
    ejemplo = [
        {'fila': 2, 'col': 0, 'sku': 'SKU-001', 'movimientos': 10, 'conteos_ultimos_365dias': 1},
        {'fila': 4, 'col': 3, 'sku': 'SKU-002', 'movimientos': 2, 'conteos_ultimos_365dias': 5},
        {'fila': 1, 'col': 9, 'sku': 'SKU-003', 'movimientos': 20, 'conteos_ultimos_365dias': 0},
    ]
    cc = ConteoCiclico(frecuencia_minima=5)
    from pprint import pprint
    pprint(cc.generar_plan(ejemplo))
