from .config import FILAS, COLUMNAS, PASILLOS, PAQUETES, INICIO, COSTO_CELDA, COSTO_PASILLO


class Exportador:
    """Exportador (backend) genera CSV y TXT sin forzar pandas"""

    @staticmethod
    def exportar_resultados(robot):
        # Intentar Excel con pandas si disponible
        try:
            import pandas as pd
            df = pd.DataFrame(robot.pasos)
            df.to_excel('reporte_recoleccion.xlsx', index=False, engine='openpyxl')
            print("  - reporte_recoleccion.xlsx")
        except Exception:
            pass
        Exportador._exportar_csv(robot)
        Exportador._exportar_resumen_txt(robot)
        print("\n✓ Reportes exportados exitosamente")

    @staticmethod
    def _exportar_csv(robot):
        try:
            import pandas as pd
            df = pd.DataFrame(robot.pasos)
            df.to_csv('reporte_recoleccion.csv', index=False)
            print("  - reporte_recoleccion.csv")
        except Exception:
            with open('reporte_recoleccion.csv', 'w', encoding='utf-8') as f:
                if not robot.pasos:
                    return
                encabezados = list(robot.pasos[0].keys())
                f.write(','.join(encabezados) + '\n')
                for paso in robot.pasos:
                    valores = [str(paso[col]).replace(',', ';') for col in encabezados]
                    f.write(','.join(valores) + '\n')
            print("  - reporte_recoleccion.csv")

    @staticmethod
    def _exportar_resumen_txt(robot):
        with open('resumen_recoleccion.txt', 'w', encoding='utf-8') as f:
            f.write("=" * 70 + "\n")
            f.write("RESUMEN DE RECOLECCIÓN DE ALMACÉN\n")
            f.write("=" * 70 + "\n\n")
            f.write("CONFIGURACIÓN DEL ALMACÉN:\n")
            f.write("-" * 70 + "\n")
            f.write(f"  • Dimensiones: {FILAS} filas x {COLUMNAS} columnas\n")
            f.write(f"  • Pasillos en columnas: {PASILLOS}\n")
            f.write(f"  • Paquetes a recolectar: {len(robot.paquetes)}\n")
            f.write(f"  • Posición inicial: ({robot.inicio[0]}, {robot.inicio[1]})\n\n")
            f.write("RESULTADOS DE LA RECOLECCIÓN:\n")
            f.write("-" * 70 + "\n")
            f.write(f"  • Costo total: {robot.costo_total:.2f} unidades\n")
            f.write(f"  • Total de movimientos: {len(robot.pasos)}\n")
            f.write(f"  • Posición final: ({robot.fila_actual}, {robot.col_actual})\n\n")
            f.write("COSTOS POR TIPO:\n")
            f.write("-" * 70 + "\n")
            f.write(f"  • Costo por celda normal: {robot.costo_celda_valor}\n")
            f.write(f"  • Costo por pasillo: {robot.costo_pasillo_valor}\n\n")
            if robot.pasos:
                costos = [paso['Costo'] for paso in robot.pasos]
                f.write("ESTADÍSTICAS:\n")
                f.write("-" * 70 + "\n")
                f.write(f"  • Costo promedio por movimiento: {sum(costos)/len(costos):.2f}\n")
                f.write(f"  • Costo máximo en movimiento: {max(costos):.2f}\n")
                f.write(f"  • Costo mínimo en movimiento: {min(costos):.2f}\n\n")
                movimientos_pasillos = sum(1 for paso in robot.pasos if paso['Es Pasillo'] == 'Sí')
                f.write("MOVIMIENTOS:\n")
                f.write("-" * 70 + "\n")
                f.write(f"  • Movimientos en pasillos: {movimientos_pasillos}\n")
                f.write(f"  • Movimientos en celdas normales: {len(robot.pasos) - movimientos_pasillos}\n\n")
            f.write("TABLA DETALLADA DE MOVIMIENTOS:\n")
            f.write("-" * 70 + "\n")
            if robot.pasos:
                encabezados = list(robot.pasos[0].keys())
                anchos = {col: max(len(col), 12) for col in encabezados}
                encabezado_line = " | ".join(f"{col:{anchos[col]}}" for col in encabezados)
                f.write(encabezado_line + "\n")
                f.write("-" * len(encabezado_line) + "\n")
                for paso in robot.pasos:
                    valores = [str(paso[col]) for col in encabezados]
                    fila = " | ".join(f"{val:{anchos[encabezados[i]]}}" for i, val in enumerate(valores))
                    f.write(fila + "\n")
            f.write("\n" + "=" * 70 + "\n")
        print("  - resumen_recoleccion.txt")

    @staticmethod
    def export_cycle_plan_bytes(plan):
        """Genera un archivo Excel (bytes) a partir de un plan de conteo.

        Si no está disponible `openpyxl`, cae a CSV (utf-8) y devuelve bytes.
        """
        import io
        headers = ['SKU', 'Fila', 'Col', 'ConteosUlt365dias', 'Faltantes', 'Score', 'FechasPlanificadas']

        # Intentar openpyxl
        try:
            from openpyxl import Workbook
            wb = Workbook()
            ws = wb.active
            ws.title = 'Plan Conteo'
            ws.append(headers)
            for p in plan:
                ws.append([
                    p.get('sku'),
                    p.get('fila'),
                    p.get('col'),
                    p.get('conteos_ultimos_365dias'),
                    p.get('faltantes'),
                    float(p.get('score') or 0),
                    ', '.join(p.get('fechas_planificadas') or [])
                ])
            bio = io.BytesIO()
            wb.save(bio)
            bio.seek(0)
            return bio.read()
        except Exception:
            # Fallback a CSV
            import csv
            sio = io.StringIO()
            writer = csv.writer(sio)
            writer.writerow(headers)
            for p in plan:
                writer.writerow([
                    p.get('sku'),
                    p.get('fila'),
                    p.get('col'),
                    p.get('conteos_ultimos_365dias'),
                    p.get('faltantes'),
                    p.get('score'),
                    ';'.join(p.get('fechas_planificadas') or [])
                ])
            return sio.getvalue().encode('utf-8')
