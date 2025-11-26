from .config import FILAS, COLUMNAS, PASILLOS, INICIO


class Visualizador:
    """Visualización en consola (backend)"""

    @staticmethod
    def visualizar_almacen_ascii(robot):
        print("\n" + "=" * 80)
        print("VISUALIZACIÓN DEL ALMACÉN (Vista ASCII)")
        print("=" * 80)
        visual = [['.' for _ in range(COLUMNAS)] for _ in range(FILAS)]
        for col in PASILLOS:
            for fila in range(FILAS):
                visual[fila][col] = '═'
        for fila, col in robot.paquetes:
            visual[fila][col] = 'P'
        for fila, col in robot.ruta[1:-1]:
            if visual[fila][col] == '.':
                visual[fila][col] = '·'
        visual[INICIO[0]][INICIO[1]] = 'S'
        if len(robot.ruta) > 0:
            fila_final, col_final = robot.ruta[-1]
            visual[fila_final][col_final] = 'E'
        print("   ", end="")
        for j in range(COLUMNAS):
            print(f"{j:2d}", end="")
        print()
        for i in range(FILAS):
            print(f"{i:2d} ", end="")
            for j in range(COLUMNAS):
                print(f" {visual[i][j]}", end="")
            print()
        print("\n" + "-" * 80)
        print("LEYENDA:")
        print("  S = Inicio (Start)")
        print("  E = Fin (End)")
        print("  P = Paquete")
        print("  · = Ruta del robot")
        print("  ═ = Pasillo (costo mayor)")
        print("  . = Celda vacía")
        print("=" * 80)

    @staticmethod
    def visualizar_estadisticas(robot):
        print("\n" + "=" * 80)
        print("ESTADÍSTICAS DE LA RECOLECCIÓN")
        print("=" * 80)
        print(f"\n📊 RESUMEN GENERAL:")
        print(f"  • Costo total: {robot.costo_total:.2f} unidades")
        print(f"  • Total de movimientos: {len(robot.pasos)}")
        print(f"  • Paquetes recogidos: {len(robot.paquetes)}")
        print(f"  • Posición inicial: ({robot.inicio[0]}, {robot.inicio[1]})")
        print(f"  • Posición final: ({robot.fila_actual}, {robot.col_actual})")
        if robot.pasos:
            costos = [paso['Costo'] for paso in robot.pasos]
            costo_promedio = sum(costos) / len(costos)
            costo_maximo = max(costos)
            costo_minimo = min(costos)
            print(f"\n💰 ANÁLISIS DE COSTOS:")
            print(f"  • Costo promedio por movimiento: {costo_promedio:.2f}")
            print(f"  • Costo máximo en movimiento: {costo_maximo:.2f}")
            print(f"  • Costo mínimo en movimiento: {costo_minimo:.2f}")
            movimientos_pasillos = sum(1 for paso in robot.pasos if paso['Es Pasillo'] == 'Sí')
            movimientos_normales = len(robot.pasos) - movimientos_pasillos
            print(f"\n🚚 TIPOS DE MOVIMIENTOS:")
            print(f"  • Movimientos en pasillos: {movimientos_pasillos}")
            print(f"  • Movimientos en celdas normales: {movimientos_normales}")
        print("\n" + "=" * 80)

    @staticmethod
    def visualizar_ruta_detallada(robot):
        print("\n" + "=" * 80)
        print("RUTA DETALLADA DEL ROBOT")
        print("=" * 80)
        print("\n📍 Secuencia de posiciones visitadas:")
        for idx, (fila, col) in enumerate(robot.ruta):
            if idx == 0:
                print(f"  {idx:2d}. ({fila}, {col}) - INICIO")
            elif idx == len(robot.ruta) - 1:
                print(f"  {idx:2d}. ({fila}, {col}) - FIN")
            else:
                print(f"  {idx:2d}. ({fila}, {col})")
        print("\n" + "=" * 80)

    @staticmethod
    def visualizar_almacen(robot, guardar=False):
        Visualizador.visualizar_almacen_ascii(robot)
        Visualizador.visualizar_estadisticas(robot)
        Visualizador.visualizar_ruta_detallada(robot)
        print("\n✓ Visualización completada")
