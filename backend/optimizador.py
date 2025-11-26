import itertools
from .config import FILAS, PASILLOS


class Optimizador:
    def __init__(self, costo_celda, costo_pasillo):
        self.costo_celda = float(costo_celda)
        self.costo_pasillo = float(costo_pasillo)

    def calcular_costo_movimiento(self, fila1, col1, fila2, col2):
        costo = 0
        pasos_verticales = abs(fila2 - fila1)
        costo += pasos_verticales * self.costo_celda
        for c in range(min(col1, col2), max(col1, col2)):
            if (c + 1) in PASILLOS:
                costo += self.costo_pasillo
            else:
                costo += self.costo_celda
        return costo

    # Mantengo los métodos principales, por si se quieren usar desde el backend
    def optimizar_orden_columnas(self, paquetes, inicio):
        columnas_unicas = sorted(set(col for fila, col in paquetes))
        if len(columnas_unicas) <= 1:
            return columnas_unicas
        if len(columnas_unicas) > 8:
            return self._optimizar_greedy(paquetes, inicio)
        mejor_costo = float('inf')
        mejor_orden = columnas_unicas
        for perm in itertools.permutations(columnas_unicas):
            costo = self._calcular_costo_orden(list(perm), paquetes, inicio)
            if costo < mejor_costo:
                mejor_costo = costo
                mejor_orden = list(perm)
        return mejor_orden

    def _calcular_costo_orden(self, orden_columnas, paquetes, inicio):
        paquetes_por_columna = {}
        for fila, col in paquetes:
            if col not in paquetes_por_columna:
                paquetes_por_columna[col] = []
            paquetes_por_columna[col].append(fila)
        for col in paquetes_por_columna:
            paquetes_por_columna[col].sort()
        costo = 0
        pos_actual = inicio[:]
        for col in orden_columnas:
            filas = paquetes_por_columna.get(col, [])
            if not filas:
                continue
            dist_arriba = abs(pos_actual[0] - 0) + abs(0 - filas[0])
            dist_abajo = abs(pos_actual[0] - (FILAS-1)) + abs((FILAS-1) - filas[-1])
            if dist_arriba <= dist_abajo:
                entrada = 0
                salida = FILAS - 1
            else:
                entrada = FILAS - 1
                salida = 0
            costo += self.calcular_costo_movimiento(pos_actual[0], pos_actual[1], pos_actual[0], col)
            pos_actual[1] = col
            costo += self.calcular_costo_movimiento(pos_actual[0], col, entrada, col)
            pos_actual[0] = entrada
            costo += self.calcular_costo_movimiento(pos_actual[0], col, salida, col)
            pos_actual[0] = salida
        return costo

    def _optimizar_greedy(self, paquetes, inicio):
        columnas_unicas = sorted(set(col for fila, col in paquetes))
        orden = []
        pos_actual = inicio[:]
        columnas_restantes = set(columnas_unicas)
        while columnas_restantes:
            mejor_col = None
            mejor_costo = float('inf')
            for col in columnas_restantes:
                costo = abs(pos_actual[1] - col)
                if costo < mejor_costo:
                    mejor_costo = costo
                    mejor_col = col
            orden.append(mejor_col)
            pos_actual[1] = mejor_col
            columnas_restantes.remove(mejor_col)
        return orden
