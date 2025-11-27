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
        """Calcula distancia y costo entre dos posiciones"""
        pasos_fila = abs(fila2 - fila1)
        costo = 0
        pasos_total = 0
        
        # Costo vertical
        costo += pasos_fila * self.costo_celda_valor
        pasos_total += pasos_fila
        
        # Costo horizontal
        for c in range(min(col1, col2), max(col1, col2)):
            if self.es_pasillo(c + 1):
                costo += self.costo_pasillo_valor
            else:
                costo += self.costo_celda_valor
            pasos_total += 1
            
        return pasos_total, costo

    def mover_a(self, fila_dest, col_dest, descripcion):
        """Registra movimiento del robot"""
        pasos, costo = self.calcular_distancia(
            self.fila_actual, self.col_actual, fila_dest, col_dest
        )
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
        self.fila_actual = fila_dest
        self.col_actual = col_dest
        self.ruta.append((fila_dest, col_dest))

    def procesar_columna_con_restriccion(self, col, config):
        """
        Procesa una columna respetando las restricciones de movimiento.
        
        Args:
            col: columna a procesar
            config: configuración retornada por el optimizador con:
                - col_transicion: columna de transición (0 o 8)
                - entrada: fila de entrada a la columna
                - salida: fila de salida de la columna
                - fila_trans: fila en la columna de transición
        """
        if col not in self.paquetes_por_columna:
            return
        
        paquetes_fila = self.paquetes_por_columna[col]
        
        # Si necesitamos transición (cambio de columna)
        if config['col_transicion'] is not None and self.col_actual != col:
            col_trans = config['col_transicion']
            
            # 1. Moverse horizontalmente a columna de transición
            if self.col_actual != col_trans:
                self.mover_a(
                    self.fila_actual, 
                    col_trans, 
                    f"Transición a columna {col_trans}"
                )
            
            # 2. Moverse verticalmente en columna de transición
            if self.fila_actual != config['fila_trans']:
                self.mover_a(
                    config['fila_trans'], 
                    col_trans, 
                    f"Ajuste vertical en transición"
                )
            
            # 3. Moverse horizontalmente a columna destino
            if col_trans != col:
                self.mover_a(
                    self.fila_actual, 
                    col, 
                    f"Entrada a columna {col}"
                )
        elif self.col_actual != col:
            # Ya estamos en columna de transición, solo ir a destino
            self.mover_a(
                self.fila_actual, 
                col, 
                f"Entrada a columna {col}"
            )
        
        # 4. Procesar paquetes en la columna
        filas_ordenadas = sorted(paquetes_fila)
        
        # Determinar dirección de recorrido
        if config['entrada'] <= filas_ordenadas[0]:
            # Recorrer de arriba hacia abajo
            for idx, fila_paq in enumerate(filas_ordenadas):
                if self.fila_actual != fila_paq:
                    self.mover_a(
                        fila_paq, 
                        col, 
                        f"Recoger paquete en ({fila_paq},{col})"
                    )
        else:
            # Recorrer de abajo hacia arriba
            for idx, fila_paq in enumerate(reversed(filas_ordenadas)):
                if self.fila_actual != fila_paq:
                    self.mover_a(
                        fila_paq, 
                        col, 
                        f"Recoger paquete en ({fila_paq},{col})"
                    )
        
        # 5. Moverse al punto de salida de la columna
        if self.fila_actual != config['salida']:
            self.mover_a(
                config['salida'], 
                col, 
                f"Salida de columna {col}"
            )

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
        
        # Ejecutar ruta de salida
        for fila_dest, col_dest in ruta_salida:
            self.mover_a(fila_dest, col_dest, "Ruta hacia punto de entrega")
        
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
            costo_sin_opt += self.optimizador.calcular_costo_movimiento(
                pos[0], pos[1], paq[0], paq[1]
            )
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