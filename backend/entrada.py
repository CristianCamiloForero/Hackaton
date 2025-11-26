from .config import FILAS, COLUMNAS, PASILLOS, PAQUETES, INICIO, COSTO_CELDA, COSTO_PASILLO


class GestorEntrada:
    """Gestiona la entrada interactiva de datos del usuario (módulo backend)"""

    @staticmethod
    def solicitar_paquetes_interactivo():
        # Método original para consola, se mantiene para compatibilidad
        print("=" * 60)
        print("INGRESO DE PAQUETES A RECOGER")
        print("=" * 60)
        print(f"Dimensiones del almacén: {FILAS} filas (0-{FILAS-1}) x {COLUMNAS} columnas (0-{COLUMNAS-1})")
        print(f"Pasillos (columnas de costo mayor): {PASILLOS}")
        print()

        paquetes = []
        while True:
            try:
                cantidad = input("¿Cuántos paquetes deseas recoger? (1-20): ").strip()
                cantidad = int(cantidad)
                if cantidad < 1 or cantidad > 20:
                    print("❌ Por favor, ingresa un número entre 1 y 20")
                    continue
                break
            except ValueError:
                print("❌ Por favor, ingresa un número válido")

        ubicaciones_ingresadas = set()
        for i in range(cantidad):
            while True:
                try:
                    ubicacion = input(f"Paquete {i+1}: ").strip()
                    if ',' in ubicacion:
                        fila, col = map(int, ubicacion.split(','))
                    else:
                        partes = ubicacion.split()
                        if len(partes) != 2:
                            print("❌ Formato inválido. Usa 'fila,columna' o 'fila columna'")
                            continue
                        fila, col = map(int, partes)
                    if fila < 0 or fila >= FILAS or col < 0 or col >= COLUMNAS:
                        print(f"❌ Posición fuera de rango. Usa: 0-{FILAS-1} para filas, 0-{COLUMNAS-1} para columnas")
                        continue
                    if (fila, col) in ubicaciones_ingresadas:
                        print("❌ Esta ubicación ya fue ingresada")
                        continue
                    ubicaciones_ingresadas.add((fila, col))
                    paquetes.append([fila, col])
                    print(f"✓ Paquete {i+1} ubicado en ({fila}, {col})")
                    break
                except ValueError:
                    print("❌ Por favor, ingresa números válidos")

        print("\n" + "=" * 60)
        print(f"Se han ingresado {len(paquetes)} paquetes:")
        for i, paq in enumerate(paquetes, 1):
            print(f"  {i}. ({paq[0]}, {paq[1]})")
        print("=" * 60)
        return paquetes

    @staticmethod
    def validar_paquetes(paquetes):
        """Valida una lista de paquetes recibida por API"""
        validos = []
        for fila, col in paquetes:
            if 0 <= fila < FILAS and 0 <= col < COLUMNAS:
                validos.append([int(fila), int(col)])
        return validos

    @staticmethod
    def validar_inicio(inicio):
        if not isinstance(inicio, (list, tuple)) or len(inicio) != 2:
            return [0, 0]
        fila, col = inicio
        if 0 <= fila < FILAS and 0 <= col < COLUMNAS:
            return [int(fila), int(col)]
        return [0, 0]

    @staticmethod
    def validar_costos(costos):
        celda = float(costos.get('celda', COSTO_CELDA))
        pasillo = float(costos.get('pasillo', COSTO_PASILLO))
        return {'celda': celda, 'pasillo': pasillo}
