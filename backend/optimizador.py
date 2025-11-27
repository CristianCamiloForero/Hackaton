import itertools
from .config import FILAS, PASILLOS


class Optimizador:
    """
    Optimizador mejorado con restricciones de cambio de columna.
    El robot solo puede cambiar de columna pasando por columnas 0 u 8.
    ESTRATEGIA: Agrupar columnas por zonas y minimizar transiciones.
    """
    
    # Columnas permitidas para cambio de nivel (extremos del almacén)
    COLUMNAS_TRANSICION = [0, 8]
    
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

    def agrupar_columnas_por_zona(self, columnas):
        """
        Agrupa columnas en zonas accesibles sin cruzar pasillos principales.
        Esto minimiza las transiciones necesarias.
        """
        if not columnas:
            return []
        
        zonas = []
        zona_actual = [columnas[0]]
        
        for i in range(1, len(columnas)):
            col_anterior = columnas[i-1]
            col_actual = columnas[i]
            
            # Verificar si necesitamos transición entre estas columnas
            # (si hay que cruzar de una zona a otra a través de columnas 0 u 8)
            necesita_transicion = self._necesita_transicion(col_anterior, col_actual)
            
            if necesita_transicion:
                # Nueva zona
                zonas.append(zona_actual)
                zona_actual = [col_actual]
            else:
                # Misma zona
                zona_actual.append(col_actual)
        
        zonas.append(zona_actual)
        return zonas

    def _necesita_transicion(self, col1, col2):
        """
        Determina si se necesita transición entre dos columnas.
        Solo necesitamos transición si las columnas no están en la misma "zona conectada"
        """
        # Si ambas columnas son de transición, no hay problema
        if col1 in self.COLUMNAS_TRANSICION and col2 in self.COLUMNAS_TRANSICION:
            return False
        
        # Si una es de transición y la otra no, siempre es accesible
        if col1 in self.COLUMNAS_TRANSICION or col2 in self.COLUMNAS_TRANSICION:
            return False
        
        # Si ambas están del mismo lado (0-7 o 8-11), verificar si están conectadas
        # Definir zonas: 0-3 (izquierda de col 0), 4-7 (entre 0 y 8), 9-11 (derecha de col 8)
        zona1 = self._obtener_zona_columna(col1)
        zona2 = self._obtener_zona_columna(col2)
        
        # Solo necesitan transición si están en zonas diferentes
        return zona1 != zona2

    def _obtener_zona_columna(self, col):
        """
        Determina en qué zona está una columna:
        - zona 'izq': columnas accesibles desde columna 0 (0-3)
        - zona 'centro': columnas entre 0 y 8 (4-7) 
        - zona 'der': columnas accesibles desde columna 8 (8-11)
        """
        if col <= 3:
            return 'izq'
        elif col <= 7:
            return 'centro'
        else:
            return 'der'

    def calcular_costo_con_restriccion(self, pos_actual, col_destino, filas_destino):
        """
        Calcula el costo de ir a una columna considerando la restricción.
        OPTIMIZADO: Solo hace transición si es necesario cambiar de zona.
        """
        fila_actual, col_actual = pos_actual
        
        # Si ya estamos en la columna destino
        if col_actual == col_destino:
            return self._costo_dentro_columna(fila_actual, col_destino, filas_destino)
        
        # Verificar si necesitamos transición
        necesita_transicion = self._necesita_transicion(col_actual, col_destino)
        
        if not necesita_transicion:
            # Movimiento directo sin transición
            return self._costo_movimiento_directo(pos_actual, col_destino, filas_destino)
        
        # Necesitamos transición: evaluar ambas opciones (col 0 o col 8)
        mejor_costo = float('inf')
        mejor_config = None
        
        for col_trans in self.COLUMNAS_TRANSICION:
            config = self._calcular_costo_via_transicion(
                pos_actual, col_destino, filas_destino, col_trans
            )
            
            if config['costo'] < mejor_costo:
                mejor_costo = config['costo']
                mejor_config = config
        
        return mejor_config

    def _costo_movimiento_directo(self, pos_actual, col_destino, filas_destino):
        """Calcula costo de movimiento directo sin transición"""
        fila_actual, col_actual = pos_actual
        
        # Determinar mejor punto de entrada
        filas_ordenadas = sorted(filas_destino)
        punto_medio = filas_ordenadas[len(filas_ordenadas) // 2]
        
        # Evaluar entrar por arriba o por abajo
        if fila_actual <= punto_medio:
            entrada = min(filas_ordenadas)
            salida = max(filas_ordenadas)
        else:
            entrada = max(filas_ordenadas)
            salida = min(filas_ordenadas)
        
        # Costo: ir a la entrada + procesar columna
        costo = self.calcular_costo_movimiento(fila_actual, col_actual, entrada, col_destino)
        costo += self._costo_procesar_columna(entrada, col_destino, filas_destino, salida)
        
        return {
            'costo': costo,
            'col_transicion': None,
            'entrada': entrada,
            'salida': salida,
            'fila_trans': None
        }

    def _calcular_costo_via_transicion(self, pos_actual, col_destino, filas_destino, col_trans):
        """Calcula costo pasando por una columna de transición específica"""
        fila_actual, col_actual = pos_actual
        filas_ordenadas = sorted(filas_destino)
        
        # Determinar mejor punto de entrada desde la transición
        punto_medio = filas_ordenadas[len(filas_ordenadas) // 2]
        
        if punto_medio <= FILAS // 2:
            entrada = 0
            salida = FILAS - 1
        else:
            entrada = FILAS - 1
            salida = 0
        
        # Costo total
        costo = 0
        
        # 1. Ir a columna de transición
        costo += self.calcular_costo_movimiento(fila_actual, col_actual, fila_actual, col_trans)
        
        # 2. Moverse verticalmente en transición
        costo += abs(entrada - fila_actual) * self.costo_celda
        
        # 3. Ir desde transición a columna destino
        costo += self.calcular_costo_movimiento(entrada, col_trans, entrada, col_destino)
        
        # 4. Procesar la columna
        costo += self._costo_procesar_columna(entrada, col_destino, filas_destino, salida)
        
        return {
            'costo': costo,
            'col_transicion': col_trans,
            'entrada': entrada,
            'salida': salida,
            'fila_trans': entrada
        }

    def _costo_dentro_columna(self, fila_actual, col, filas_destino):
        """Calcula costo cuando ya estamos en la columna destino"""
        filas_ordenadas = sorted(filas_destino)
        
        # Determinar mejor dirección
        if fila_actual <= filas_ordenadas[0]:
            salida = max(filas_ordenadas)
        else:
            salida = min(filas_ordenadas)
        
        costo = self._costo_procesar_columna(fila_actual, col, filas_destino, salida)
        
        return {
            'costo': costo,
            'col_transicion': None,
            'entrada': fila_actual,
            'salida': salida,
            'fila_trans': None
        }

    def _costo_procesar_columna(self, fila_entrada, col, filas_paquetes, fila_salida):
        """Calcula el costo de procesar todos los paquetes en una columna"""
        costo = 0
        fila_actual = fila_entrada
        
        filas_ordenadas = sorted(filas_paquetes)
        
        # Recorrer paquetes en orden
        if fila_entrada <= filas_ordenadas[0]:
            # De arriba hacia abajo
            for fila_paq in filas_ordenadas:
                costo += abs(fila_paq - fila_actual) * self.costo_celda
                fila_actual = fila_paq
        else:
            # De abajo hacia arriba
            for fila_paq in reversed(filas_ordenadas):
                costo += abs(fila_paq - fila_actual) * self.costo_celda
                fila_actual = fila_paq
        
        # Ir a punto de salida
        costo += abs(fila_salida - fila_actual) * self.costo_celda
        
        return costo

    def optimizar_orden_columnas(self, paquetes, inicio):
        """
        Determina el orden óptimo para visitar columnas minimizando transiciones.
        ESTRATEGIA: Agrupar columnas por zonas y optimizar dentro de cada zona.
        """
        columnas_unicas = sorted(set(col for fila, col in paquetes))
        
        if len(columnas_unicas) <= 1:
            return columnas_unicas
        
        # Agrupar paquetes por columna
        paquetes_por_columna = {}
        for fila, col in paquetes:
            if col not in paquetes_por_columna:
                paquetes_por_columna[col] = []
            paquetes_por_columna[col].append(fila)
        
        # Agrupar columnas por zonas para minimizar transiciones
        zonas = self._optimizar_por_zonas(columnas_unicas, paquetes_por_columna, inicio)
        
        # Aplanar las zonas en un solo orden
        orden_final = []
        for zona in zonas:
            orden_final.extend(zona)
        
        return orden_final

    def _optimizar_por_zonas(self, columnas, paquetes_por_col, inicio):
        """
        Agrupa columnas en zonas y optimiza el orden de visita.
        Minimiza el número de transiciones entre zonas.
        """
        # Clasificar columnas por zona
        zonas_dict = {'izq': [], 'centro': [], 'der': []}
        
        for col in columnas:
            zona = self._obtener_zona_columna(col)
            zonas_dict[zona].append(col)
        
        # Determinar orden óptimo de zonas basado en posición inicial
        col_inicio = inicio[1]
        zona_inicio = self._obtener_zona_columna(col_inicio)
        
        # Estrategia: visitar zona actual primero, luego las adyacentes
        if zona_inicio == 'izq':
            orden_zonas = ['izq', 'centro', 'der']
        elif zona_inicio == 'der':
            orden_zonas = ['der', 'centro', 'izq']
        else:  # centro
            # Evaluar qué lado tiene más columnas
            if len(zonas_dict['izq']) >= len(zonas_dict['der']):
                orden_zonas = ['izq', 'centro', 'der']
            else:
                orden_zonas = ['der', 'centro', 'izq']
        
        # Construir orden final
        resultado = []
        for zona_nombre in orden_zonas:
            if zonas_dict[zona_nombre]:
                # Ordenar columnas dentro de cada zona
                columnas_zona = sorted(zonas_dict[zona_nombre])
                resultado.append(columnas_zona)
        
        return resultado

    def calcular_ruta_optima_salida(self, pos_final, punto_entrega):
        """
        Calcula la ruta óptima para salir hacia el punto de entrega.
        """
        fila_actual, col_actual = pos_final
        fila_entrega, col_entrega = punto_entrega
        
        # Si ya estamos en la columna de entrega
        if col_actual == col_entrega:
            costo = abs(fila_entrega - fila_actual) * self.costo_celda
            return [(fila_entrega, col_entrega)], costo
        
        # Verificar si necesitamos transición
        necesita_trans = self._necesita_transicion(col_actual, col_entrega)
        
        if not necesita_trans:
            # Ruta directa
            costo = self.calcular_costo_movimiento(
                fila_actual, col_actual, fila_entrega, col_entrega
            )
            return [(fila_entrega, col_entrega)], costo
        
        # Necesitamos transición: evaluar ambas opciones
        mejor_ruta = None
        mejor_costo = float('inf')
        
        for col_trans in self.COLUMNAS_TRANSICION:
            ruta = []
            costo = 0
            
            # 1. Ir a columna de transición
            if col_actual != col_trans:
                ruta.append((fila_actual, col_trans))
                costo += self.calcular_costo_movimiento(
                    fila_actual, col_actual, fila_actual, col_trans
                )
            
            # 2. Ajuste vertical en transición
            if fila_actual != fila_entrega:
                ruta.append((fila_entrega, col_trans))
                costo += abs(fila_entrega - fila_actual) * self.costo_celda
            
            # 3. Ir al punto de entrega
            if col_trans != col_entrega:
                ruta.append((fila_entrega, col_entrega))
                costo += self.calcular_costo_movimiento(
                    fila_entrega, col_trans, fila_entrega, col_entrega
                )
            
            if costo < mejor_costo:
                mejor_costo = costo
                mejor_ruta = ruta if ruta else [(fila_entrega, col_entrega)]
        
        return mejor_ruta, mejor_costo