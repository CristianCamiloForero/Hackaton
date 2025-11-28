from .config import PASILLOS

TRANSITIONS = {0, 8}

class Optimizador:
    """
    Optimizador que respeta las restricciones de movimiento del almacén.
    - Los movimientos se descomponen en Vertical y Horizontal.
    - Los movimientos horizontales que cruzan pasillos deben pasar por columnas de transición.
    - El orden de las columnas se determina de forma secuencial.
    """

    def __init__(self, costo_celda, costo_pasillo):
        self.costo_celda = float(costo_celda)
        self.costo_pasillo = float(costo_pasillo)

    def _costo_horizontal_simple(self, col1, col2):
        """Calcula costo y pasos para un movimiento horizontal directo (sin desvíos)."""
        pasos = abs(col1 - col2)
        costo = 0
        
        # El costo se aplica al movernos a la siguiente columna
        for c in range(min(col1, col2), max(col1, col2)):
            costo += self.costo_pasillo if (c + 1) in PASILLOS else self.costo_celda
            
        return pasos, costo

    def calcular_costo_movimiento(self, fila1, col1, fila2, col2):
        """
        Calcula el costo y pasos de moverse de una posición a otra, respetando TODAS las restricciones.
        1. Movimientos se descomponen en Vertical y Horizontal (estilo V-H).
        2. Movimientos horizontales que cruzan pasillos deben pasar por columnas de transición (0 u 8).
        """
        
        # 1. Costo del movimiento vertical (siempre es directo)
        pasos_verticales = abs(fila2 - fila1)
        costo_vertical = pasos_verticales * self.costo_celda

        # 2. Costo del movimiento horizontal
        pasos_horizontales = 0
        costo_horizontal = 0

        if col1 != col2:
            left, right = min(col1, col2), max(col1, col2)
            # Un cruce ocurre si un pasillo está ESTRICTAMENTE entre las dos columnas
            cruza_pasillo = any(p in PASILLOS for p in range(left + 1, right))
            
            # Si el movimiento horizontal cruza un pasillo y no empieza/termina en una transición,
            # se debe desviar por la columna de transición más cercana/barata.
            if cruza_pasillo and col1 not in TRANSITIONS and col2 not in TRANSITIONS:
                # Calcular costo vía columna 0
                pasos_a_0, costo_a_0 = self._costo_horizontal_simple(col1, 0)
                pasos_de_0, costo_de_0 = self._costo_horizontal_simple(0, col2)
                pasos_via_0 = pasos_a_0 + pasos_de_0
                costo_via_0 = costo_a_0 + costo_de_0

                # Calcular costo vía columna 8
                pasos_a_8, costo_a_8 = self._costo_horizontal_simple(col1, 8)
                pasos_de_8, costo_de_8 = self._costo_horizontal_simple(8, col2)
                pasos_via_8 = pasos_a_8 + pasos_de_8
                costo_via_8 = costo_a_8 + costo_de_8

                # Elegir la ruta de transición más barata
                if costo_via_0 <= costo_via_8:
                    pasos_horizontales = pasos_via_0
                    costo_horizontal = costo_via_0
                else:
                    pasos_horizontales = pasos_via_8
                    costo_horizontal = costo_via_8
            else:
                # Movimiento horizontal directo (no cruza pasillos o ya está en transición)
                pasos_horizontales, costo_horizontal = self._costo_horizontal_simple(col1, col2)

        total_pasos = pasos_verticales + pasos_horizontales
        total_costo = costo_vertical + costo_horizontal
        
        return total_pasos, total_costo

    def optimizar_orden_columnas(self, paquetes, inicio):
        """
        ALGORITMO SECUENCIAL: Visitar solo columnas con paquetes, en orden ascendente.
        """
        if not paquetes:
            return []
        
        columnas_con_paquetes = sorted(list(set(col for _, col in paquetes)))
        return columnas_con_paquetes

    def calcular_costo_con_restriccion(self, pos_actual, col_destino, filas_destino):
        """
        Calcula el costo de visitar una columna, recoger todos los paquetes y salir.
        Determina el punto de entrada y salida óptimo para esa columna.
        """
        fila_actual, col_actual = pos_actual
        filas_ordenadas = sorted(filas_destino)
        
        # Posibles puntos de entrada/salida: el primer y último paquete de la columna
        entrada_arriba, salida_abajo = filas_ordenadas[0], filas_ordenadas[-1]
        entrada_abajo, salida_arriba = filas_ordenadas[-1], filas_ordenadas[0]
        
        # Calcular costo de la estrategia "entrar por arriba, salir por abajo"
        _, costo_ida_arriba = self.calcular_costo_movimiento(fila_actual, col_actual, entrada_arriba, col_destino)
        recorrido_columna = abs(salida_abajo - entrada_arriba)
        costo_total_arriba = costo_ida_arriba + (recorrido_columna * self.costo_celda)

        # Calcular costo de la estrategia "entrar por abajo, salir por arriba"
        _, costo_ida_abajo = self.calcular_costo_movimiento(fila_actual, col_actual, entrada_abajo, col_destino)
        costo_total_abajo = costo_ida_abajo + (recorrido_columna * self.costo_celda)
        
        # Elegir la estrategia más barata
        if costo_total_arriba <= costo_total_abajo:
            return {'entrada': entrada_arriba, 'salida': salida_abajo}
        else:
            return {'entrada': entrada_abajo, 'salida': salida_arriba}

    def calcular_ruta_optima_salida(self, pos_final, punto_entrega):
        """
        Calcula el costo hacia el punto de entrega y devuelve una ruta placeholder.
        El robot se encargará de descomponer el movimiento final.
        """
        fila_actual, col_actual = pos_final
        fila_entrega, col_entrega = punto_entrega
        
        _, costo = self.calcular_costo_movimiento(
            fila_actual, col_actual, fila_entrega, col_entrega
        )
        
        # La ruta solo necesita el punto final; el robot la construirá
        ruta = [(fila_entrega, col_entrega)]
        
        return ruta, costo
