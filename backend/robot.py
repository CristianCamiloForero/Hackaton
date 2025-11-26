from .config import FILAS, COLUMNAS, PASILLOS, PAQUETES, INICIO, COSTO_CELDA, COSTO_PASILLO


class RobotAlmacen:
    """Clase que representa un robot recolector de paquetes en un almacén (backend)"""

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

        # Crear matriz como lista de listas
        self.matriz = [["" for _ in range(COLUMNAS)] for _ in range(FILAS)]
        self.fila_actual = inicio[0]
        self.col_actual = inicio[1]
        self.costo_total = 0
        self.pasos = []
        self.ruta = [(self.fila_actual, self.col_actual)]

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

    def columna_vacia(self, col):
        return col not in self.paquetes_por_columna

    def calcular_distancia(self, fila1, col1, fila2, col2):
        pasos_fila = abs(fila2 - fila1)
        costo = 0
        pasos_total = 0
        costo += pasos_fila * self.costo_celda_valor
        pasos_total += pasos_fila
        for c in range(min(col1, col2), max(col1, col2)):
            if self.es_pasillo(c + 1):
                costo += self.costo_pasillo_valor
            else:
                costo += self.costo_celda_valor
            pasos_total += 1
        return pasos_total, costo

    def mover_a(self, fila_dest, col_dest, descripcion):
        pasos, costo = self.calcular_distancia(self.fila_actual, self.col_actual, fila_dest, col_dest)
        self.costo_total += costo
        self.pasos.append({
            'Desde': f"({self.fila_actual},{self.col_actual})",
            'Hacia': f"({fila_dest},{col_dest})",
            'Pasos': pasos,
            'Costo': round(costo, 2),
            'Es Pasillo': "Sí" if self.es_pasillo(col_dest) else "No",
            'Columna Vacía': "Sí" if self.columna_vacia(col_dest) else "No",
            'Acumulado': round(self.costo_total, 2),
            'Descripción': descripcion
        })
        self.fila_actual = fila_dest
        self.col_actual = col_dest
        self.ruta.append((fila_dest, col_dest))

    def procesar_columna(self, col):
        if self.columna_vacia(col):
            return
        paquetes_fila = self.paquetes_por_columna[col]
        dist_desde_arriba = abs(self.fila_actual - 0) + abs(0 - paquetes_fila[0])
        dist_desde_abajo = abs(self.fila_actual - (FILAS-1)) + abs((FILAS-1) - paquetes_fila[-1])
        if dist_desde_arriba <= dist_desde_abajo:
            punto_entrada = 0
            punto_salida = FILAS - 1
            sentido = "arriba-abajo"
        else:
            punto_entrada = FILAS - 1
            punto_salida = 0
            sentido = "abajo-arriba"
        if col != self.col_actual:
            self.mover_a(self.fila_actual, col, f"Moverse horizontalmente a columna {col}")
        if self.fila_actual != punto_entrada:
            self.mover_a(punto_entrada, col, f"Entrar a columna {col} por {sentido}")
        for idx, fila_paq in enumerate(paquetes_fila):
            if self.fila_actual != fila_paq:
                self.mover_a(fila_paq, col, f"Recoger paquete #{idx+1} en columna {col}")
        if self.fila_actual != punto_salida:
            self.mover_a(punto_salida, col, f"Completar recorrido de columna {col} hacia {sentido}")

    def ejecutar_recoleccion(self):
        # Mensajes mantenidos para compatibilidad
        self.pasos = []
        self.ruta = [(self.fila_actual, self.col_actual)]
        columnas_con_paquetes = sorted(self.paquetes_por_columna.keys())
        for col in columnas_con_paquetes:
            self.procesar_columna(col)
        return {
            'total_cost': round(self.costo_total, 2),
            'pos_final': [self.fila_actual, self.col_actual],
            'pasos': self.pasos,
            'ruta': self.ruta
        }

    def generar_tabla_pasos(self):
        # devuelve lista de pasos (sin pandas)
        return self.pasos
