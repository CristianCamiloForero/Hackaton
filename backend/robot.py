from .config import FILAS, COLUMNAS, PASILLOS, PAQUETES, INICIO, FINAL, COSTO_CELDA, COSTO_PASILLO
from .optimizador import Optimizador


class RobotAlmacen:
    """
    Robot recolector optimizado con restricciones de movimiento.
    Solo puede cambiar de columna pasando por columnas 0 u 8.
    """

    def __init__(self, paquetes=None, inicio=None, costo_celda=None, costo_pasillo=None):
        if paquetes is None:
            paquetes = PAQUETES
        if inicio is None:
            inicio = INICIO
        if costo_celda is None:
            costo_celda = COSTO_CELDA
        if costo_pasillo is None:
            costo_pasillo = COSTO_PASILLO

        self.paquetes = paquetes
        self.inicio = inicio
        self.costo_celda_valor = float(costo_celda)
        self.costo_pasillo_valor = float(costo_pasillo)

        # Matriz del almacén
        self.matriz = [["" for _ in range(COLUMNAS)] for _ in range(FILAS)]
        self.fila_actual = inicio[0]
        self.col_actual = inicio[1]
        self.costo_total = 0
        self.pasos = []
        self.ruta = [(self.fila_actual, self.col_actual)]

        # Optimizador con restricciones
        self.optimizador = Optimizador(costo_celda, costo_pasillo)

        self._inicializar_matriz()
        self._organizar_paquetes()

    def _inicializar_matriz(self):
        for i in range(FILAS):
            for j in range(COLUMNAS):
                self.matriz[i][j] = ""
        for paq in self.paquetes:
            fila, col = paq
            self.matriz[fila][col] = "X"

    def _organizar_paquetes(self):
        self.paquetes_por_columna = {}
        for paq in self.paquetes:
            fila, col = paq
            if col not in self.paquetes_por_columna:
                self.paquetes_por_columna[col] = []
            self.paquetes_por_columna[col].append(fila)
        for col in self.paquetes_por_columna:
            self.paquetes_por_columna[col].sort()

    def es_pasillo(self, col):
        return col in PASILLOS

    def calcular_distancia(self, fila1, col1, fila2, col2):
        """Calcula distancia y costo entre dos posiciones respetando restricciones de movimiento"""
        return self.optimizador.calcular_costo_movimiento(fila1, col1, fila2, col2)

    def mover_a(self, fila_dest, col_dest, descripcion):
        """Registra movimiento del robot (segmento simple A->B).

        Esta función NO inserta puntos de transición. Use
        `mover_respetando_restriccion` para movimientos que requieran
        pasar por columnas de transición (0 u 8).
        """
        # Si el movimiento es diagonal, o si es horizontal y cruzaría
        # columnas marcadas como PASILLOS sin empezar/terminar en una
        # columna de transición (0 u 8), delegamos a
        # mover_respetando_restriccion para descomponer el movimiento.
        if fila_dest != self.fila_actual and col_dest != self.col_actual:
            return self.mover_respetando_restriccion(fila_dest, col_dest, descripcion)

        # Movimiento horizontal (misma fila)
        if fila_dest == self.fila_actual and col_dest != self.col_actual:
            start = min(self.col_actual, col_dest)
            end = max(self.col_actual, col_dest)
            # columnas estrictamente entre start y end
            atraviesa_pasillo = any((c in PASILLOS) for c in range(start + 1, end))
            if atraviesa_pasillo and (self.col_actual not in (0, 8) and col_dest not in (0, 8)):
                return self.mover_respetando_restriccion(fila_dest, col_dest, descripcion)

        pasos, costo = self.calcular_distancia(
            self.fila_actual, self.col_actual, fila_dest, col_dest
        )

        # Registrar usando el helper directo (no delega a mover_respetando_restriccion)
        self._registrar_segmento(fila_dest, col_dest, pasos, costo, descripcion)

    def _registrar_segmento(self, fila_dest, col_dest, pasos, costo, descripcion):
        """Registra en `self.pasos`, actualiza costo acumulado y la `ruta`.

        Esta función permite que otras rutinas (p. ej. `mover_respetando_restriccion`)
        registren segmentos sin entrar en lógica de descomposición adicional.
        """
        # Forzar descomposición agresiva: si es un tramo HORIZONTAL que
        # atraviesa columnas marcadas en PASILLOS, y ninguno de los extremos
        # es una columna de transición (0 u 8), descomponemos vía 0 o 8.
        if self.fila_actual == fila_dest and self.col_actual != col_dest:
            left, right = min(self.col_actual, col_dest), max(self.col_actual, col_dest)
            crossed = [c for c in PASILLOS if left < c < right]
            if crossed and (self.col_actual not in (0, 8) and col_dest not in (0, 8)):
                # Elegir columna de transición (0 u 8) por menor paso estimado
                pasos_por_0 = abs(self.col_actual - 0) + abs(0 - col_dest)
                pasos_por_8 = abs(self.col_actual - 8) + abs(8 - col_dest)
                col_transicion = 0 if pasos_por_0 <= pasos_por_8 else 8

                # 1) Mover horizontalmente hasta la columna de transición
                pasos1, costo1 = self.calcular_distancia(self.fila_actual, self.col_actual, self.fila_actual, col_transicion)
                self.costo_total += costo1
                self.pasos.append({
                    'Desde': f"({self.fila_actual},{self.col_actual})",
                    'Hacia': f"({self.fila_actual},{col_transicion})",
                    'Pasos': pasos1,
                    'Costo': round(costo1, 2),
                    'Es Pasillo': "Sí" if self.es_pasillo(col_transicion) else "No",
                    'Acumulado': round(self.costo_total, 2),
                    'Descripción': f"Ir a pasillo {col_transicion}"
                })
                self.col_actual = col_transicion
                self.ruta.append((self.fila_actual, self.col_actual))

                # 2) (si fuera necesario) Mover verticalmente en pasillo a la misma fila destino
                # En este caso fila_actual == fila_dest, así que omitimos vertical

                # 3) Cruzar desde pasillo hasta columna destino
                pasos2, costo2 = self.calcular_distancia(self.fila_actual, self.col_actual, fila_dest, col_dest)
                self.costo_total += costo2
                self.pasos.append({
                    'Desde': f"({self.fila_actual},{self.col_actual})",
                    'Hacia': f"({fila_dest},{col_dest})",
                    'Pasos': pasos2,
                    'Costo': round(costo2, 2),
                    'Es Pasillo': "Sí" if self.es_pasillo(col_dest) else "No",
                    'Acumulado': round(self.costo_total, 2),
                    'Descripción': descripcion
                })
                self.fila_actual = fila_dest
                self.col_actual = col_dest
                self.ruta.append((fila_dest, col_dest))
                return

        # Caso por defecto: registrar el segmento tal cual
        self.costo_total += costo
        self.pasos.append({
            'Desde': f"({self.fila_actual},{self.col_actual})",
            'Hacia': f"({fila_dest},{col_dest})",
            'Pasos': pasos,
            'Costo': round(costo, 2),
            'Es Pasillo': "Sí" if self.es_pasillo(col_dest) else "No",
            'Acumulado': round(self.costo_total, 2),
            'Descripción': descripcion
        })

        # Registrar sólo el destino como punto clave
        self.fila_actual = fila_dest
        self.col_actual = col_dest
        self.ruta.append((fila_dest, col_dest))

    def mover_respetando_restriccion(self, fila_dest, col_dest, descripcion):
        """Mueve respetando la restricción de cambio de columna solo por pasillos.

        Descompone el movimiento en 1..n segmentos (horizontal/vertical)
        y llama a `mover_a` para cada segmento. Registra puntos clave
        (inicio/trasposición en pasillo/altura destino/destino).
        """
        def get_zona(col):
            if col < 4:
                return 'izq'
            elif col <= 8:
                return 'centro'
            else:
                return 'der'

        zona_origen = get_zona(self.col_actual)
        zona_dest = get_zona(col_dest)

        # Si misma zona o misma columna -> normalmente movimiento directo,
        # pero evitamos pasar por columnas catalogadas como PASILLOS
        if zona_origen == zona_dest or self.col_actual == col_dest:
            # Si el movimiento horizontal directo atraviesa una columna prohibida
            if self.col_actual != col_dest:
                start = min(self.col_actual, col_dest)
                end = max(self.col_actual, col_dest)
                # comprobar si alguna columna en el tramo está marcada como pasillo
                atraviesa_pasillo = any((c in PASILLOS) for c in range(start + 1, end + 1))
                if atraviesa_pasillo:
                    # Forzar cruce vía columna de transición (0 u 8)
                    pasos_por_0 = abs(self.col_actual - 0) + abs(0 - col_dest)
                    pasos_por_8 = abs(self.col_actual - 8) + abs(8 - col_dest)
                    col_transicion = 0 if pasos_por_0 <= pasos_por_8 else 8

                    if self.col_actual != col_transicion:
                        pasos, costo = self.calcular_distancia(self.fila_actual, self.col_actual, self.fila_actual, col_transicion)
                        self._registrar_segmento(self.fila_actual, col_transicion, pasos, costo, f"Ir a pasillo {col_transicion}")
                    if self.fila_actual != fila_dest:
                        pasos, costo = self.calcular_distancia(self.fila_actual, self.col_actual, fila_dest, self.col_actual)
                        self._registrar_segmento(fila_dest, col_transicion, pasos, costo, f"Desplazarse en pasillo {col_transicion} a fila {fila_dest}")
                    if col_transicion != col_dest:
                        pasos, costo = self.calcular_distancia(self.fila_actual, self.col_actual, fila_dest, col_dest)
                        self._registrar_segmento(fila_dest, col_dest, pasos, costo, descripcion)
                    return

            # Si no atraviesa pasillo, movimiento directo
            # Descomponer movimiento si es diagonal para evitar recursión
            if self.fila_actual != fila_dest and self.col_actual != col_dest:
                # Primero mover verticalmente hasta la fila destino (misma columna actual)
                pasos, costo = self.calcular_distancia(self.fila_actual, self.col_actual, fila_dest, self.col_actual)
                self._registrar_segmento(fila_dest, self.col_actual, pasos, costo, f"Vertical a fila {fila_dest}")

                # Después mover horizontalmente desde (fila_dest, col_actual) a (fila_dest, col_dest)
                start = min(self.col_actual, col_dest)
                end = max(self.col_actual, col_dest)
                atraviesa_pasillo_h = any((c in PASILLOS) for c in range(start + 1, end + 1))
                if atraviesa_pasillo_h and (self.col_actual not in (0, 8) and col_dest not in (0, 8)):
                    # Forzar vía pasillo de transición
                    pasos_por_0 = abs(self.col_actual - 0) + abs(0 - col_dest)
                    pasos_por_8 = abs(self.col_actual - 8) + abs(8 - col_dest)
                    col_transicion = 0 if pasos_por_0 <= pasos_por_8 else 8
                    if self.col_actual != col_transicion:
                        pasos, costo = self.calcular_distancia(self.fila_actual, self.col_actual, self.fila_actual, col_transicion)
                        self._registrar_segmento(self.fila_actual, col_transicion, pasos, costo, f"Ir a pasillo {col_transicion}")
                    if self.fila_actual != fila_dest:
                        pasos, costo = self.calcular_distancia(self.fila_actual, self.col_actual, fila_dest, self.col_actual)
                        self._registrar_segmento(fila_dest, col_transicion, pasos, costo, f"Desplazarse en pasillo {col_transicion} a fila {fila_dest}")
                    if col_transicion != col_dest:
                        pasos, costo = self.calcular_distancia(self.fila_actual, self.col_actual, fila_dest, col_dest)
                        self._registrar_segmento(fila_dest, col_dest, pasos, costo, descripcion)
                else:
                    pasos, costo = self.calcular_distancia(self.fila_actual, self.col_actual, fila_dest, col_dest)
                    self._registrar_segmento(fila_dest, col_dest, pasos, costo, descripcion)
            else:
                # Movimiento no diagonal -> registro directo
                pasos, costo = self.calcular_distancia(self.fila_actual, self.col_actual, fila_dest, col_dest)
                self._registrar_segmento(fila_dest, col_dest, pasos, costo, descripcion)
            return

        # Elegir columna de transición (0 u 8) por menor costo estimado
        pasos_por_0 = abs(self.col_actual - 0) + abs(0 - col_dest)
        pasos_por_8 = abs(self.col_actual - 8) + abs(8 - col_dest)
        col_transicion = 0 if pasos_por_0 <= pasos_por_8 else 8

        # 1) Mover horizontalmente hasta la columna de transición (misma fila actual)
        if self.col_actual != col_transicion:
            pasos, costo = self.calcular_distancia(self.fila_actual, self.col_actual, self.fila_actual, col_transicion)
            self._registrar_segmento(self.fila_actual, col_transicion, pasos, costo, f"Ir a pasillo {col_transicion}")

        # 2) Bajar/Subir verticalmente dentro del pasillo hasta la fila destino
        if self.fila_actual != fila_dest:
            pasos, costo = self.calcular_distancia(self.fila_actual, self.col_actual, fila_dest, self.col_actual)
            self._registrar_segmento(fila_dest, col_transicion, pasos, costo, f"Desplazarse en pasillo {col_transicion} a fila {fila_dest}")

        # 3) Cruzar horizontalmente desde pasillo hasta columna destino
        if col_transicion != col_dest:
            pasos, costo = self.calcular_distancia(self.fila_actual, self.col_actual, fila_dest, col_dest)
            self._registrar_segmento(fila_dest, col_dest, pasos, costo, descripcion)
    
    def _registrar_movimiento_con_restriccion(self, fila1, col1, fila2, col2):
        """Registra el movimiento en la ruta - SOLO horizontal y vertical, sin diagonales"""
        def get_zona(col):
            if col < 4:
                return 'izq'
            elif col <= 8:
                return 'centro'
            else:
                return 'der'
        
        zona1 = get_zona(col1)
        zona2 = get_zona(col2)
        
        # Caso 1: Misma zona o columna - movimiento directo
        if zona1 == zona2 or col1 == col2:
            self.ruta.append((fila2, col2))
            return
        
        # Caso 2: Diferentes zonas - RUTA COMPLETA sin diagonales
        # Elegir columna de transición (0 u 8)
        pasos_por_0 = abs(col1 - 0) + abs(0 - col2)
        pasos_por_8 = abs(col1 - 8) + abs(8 - col2)
        col_transicion = 0 if pasos_por_0 <= pasos_por_8 else 8
        
        # La ruta será:
        # 1. Horizontal a pasillo (fila1, col_transicion)
        # 2. Vertical en pasillo a altura destino (fila2, col_transicion)
        # 3. Horizontal a destino (fila2, col2)
        
        # Registrar cada punto clave de la ruta
        self.ruta.append((fila1, col_transicion))      # Horizontal a pasillo
        self.ruta.append((fila2, col_transicion))      # Vertical en pasillo
        self.ruta.append((fila2, col2))                # Horizontal a destino

    def procesar_columna_con_restriccion(self, col, config):
        """
        Procesa una columna de manera simplificada.
        - Ir a la columna
        - Recoger todos los paquetes en orden
        - Salir por el punto óptimo
        """
        if col not in self.paquetes_por_columna:
            return
        
        paquetes_fila = self.paquetes_por_columna[col]
        entrada = config['entrada']
        salida = config['salida']
        
        # 1. Ir a la entrada de la columna (respetando restricción)
        if self.fila_actual != entrada or self.col_actual != col:
            self.mover_respetando_restriccion(entrada, col, f"Entrada a columna {col}")
        
        # 2. Recoger paquetes en orden
        filas_ordenadas = sorted(paquetes_fila)
        
        if entrada <= filas_ordenadas[0]:
            # De arriba hacia abajo
            for fila_paq in filas_ordenadas:
                if self.fila_actual != fila_paq:
                    self.mover_respetando_restriccion(fila_paq, col, f"Recoger paquete en ({fila_paq},{col})")
        else:
            # De abajo hacia arriba
            for fila_paq in reversed(filas_ordenadas):
                if self.fila_actual != fila_paq:
                    self.mover_respetando_restriccion(fila_paq, col, f"Recoger paquete en ({fila_paq},{col})")
        
        # 3. Salir de la columna por el punto óptimo
        if self.fila_actual != salida:
            self.mover_respetando_restriccion(salida, col, f"Salida de columna {col}")

    def ejecutar_recoleccion(self):
        """
        Ejecuta la recolección completa con optimización y restricciones.
        Incluye ruta optimizada de salida al punto de entrega.
        """
        self.pasos = []
        self.ruta = [(self.fila_actual, self.col_actual)]
        self.costo_total = 0
        
        # 1. Obtener orden optimizado de columnas
        columnas_ordenadas = self.optimizador.optimizar_orden_columnas(
            self.paquetes,
            [self.fila_actual, self.col_actual]
        )
        
        # 2. Procesar cada columna con restricciones
        pos_actual = [self.fila_actual, self.col_actual]
        
        for col in columnas_ordenadas:
            filas = self.paquetes_por_columna[col]
            config = self.optimizador.calcular_costo_con_restriccion(
                pos_actual, col, filas
            )
            
            self.procesar_columna_con_restriccion(col, config)
            pos_actual = [self.fila_actual, self.col_actual]
        
        # 3. Ruta optimizada hacia punto de entrega (FINAL)
        if hasattr(self, 'final_punto'):
            punto_entrega = self.final_punto
        else:
            punto_entrega = FINAL
        
        ruta_salida, costo_salida = self.optimizador.calcular_ruta_optima_salida(
            [self.fila_actual, self.col_actual],
            punto_entrega
        )
        
        # Ejecutar ruta de salida (respetando restricciones)
        for fila_dest, col_dest in ruta_salida:
            self.mover_respetando_restriccion(fila_dest, col_dest, "Ruta hacia punto de entrega")

        # Normalizar la ruta final para asegurar segmentos H/V y
        # que no crucen PASILLOS salvo por columnas de transición (0 u 8).
        try:
            self.ruta = self._normalizar_ruta(self.ruta)
        except Exception:
            # En caso de error de normalización, devolvemos la ruta tal cual
            pass

        return {
            'total_cost': round(self.costo_total, 2),
            'pos_final': [self.fila_actual, self.col_actual],
            'pasos': self.pasos,
            'ruta': self.ruta,
            'orden_columnas': columnas_ordenadas,
            'ahorro_estimado': self._calcular_ahorro()
        }

    def _calcular_ahorro(self):
        """
        Estima el ahorro comparado con una ruta sin optimización.
        """
        # Costo estimado sin optimización (ruta directa secuencial)
        costo_sin_opt = 0
        pos = self.inicio[:]
        
        for paq in self.paquetes:
            _, costo = self.optimizador.calcular_costo_movimiento(
                pos[0], pos[1], paq[0], paq[1]
            )
            costo_sin_opt += costo
            pos = paq[:]
        
        ahorro = costo_sin_opt - self.costo_total
        porcentaje = (ahorro / costo_sin_opt * 100) if costo_sin_opt > 0 else 0
        
        return {
            'costo_sin_optimizar': round(costo_sin_opt, 2),
            'costo_optimizado': round(self.costo_total, 2),
            'ahorro_absoluto': round(ahorro, 2),
            'ahorro_porcentaje': round(porcentaje, 2)
        }

    def generar_tabla_pasos(self):
        """Devuelve lista de pasos"""
        return self.pasos

    def _normalizar_ruta(self, ruta):
        """Devuelve una nueva ruta donde todos los tramos son ortogonales (H/V)
        y ningún tramo horizontal cruza una columna en `PASILLOS` salvo que el
        inicio o el fin sea una columna de transición (0 u 8).
        """
        if not ruta:
            return ruta

        def crossed_pasillos(col_a, col_b):
            left, right = min(col_a, col_b), max(col_a, col_b)
            return [c for c in PASILLOS if left < c < right]

        new = [ruta[0]]
        for i in range(len(ruta) - 1):
            r1, c1 = ruta[i]
            r2, c2 = ruta[i + 1]

            # skip identical
            if r1 == r2 and c1 == c2:
                continue

            # Vertical move
            if c1 == c2:
                new.append((r2, c2))
                continue

            # Horizontal move
            if r1 == r2:
                crossed = crossed_pasillos(c1, c2)
                if crossed and (c1 not in (0, 8) and c2 not in (0, 8)):
                    # route via transition column
                    pasos_por_0 = abs(c1 - 0) + abs(0 - c2)
                    pasos_por_8 = abs(c1 - 8) + abs(8 - c2)
                    col_trans = 0 if pasos_por_0 <= pasos_por_8 else 8
                    if (r1, col_trans) != new[-1]:
                        new.append((r1, col_trans))
                    if (r2, col_trans) != new[-1]:
                        new.append((r2, col_trans))
                    if (r2, c2) != new[-1]:
                        new.append((r2, c2))
                else:
                    new.append((r2, c2))
                continue

            # Diagonal move: try to decompose into two orthogonal steps
            # Try horizontal then vertical (via (r1, c2)) and prefer the one
            # that doesn't cross PASILLOS on its horizontal leg.
            opt1_h_crossed = crossed_pasillos(c1, c2)
            # For opt1 horizontal is from c1->c2 at row r1
            opt1_bad = bool(opt1_h_crossed and (c1 not in (0, 8) and c2 not in (0, 8)))

            # For opt2 horizontal is from c1->c2 at row r2 (vertical then horizontal)
            opt2_h_crossed = crossed_pasillos(c1, c2)
            opt2_bad = bool(opt2_h_crossed and (c1 not in (0, 8) and c2 not in (0, 8)))

            if not opt1_bad:
                # do (r1,c2) then (r2,c2)
                if (r1, c2) != new[-1]:
                    new.append((r1, c2))
                if (r2, c2) != new[-1]:
                    new.append((r2, c2))
                continue

            if not opt2_bad:
                # do (r2,c1) then (r2,c2)
                if (r2, c1) != new[-1]:
                    new.append((r2, c1))
                if (r2, c2) != new[-1]:
                    new.append((r2, c2))
                continue

            # Both decompositions would cross pasillos on their horizontal leg.
            # Force route via transition column.
            pasos_por_0 = abs(c1 - 0) + abs(0 - c2)
            pasos_por_8 = abs(c1 - 8) + abs(8 - c2)
            col_trans = 0 if pasos_por_0 <= pasos_por_8 else 8

            if (r1, col_trans) != new[-1]:
                new.append((r1, col_trans))
            if (r2, col_trans) != new[-1]:
                new.append((r2, col_trans))
            if (r2, c2) != new[-1]:
                new.append((r2, c2))

        # Remove possible consecutive duplicates
        dedup = [new[0]]
        for p in new[1:]:
            if p != dedup[-1]:
                dedup.append(p)

        return dedup