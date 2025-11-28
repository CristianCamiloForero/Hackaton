import json

# --- Configuración del Almacén ---
FILAS = 9
COLUMNAS = 12
PASILLOS = {1, 4, 7, 10}
PAQUETES = [[2, 0], [6, 3], [0, 5], [3, 6], [4, 8], [1, 9], [6, 11]]
INICIO = [0, 0]
FINAL = [8, 11] # Punto de entrega final
COSTO_CELDA = 2.7
COSTO_PASILLO = 5.0

class RobotRecolectorSimple:
    """
    Implementa el algoritmo de recolección simple descrito por el instructor.
    - Se mueve por la fila 0 para cambiar de columna.
    - Baja a recoger paquetes y elige la salida más eficiente (volver a fila 0 o ir a fila 8).
    """

    def __init__(self, paquetes, inicio, final):
        self.paquetes_config = paquetes
        self.inicio = inicio
        self.final = final
        
        self.pos_actual = list(inicio)
        self.costo_total = 0.0
        self.pasos_detalle = []
        self.ruta_visual = [tuple(self.pos_actual)]

        # Agrupar paquetes por columna para facilitar el procesamiento
        self.paquetes_por_columna = {}
        for fila, col in self.paquetes_config:
            if col not in self.paquetes_por_columna:
                self.paquetes_por_columna[col] = []
            self.paquetes_por_columna[col].append(fila)
        
        for col in self.paquetes_por_columna:
            self.paquetes_por_columna[col].sort()

    def _registrar_paso(self, desde, hacia, descripcion):
        """Registra un movimiento y calcula su costo."""
        f1, c1 = desde
        f2, c2 = hacia
        
        pasos_movimiento = 0
        costo_movimiento = 0
        es_pasillo = False

        # Movimiento Vertical
        if c1 == c2:
            pasos_movimiento = abs(f1 - f2)
            costo_movimiento = pasos_movimiento * COSTO_CELDA
        # Movimiento Horizontal
        elif f1 == f2:
            pasos_movimiento = abs(c1 - c2)
            for c in range(min(c1, c2), max(c1, c2)):
                if (c + 1) in PASILLOS:
                    costo_movimiento += COSTO_PASILLO
                    es_pasillo = True
                else:
                    costo_movimiento += COSTO_CELDA
        
        self.costo_total += costo_movimiento
        self.pasos_detalle.append({
            'Desde': f"({f1},{c1})",
            'Hacia': f"({f2},{c2})",
            'Pasos': pasos_movimiento,
            'Costo': round(costo_movimiento, 2),
            'Es Pasillo': "Sí" if es_pasillo else "No",
            'Acumulado': round(self.costo_total, 2),
            'Descripción': descripcion
        })
        
        # Actualizar posición y ruta
        self.pos_actual = list(hacia)
        self.ruta_visual.append(tuple(hacia))

    def ejecutar_recoleccion(self):
        """Ejecuta el ciclo completo de recolección."""
        
        columnas_a_visitar = sorted(self.paquetes_por_columna.keys())

        # Moverse a la primera columna con paquetes si no empezamos en ella
        if self.pos_actual[1] != columnas_a_visitar[0]:
            desde = tuple(self.pos_actual)
            hacia = (self.pos_actual[0], columnas_a_visitar[0])
            self._registrar_paso(desde, hacia, f"Ir a la primera columna de trabajo ({hacia[1]})")

        for i, col in enumerate(columnas_a_visitar):
            # 1. Bajar a recoger paquetes
            paquetes_en_col = self.paquetes_por_columna[col]
            fila_entrada = paquetes_en_col[0] # Siempre entra por el más alto
            
            desde = tuple(self.pos_actual)
            hacia = (fila_entrada, col)
            self._registrar_paso(desde, hacia, f"Bajar a recoger paquete en ({hacia[0]},{hacia[1]})")

            # Recoger todos los paquetes en la columna (movimiento vertical)
            for j in range(len(paquetes_en_col) - 1):
                desde = (paquetes_en_col[j], col)
                hacia = (paquetes_en_col[j+1], col)
                self._registrar_paso(desde, hacia, f"Recoger siguiente paquete en ({hacia[0]},{hacia[1]})")

            # 2. Decidir a dónde moverse para la siguiente columna
            if i + 1 < len(columnas_a_visitar):
                col_siguiente = columnas_a_visitar[i+1]
                
                # Opción A: Volver a la fila 0 y moverse horizontalmente
                pasos_a_fila_0 = self.pos_actual[0]
                
                # Opción B: Ir a la fila 8 (final) y moverse horizontalmente
                pasos_a_fila_8 = (FILAS - 1) - self.pos_actual[0]

                if pasos_a_fila_0 <= pasos_a_fila_8:
                    # Mover a fila 0
                    desde = tuple(self.pos_actual)
                    hacia = (0, self.pos_actual[1])
                    self._registrar_paso(desde, hacia, "Subir a fila 0 para avanzar")
                    # Mover a la siguiente columna por fila 0
                    desde = tuple(self.pos_actual)
                    hacia = (0, col_siguiente)
                    self._registrar_paso(desde, hacia, f"Avanzar a la siguiente columna ({col_siguiente})")
                else:
                    # Mover a fila 8
                    desde = tuple(self.pos_actual)
                    hacia = (FILAS - 1, self.pos_actual[1])
                    self._registrar_paso(desde, hacia, "Bajar a fila 8 para avanzar")
                    # Mover a la siguiente columna por fila 8
                    desde = tuple(self.pos_actual)
                    hacia = (FILAS - 1, col_siguiente)
                    self._registrar_paso(desde, hacia, f"Avanzar a la siguiente columna ({col_siguiente})")
        
        # 3. Moverse al punto de entrega final
        desde = tuple(self.pos_actual)
        hacia = tuple(self.final)
        self._registrar_paso(desde, hacia, f"Ir al punto de entrega final en {hacia}")

        return {
            'total_cost': round(self.costo_total, 2),
            'pos_final': self.pos_actual,
            'pasos': self.pasos_detalle,
            'ruta': self.ruta_visual,
        }

# --- Ejecución y Salida ---
if __name__ == '__main__':
    # Esta parte se ejecuta solo si corres `python Hackaton/Main.py`
    # El frontend usará la lógica de app.py, pero esta simulación es para validar.
    robot = RobotRecolectorSimple(paquetes=PAQUETES, inicio=INICIO, final=FINAL)
    resultado = robot.ejecutar_recoleccion()
    
    # Imprimir el resultado en formato JSON para que otros scripts lo puedan usar
    print(json.dumps(resultado, indent=2))
