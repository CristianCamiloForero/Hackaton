from .config import FILAS, COLUMNAS, PASILLOS


class Optimizador:
    """
    Optimizador SIMPLIFICADO siguiendo el algoritmo original:
    - Recorrer columna por columna secuencialmente (0 a 11)
    - Si la columna tiene paquetes, recogerlos todos
    - Si está vacía, pasar a la siguiente
    - Respetar costos de pasillos (5) vs celdas normales (2.7)
    """
    
    def __init__(self, costo_celda, costo_pasillo):
        self.costo_celda = float(costo_celda)
        self.costo_pasillo = float(costo_pasillo)

    def calcular_costo_movimiento(self, fila1, col1, fila2, col2):
        """
        Calcula el costo y pasos de moverse de una posición a otra.
        Respeta restricción: cambiar de zona SOLO por columnas 0 u 8.
        """
        pasos = 0
        costo = 0
        
        # Si estamos en la misma columna, solo movimiento vertical
        if col1 == col2:
            pasos_verticales = abs(fila2 - fila1)
            costo = pasos_verticales * self.costo_celda
            return pasos_verticales, costo
        
        # Si están en el MISMO LADO del almacén, movimiento horizontal directo
        # Lado izquierdo: columnas 0-3, Lado derecho: columnas 9-11, Centro: 4-8
        def get_zona(col):
            if col < 4:
                return 'izq'
            elif col <= 8:
                return 'centro'
            else:
                return 'der'
        
        zona1 = get_zona(col1)
        zona2 = get_zona(col2)
        
        # Caso 1: Misma zona, movimiento horizontal directo
        if zona1 == zona2:
            # Movimiento vertical primero
            pasos_verticales = abs(fila2 - fila1)
            costo += pasos_verticales * self.costo_celda
            pasos += pasos_verticales
            
            # Movimiento horizontal
            for c in range(min(col1, col2), max(col1, col2)):
                if (c + 1) in PASILLOS:
                    costo += self.costo_pasillo
                else:
                    costo += self.costo_celda
                pasos += 1
            return pasos, costo
        
        # Caso 2: Diferentes zonas, pasar por columna 0 u 8 (elegir la más económica)
        # Primero movimiento vertical a fila destino
        pasos_verticales = abs(fila2 - fila1)
        costo += pasos_verticales * self.costo_celda
        pasos += pasos_verticales
        
        # Detectar si necesitamos pasar por 0 u 8
        if zona1 == 'izq' and zona2 == 'der':
            # Pasar por 0 o 8, evaluamos ambas
            costo_por_0 = self._costo_paso_horizontal(col1, col2, fila1, 0, fila2)
            costo_por_8 = self._costo_paso_horizontal(col1, col2, fila1, 8, fila2)
            pasos_por_0 = abs(col1 - 0) + abs(0 - col2)
            pasos_por_8 = abs(col1 - 8) + abs(8 - col2)
            
            if costo_por_0 <= costo_por_8:
                pasos += pasos_por_0
                costo += costo_por_0
            else:
                pasos += pasos_por_8
                costo += costo_por_8
        elif zona1 == 'der' and zona2 == 'izq':
            # Pasar por 8 o 0, evaluamos ambas
            costo_por_0 = self._costo_paso_horizontal(col1, col2, fila1, 0, fila2)
            costo_por_8 = self._costo_paso_horizontal(col1, col2, fila1, 8, fila2)
            pasos_por_0 = abs(col1 - 0) + abs(0 - col2)
            pasos_por_8 = abs(col1 - 8) + abs(8 - col2)
            
            if costo_por_0 <= costo_por_8:
                pasos += pasos_por_0
                costo += costo_por_0
            else:
                pasos += pasos_por_8
                costo += costo_por_8
        else:
            # Centro a lado: pasar por columna más cercana (0 u 8)
            pasos_por_0 = abs(col1 - 0) + abs(0 - col2)
            pasos_por_8 = abs(col1 - 8) + abs(8 - col2)
            
            if pasos_por_0 <= pasos_por_8:
                costo += self._costo_paso_horizontal(col1, col2, fila1, 0, fila2)
                pasos += pasos_por_0
            else:
                costo += self._costo_paso_horizontal(col1, col2, fila1, 8, fila2)
                pasos += pasos_por_8
        
        return pasos, costo
    
    def _costo_paso_horizontal(self, col_origen, col_destino, fila_origen, col_transicion, fila_destino):
        """Calcula costo de pasar horizontalmente por una columna de transición."""
        costo = 0
        
        # De origen a transición
        for c in range(min(col_origen, col_transicion), max(col_origen, col_transicion)):
            if (c + 1) in PASILLOS:
                costo += self.costo_pasillo
            else:
                costo += self.costo_celda
        
        # De transición a destino
        for c in range(min(col_transicion, col_destino), max(col_transicion, col_destino)):
            if (c + 1) in PASILLOS:
                costo += self.costo_pasillo
            else:
                costo += self.costo_celda
        
        return costo

    def optimizar_orden_columnas(self, paquetes, inicio):
        """
        ALGORITMO SECUENCIAL: Visitar solo columnas con paquetes, en orden.
        No hay saltos, no hay zigzag.
        """
        if not paquetes:
            return []
        
        # Agrupar paquetes por columna
        paquetes_por_columna = {}
        for fila, col in paquetes:
            if col not in paquetes_por_columna:
                paquetes_por_columna[col] = []
            paquetes_por_columna[col].append(fila)
        
        # Ordenar filas dentro de cada columna
        for col in paquetes_por_columna:
            paquetes_por_columna[col] = sorted(paquetes_por_columna[col])
        
        # Retornar columnas en orden secuencial
        return sorted(paquetes_por_columna.keys())

    def calcular_costo_con_restriccion(self, pos_actual, col_destino, filas_destino):
        """
        Calcula el costo de visitar una columna con paquetes.
        SIMPLIFICADO: Ir a la columna, recoger todos, salir.
        """
        fila_actual, col_actual = pos_actual
        
        filas_ordenadas = sorted(filas_destino)
        
        # Estrategia: entrar por el paquete más cercano
        paquete_mas_cercano = min(filas_ordenadas, key=lambda f: abs(f - fila_actual))
        
        # Decidir dirección basada en proximidad
        if paquete_mas_cercano <= fila_actual:
            entrada = paquete_mas_cercano
            salida = max(filas_ordenadas)
        else:
            entrada = paquete_mas_cercano
            salida = min(filas_ordenadas)
        
        # Costo total
        pasos_entrada, costo_entrada = self.calcular_costo_movimiento(
            fila_actual, col_actual, entrada, col_destino
        )
        
        pasos_columna, costo_columna = self._procesar_columna(
            entrada, col_destino, filas_destino, salida
        )
        
        costo_total = costo_entrada + costo_columna
        pasos_total = pasos_entrada + pasos_columna
        
        return {
            'costo': costo_total,
            'pasos': pasos_total,
            'entrada': entrada,
            'salida': salida,
        }

    def _procesar_columna(self, fila_entrada, col, filas_paquetes, fila_salida):
        """
        Procesa todos los paquetes en una columna.
        Recorre en orden secuencial (arriba a abajo o abajo a arriba).
        """
        pasos_total = 0
        costo_total = 0
        fila_actual = fila_entrada
        
        filas_ordenadas = sorted(filas_paquetes)
        
        # Recorrer en orden
        if fila_entrada <= filas_ordenadas[0]:
            # De arriba hacia abajo
            for fila_paq in filas_ordenadas:
                pasos, costo = self.calcular_costo_movimiento(
                    fila_actual, col, fila_paq, col
                )
                pasos_total += pasos
                costo_total += costo
                fila_actual = fila_paq
        else:
            # De abajo hacia arriba
            for fila_paq in reversed(filas_ordenadas):
                pasos, costo = self.calcular_costo_movimiento(
                    fila_actual, col, fila_paq, col
                )
                pasos_total += pasos
                costo_total += costo
                fila_actual = fila_paq
        
        # Ir a punto de salida
        pasos_salida, costo_salida = self.calcular_costo_movimiento(
            fila_actual, col, fila_salida, col
        )
        pasos_total += pasos_salida
        costo_total += costo_salida
        
        return pasos_total, costo_total

    def calcular_ruta_optima_salida(self, pos_final, punto_entrega):
        """Calcula la ruta hacia el punto de entrega."""
        fila_actual, col_actual = pos_final
        fila_entrega, col_entrega = punto_entrega
        
        pasos, costo = self.calcular_costo_movimiento(
            fila_actual, col_actual, fila_entrega, col_entrega
        )
        
        ruta = [(fila_entrega, col_entrega)]
        
        return ruta, costo
