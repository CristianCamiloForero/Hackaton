"""
Simulador de Robot Recolector de Almacén
Aplicación principal que orquesta la simulación, visualización y exportación de resultados
Versión interactiva con entrada de datos personalizada
"""

from robot import RobotAlmacen
from visualizador import Visualizador
from exportador import Exportador
from entrada import GestorEntrada
from config import PAQUETES, INICIO, COSTO_CELDA, COSTO_PASILLO


def main():
    """Función principal que ejecuta toda la simulación"""
    
    print("\n" + "=" * 60)
    print(" ROBOT RECOLECTOR DE ALMACÉN")
    print("=" * 60)
    
    # Mostrar menú
    opcion = GestorEntrada.mostrar_menu()
    
    if opcion == '1':
        # Usar datos por defecto
        print("\n✓ Usando configuración por defecto...")
        paquetes = PAQUETES
        inicio = INICIO
        costo_celda = COSTO_CELDA
        costo_pasillo = COSTO_PASILLO
    else:
        # Solicitar datos personalizados
        paquetes = GestorEntrada.solicitar_paquetes()
        inicio = GestorEntrada.solicitar_posicion_inicio()
        costos = GestorEntrada.solicitar_costos_personalizados()
        costo_celda = costos['celda']
        costo_pasillo = costos['pasillo']
    
    # Crear instancia del robot con datos personalizados
    robot = RobotAlmacen(
        paquetes=paquetes,
        inicio=inicio,
        costo_celda=costo_celda,
        costo_pasillo=costo_pasillo
    )
    
    # Ejecutar recolección
    robot.ejecutar_recoleccion()
    
    # Generar y mostrar tabla de pasos
    print("\n" + "=" * 60)
    print("TABLA DETALLADA DE MOVIMIENTOS")
    print("=" * 60)
    df_pasos = robot.generar_tabla_pasos()
    print(df_pasos.to_string(index=False))
    
    # Preguntar si visualizar y exportar
    print("\n" + "=" * 60)
    visualizar = input("¿Deseas generar visualizaciones? (s/n) [s]: ").strip().lower()
    
    if visualizar != 'n':
        print("GENERANDO VISUALIZACIONES...")
        print("=" * 60)
        Visualizador.visualizar_almacen(robot)
    
    exportar = input("\n¿Deseas exportar los resultados? (s/n) [s]: ").strip().lower()
    
    if exportar != 'n':
        print("\n" + "=" * 60)
        print("EXPORTANDO RESULTADOS...")
        print("=" * 60)
        Exportador.exportar_resultados(robot)
    
    print("\n" + "=" * 60)
    print("✅ PROCESO COMPLETADO EXITOSAMENTE")
    print("=" * 60)


if __name__ == "__main__":
    main()