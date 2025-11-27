from .config import FILAS, COLUMNAS, PASILLOS, PAQUETES, INICIO, COSTO_CELDA, COSTO_PASILLO
from .optimizador import Optimizador


class RobotAlmacen:
    """Clase que representa un robot recolector de paquetes en un almacén (backend optimizado)"""

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

        # Inicializar optimizador
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

    def columna_vacia(self, col):
        return col not in self.paquetes_por_columna

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

    def determinar_punto_entrada_salida(self, col, pos_actual):
        """
        Determina el mejor punto de entrada y salida de una columna.
        Optimización: evalúa desde qué extremo es más eficiente entrar.
        """
        if self.columna_vacia(col):
            return None, None
        
        paquetes_fila = self.paquetes_por_columna[col]
        primer_paquete = paquetes_fila[0]
        ultimo_paquete = paquetes_fila[-1]
        
        # Calcular costo de entrar por arriba
        costo_arriba = abs(pos_actual - 0) + abs(0 - ultimo_paquete)
        
        # Calcular costo de entrar por abajo
        costo_abajo = abs(pos_actual - (FILAS - 1)) + abs((FILAS - 1) - primer_paquete)
        
        if costo_arriba <= costo_abajo:
            return 0, FILAS - 1  # Entrar por arriba, salir por abajo
        else:
            return FILAS - 1, 0  # Entrar por abajo, salir por arriba

    def procesar_columna_optimizada(self, col):
        """Procesa una columna con estrategia optimizada - SIN recorridos innecesarios"""
        if self.columna_vacia(col):
            return
        
        paquetes_fila = self.paquetes_por_columna[col]
        
        # Moverse horizontalmente a la columna si es necesario
        if col != self.col_actual:
            self.mover_a(self.fila_actual, col, f"Moverse a columna {col}")
        
        # Estrategia simple y óptima: visitar paquetes en orden vertical
        # Minimiza movimientos innecesarios
        paquetes_ordenados = sorted(paquetes_fila)
        
        # Detectar si es mejor ir de arriba-abajo o abajo-arriba
        if self.fila_actual <= paquetes_ordenados[0]:
            # Robot está arriba o al inicio: recorrer de arriba-abajo
            for idx, fila_paq in enumerate(paquetes_ordenados):
                if self.fila_actual != fila_paq:
                    self.mover_a(fila_paq, col, f"Recoger paquete {idx+1}")
        else:
            # Robot está abajo: recorrer de abajo-arriba
            for idx, fila_paq in enumerate(reversed(paquetes_ordenados)):
                if self.fila_actual != fila_paq:
                    self.mover_a(fila_paq, col, f"Recoger paquete {idx+1}")

    def ejecutar_recoleccion(self):
        """
        Ejecuta la recolección con optimización de ruta.
        Usa el optimizador para determinar el mejor orden de columnas.
        """
        self.pasos = []
        self.ruta = [(self.fila_actual, self.col_actual)]
        
        # Obtener orden optimizado de columnas
        columnas_ordenadas = self.optimizador.optimizar_orden_columnas(
            self.paquetes,
            [self.fila_actual, self.col_actual]
        )
        
        # Procesar cada columna en el orden optimizado
        for col in columnas_ordenadas:
            self.procesar_columna_optimizada(col)
        
        return {
            'total_cost': round(self.costo_total, 2),
            'pos_final': [self.fila_actual, self.col_actual],
            'pasos': self.pasos,
            'ruta': self.ruta,
            'orden_columnas': columnas_ordenadas
        }

    def generar_tabla_pasos(self):
        """Devuelve lista de pasos (sin pandas)"""
        return self.pasos