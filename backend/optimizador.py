import itertools
from .config import FILAS, PASILLOS


class Optimizador:
    """
    Optimizador mejorado que usa múltiples estrategias:
    1. Permutaciones completas para conjuntos pequeños (<= 8 columnas)
    2. Algoritmo greedy mejorado para conjuntos grandes
    3. Vecino más cercano con look-ahead
    4. Optimización 2-opt para refinar rutas
    """
    
    def __init__(self, costo_celda, costo_pasillo):
        self.costo_celda = float(costo_celda)
        self.costo_pasillo = float(costo_pasillo)

    def calcular_costo_movimiento(self, fila1, col1, fila2, col2):
        """Calcula el costo de moverse de una posición a otra"""
        costo = 0
        
        # Costo vertical
        pasos_verticales = abs(fila2 - fila1)
        costo += pasos_verticales * self.costo_celda
        
        # Costo horizontal (considerando pasillos)
        for c in range(min(col1, col2), max(col1, col2)):
            if (c + 1) in PASILLOS:
                costo += self.costo_pasillo
            else:
                costo += self.costo_celda
                
        return costo

    def optimizar_orden_columnas(self, paquetes, inicio):
        """
        Determina el orden óptimo para visitar las columnas.
        Usa fuerza bruta para <= 8 columnas, algoritmos heurísticos para más.
        """
        columnas_unicas = sorted(set(col for fila, col in paquetes))
        
        if len(columnas_unicas) <= 1:
            return columnas_unicas
        
        # Para 8 o menos columnas: fuerza bruta (8! = 40,320 permutaciones)
        if len(columnas_unicas) <= 8:
            return self._optimizar_fuerza_bruta(paquetes, inicio, columnas_unicas)
        
        # Para más columnas: combinación de estrategias
        return self._optimizar_hibrido(paquetes, inicio, columnas_unicas)

    def _optimizar_fuerza_bruta(self, paquetes, inicio, columnas):
        """Prueba todas las permutaciones posibles (óptimo garantizado)"""
        mejor_costo = float('inf')
        mejor_orden = columnas
        
        for perm in itertools.permutations(columnas):
            costo = self._calcular_costo_orden(list(perm), paquetes, inicio)
            if costo < mejor_costo:
                mejor_costo = costo
                mejor_orden = list(perm)
        
        return mejor_orden

    def _optimizar_hibrido(self, paquetes, inicio, columnas):
        """
        Para muchas columnas: combina nearest neighbor + 2-opt
        """
        # 1. Generar solución inicial con nearest neighbor mejorado
        solucion_nn = self._nearest_neighbor_mejorado(paquetes, inicio, columnas)
        
        # 2. Refinar con 2-opt
        solucion_2opt = self._optimizar_2opt(solucion_nn, paquetes, inicio)
        
        # 3. También probar greedy básico y quedarse con la mejor
        solucion_greedy = self._optimizar_greedy_mejorado(paquetes, inicio, columnas)
        
        costo_2opt = self._calcular_costo_orden(solucion_2opt, paquetes, inicio)
        costo_greedy = self._calcular_costo_orden(solucion_greedy, paquetes, inicio)
        
        return solucion_2opt if costo_2opt < costo_greedy else solucion_greedy

    def _nearest_neighbor_mejorado(self, paquetes, inicio, columnas):
        """
        Vecino más cercano con look-ahead de 2 pasos.
        """
        orden = []
        pos_actual = inicio[:]
        columnas_restantes = set(columnas)
        
        while columnas_restantes:
            if len(columnas_restantes) == 1:
                orden.append(columnas_restantes.pop())
                break
            
            mejor_col = None
            mejor_costo_total = float('inf')
            
            # Para cada columna candidata, evaluar también el siguiente paso
            for col in columnas_restantes:
                # Costo de ir a esta columna
                costo_actual = self._estimar_costo_visita_columna(
                    col, paquetes, pos_actual
                )
                
                # Look-ahead: evaluar el mejor siguiente paso
                temp_restantes = columnas_restantes - {col}
                if temp_restantes:
                    # Posición después de visitar esta columna
                    pos_temp = self._posicion_despues_columna(col, paquetes, pos_actual)
                    
                    # Encontrar el costo al vecino más cercano desde ahí
                    min_siguiente = min(
                        abs(pos_temp[1] - c) for c in temp_restantes
                    )
                    costo_total = costo_actual + min_siguiente * self.costo_celda
                else:
                    costo_total = costo_actual
                
                if costo_total < mejor_costo_total:
                    mejor_costo_total = costo_total
                    mejor_col = col
            
            orden.append(mejor_col)
            pos_actual = self._posicion_despues_columna(mejor_col, paquetes, pos_actual)
            columnas_restantes.remove(mejor_col)
        
        return orden

    def _optimizar_greedy_mejorado(self, paquetes, inicio, columnas):
        """
        Greedy que considera no solo distancia sino también densidad de paquetes.
        """
        orden = []
        pos_actual = inicio[:]
        columnas_restantes = set(columnas)
        
        # Calcular densidad de paquetes por columna
        densidad = {}
        for col in columnas:
            paquetes_col = [p for p in paquetes if p[1] == col]
            densidad[col] = len(paquetes_col)
        
        while columnas_restantes:
            mejor_col = None
            mejor_score = float('inf')
            
            for col in columnas_restantes:
                # Distancia horizontal
                dist = abs(pos_actual[1] - col)
                
                # Penalizar pasillos en el camino
                pasillos_en_camino = sum(
                    1 for c in range(min(pos_actual[1], col), max(pos_actual[1], col))
                    if (c + 1) in PASILLOS
                )
                
                # Score: distancia + penalización de pasillos - bonus por densidad
                score = (
                    dist * self.costo_celda +
                    pasillos_en_camino * (self.costo_pasillo - self.costo_celda) -
                    densidad[col] * 0.5  # Bonus por recoger más paquetes
                )
                
                if score < mejor_score:
                    mejor_score = score
                    mejor_col = col
            
            orden.append(mejor_col)
            pos_actual[1] = mejor_col
            columnas_restantes.remove(mejor_col)
        
        return orden

    def _optimizar_2opt(self, orden, paquetes, inicio, max_iteraciones=100):
        """
        Optimización 2-opt: intercambia pares de segmentos para mejorar la ruta.
        """
        mejor_orden = orden[:]
        mejor_costo = self._calcular_costo_orden(mejor_orden, paquetes, inicio)
        mejora = True
        iteracion = 0
        
        while mejora and iteracion < max_iteraciones:
            mejora = False
            iteracion += 1
            
            for i in range(1, len(mejor_orden) - 1):
                for j in range(i + 1, len(mejor_orden)):
                    # Crear nuevo orden invirtiendo el segmento [i:j]
                    nuevo_orden = mejor_orden[:i] + mejor_orden[i:j][::-1] + mejor_orden[j:]
                    nuevo_costo = self._calcular_costo_orden(nuevo_orden, paquetes, inicio)
                    
                    if nuevo_costo < mejor_costo:
                        mejor_orden = nuevo_orden
                        mejor_costo = nuevo_costo
                        mejora = True
                        break
                
                if mejora:
                    break
        
        return mejor_orden

    def _calcular_costo_orden(self, orden_columnas, paquetes, inicio):
        """Calcula el costo total de un orden específico de columnas"""
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
            
            # Determinar mejor punto de entrada
            dist_arriba = abs(pos_actual[0] - 0) + abs(0 - filas[0])
            dist_abajo = abs(pos_actual[0] - (FILAS - 1)) + abs((FILAS - 1) - filas[-1])
            
            if dist_arriba <= dist_abajo:
                entrada = 0
                salida = FILAS - 1
            else:
                entrada = FILAS - 1
                salida = 0
            
            # Costo horizontal hacia la columna
            costo += self.calcular_costo_movimiento(pos_actual[0], pos_actual[1], pos_actual[0], col)
            pos_actual[1] = col
            
            # Costo de entrar a la columna
            costo += self.calcular_costo_movimiento(pos_actual[0], col, entrada, col)
            pos_actual[0] = entrada
            
            # Costo de recorrer la columna
            costo += self.calcular_costo_movimiento(pos_actual[0], col, salida, col)
            pos_actual[0] = salida
        
        return costo

    def _estimar_costo_visita_columna(self, col, paquetes, pos_actual):
        """Estima el costo de visitar una columna desde la posición actual"""
        paquetes_col = [p[0] for p in paquetes if p[1] == col]
        if not paquetes_col:
            return abs(pos_actual[1] - col) * self.costo_celda
        
        paquetes_col.sort()
        
        # Costo horizontal
        costo = abs(pos_actual[1] - col) * self.costo_celda
        
        # Costo vertical (aproximado como el recorrido completo)
        costo += FILAS * self.costo_celda
        
        return costo

    def _posicion_despues_columna(self, col, paquetes, pos_actual):
        """Estima la posición después de visitar una columna"""
        paquetes_col = [p[0] for p in paquetes if p[1] == col]
        if not paquetes_col:
            return [pos_actual[0], col]
        
        paquetes_col.sort()
        
        # Determinar punto de salida
        dist_arriba = abs(pos_actual[0] - 0) + abs(0 - paquetes_col[0])
        dist_abajo = abs(pos_actual[0] - (FILAS - 1)) + abs((FILAS - 1) - paquetes_col[-1])
        
        salida = FILAS - 1 if dist_arriba <= dist_abajo else 0
        
        return [salida, col]

    def _optimizar_greedy(self, paquetes, inicio):
        """Método greedy básico (mantenido por compatibilidad)"""
        return self._optimizar_greedy_mejorado(paquetes, inicio, sorted(set(col for _, col in paquetes)))