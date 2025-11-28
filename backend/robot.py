from .config import FILAS, PASILLOS, PAQUETES, INICIO, FINAL, COSTO_CELDA, COSTO_PASILLO

class RobotAlmacen:
    """
    Implementa el algoritmo de recolección simple descrito por el instructor.
    - Se mueve por una fila principal (0 o la última) para cambiar de columna.
    - Baja/sube a recoger paquetes y elige la salida más eficiente.
    """

    def __init__(self, paquetes=None, inicio=None, final=None, costo_celda=None, costo_pasillo=None):
        self.paquetes_config = paquetes if paquetes is not None else PAQUETES
        self.inicio = inicio if inicio is not None else INICIO
        self.final = final if final is not None else FINAL
        self.costo_celda_valor = float(costo_celda if costo_celda is not None else COSTO_CELDA)
        self.costo_pasillo_valor = float(costo_pasillo if costo_pasillo is not None else COSTO_PASILLO)
        
        self.pos_actual = list(self.inicio)
        self.costo_total = 0.0
        self.pasos_detalle = []
        self.ruta_visual = [tuple(self.pos_actual)]

        self.paquetes_por_columna = {}
        for fila, col in self.paquetes_config:
            if col not in self.paquetes_por_columna:
                self.paquetes_por_columna[col] = []
            self.paquetes_por_columna[col].append(fila)
        
        for col in self.paquetes_por_columna:
            self.paquetes_por_columna[col].sort()

    def _registrar_paso(self, desde, hacia, descripcion):
        """Registra un movimiento, calcula su costo y actualiza la ruta."""
        f1, c1 = desde
        f2, c2 = hacia
        
        pasos_movimiento = 0
        costo_movimiento = 0
        es_pasillo_str = "No"

        # Movimiento Vertical
        if c1 == c2:
            pasos_movimiento = abs(f1 - f2)
            costo_movimiento = pasos_movimiento * self.costo_celda_valor
        # Movimiento Horizontal
        elif f1 == f2:
            pasos_movimiento = abs(c1 - c2)
            for c in range(min(c1, c2), max(c1, c2)):
                # El costo se aplica al entrar en la siguiente celda
                if (c + 1) in PASILLOS:
                    costo_movimiento += self.costo_pasillo_valor
                else:
                    costo_movimiento += self.costo_celda_valor
            # Si el rango de movimiento contiene un pasillo
            if any(p in PASILLOS for p in range(min(c1, c2) + 1, max(c1, c2) + 1)):
                 es_pasillo_str = "Sí"

        self.costo_total += costo_movimiento
        self.pasos_detalle.append({
            'Desde': f"({f1},{c1})",
            'Hacia': f"({f2},{c2})",
            'Pasos': pasos_movimiento,
            'Costo': round(costo_movimiento, 2),
            'Es Pasillo': es_pasillo_str,
            'Acumulado': round(self.costo_total, 2),
            'Descripción': descripcion
        })
        
        # Actualizar posición y añadir todos los puntos intermedios a la ruta visual
        # para que el frontend dibuje líneas rectas.
        self.pos_actual = list(hacia)
        self.ruta_visual.append(tuple(hacia))

    def ejecutar_recoleccion(self):
        """Ejecuta el ciclo completo de recolección según la lógica del instructor."""
        
        columnas_a_visitar = sorted(self.paquetes_por_columna.keys())

        if not columnas_a_visitar:
            # Si no hay paquetes, ir directamente al final
            self._registrar_paso(tuple(self.pos_actual), tuple(self.final), "Ir al punto de entrega final")
            return self.generar_resultado()

        # Moverse horizontalmente a la primera columna con paquetes
        if self.pos_actual[1] != columnas_a_visitar[0]:
            self._registrar_paso(tuple(self.pos_actual), (self.pos_actual[0], columnas_a_visitar[0]), f"Ir a la primera columna ({columnas_a_visitar[0]})")

        for i, col in enumerate(columnas_a_visitar):
            paquetes_en_col = self.paquetes_por_columna[col]
            
            # 1. Moverse verticalmente a la primera fila de paquete en la columna
            self._registrar_paso(tuple(self.pos_actual), (paquetes_en_col[0], col), f"Bajar a recoger en ({paquetes_en_col[0]},{col})")

            # 2. Recorrer todos los paquetes en la columna
            for j in range(len(paquetes_en_col) - 1):
                self._registrar_paso((paquetes_en_col[j], col), (paquetes_en_col[j+1], col), f"Recoger paquete en ({paquetes_en_col[j+1]},{col})")

            # 3. Decidir cómo moverse a la siguiente columna
            if i + 1 < len(columnas_a_visitar):
                col_siguiente = columnas_a_visitar[i+1]
                
                pasos_a_fila_0 = self.pos_actual[0]
                pasos_a_fila_final = (FILAS - 1) - self.pos_actual[0]

                # Elegir la ruta vertical más corta para el tránsito horizontal
                if pasos_a_fila_0 <= pasos_a_fila_final:
                    fila_transito = 0
                    accion = "Subir"
                else:
                    fila_transito = FILAS - 1
                    accion = "Bajar"
                
                # Moverse verticalmente a la fila de tránsito
                self._registrar_paso(tuple(self.pos_actual), (fila_transito, self.pos_actual[1]), f"{accion} a fila {fila_transito}")
                # Moverse horizontalmente a la siguiente columna
                self._registrar_paso(tuple(self.pos_actual), (fila_transito, col_siguiente), f"Avanzar a columna {col_siguiente}")
        
        # 4. Movimiento final al punto de entrega (descompuesto en V y H)
        if tuple(self.pos_actual) != tuple(self.final):
            # Movimiento vertical
            if self.pos_actual[0] != self.final[0]:
                self._registrar_paso(tuple(self.pos_actual), (self.final[0], self.pos_actual[1]), "Ajuste vertical para entrega")
            # Movimiento horizontal
            if self.pos_actual[1] != self.final[1]:
                self._registrar_paso(tuple(self.pos_actual), tuple(self.final), "Ajuste horizontal para entrega")

        return self.generar_resultado()

    def generar_resultado(self):
        return {
            'total_cost': round(self.costo_total, 2),
            'pos_final': self.pos_actual,
            'pasos': self.pasos_detalle,
            'ruta': self.ruta_visual,
        }
