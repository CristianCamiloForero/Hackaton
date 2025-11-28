# Simulación Robot de Almacén

Sistema interactivo para simular la recolección de paquetes en un almacén automático. El proyecto incluye un backend en Python con FastAPI y un frontend web moderno con interfaz responsiva.

## 📋 Características

- **Simulación de rutas optimizadas**: Calcula la ruta más eficiente para recoger paquetes en un almacén.
- **Backend API RESTful**: Endpoints para ejecutar simulaciones, obtener valores por defecto y exportar resultados.
- **Frontend interactivo**: Interfaz web moderna (blanco + café) con formularios, visualización del almacén y tabla de movimientos.
- **Exportación a Excel**: Genera reportes en formato Excel de los movimientos realizados.
- **Visualización de almacén**: Grid interactivo que muestra inicio, paquetes, y posición final.
- **Sin dependencias externas obligatorias**: Funciona sin pandas/matplotlib si no están instalados.

## 🛠️ Requisitos Previos

- **Python 3.8+** (probado con Python 3.12)
- **pip** (gestor de paquetes de Python)

## 📦 Instalación

### 1. Clonar o descargar el proyecto

```bash
cd c:\Users\Aprendiz\Downloads\Hackaton
```

### 2. Instalar dependencias (opcional pero recomendado)

```powershell
pip install fastapi uvicorn pandas matplotlib openpyxl
```

**Nota**: Si no instalas estas dependencias, el backend seguirá funcionando pero:
- La exportación a Excel fallará (pero se puede usar CSV)
- La visualización ASCII será la única disponible

Para solo lo esencial:

```powershell
pip install fastapi uvicorn
```

## 🚀 Ejecución

### Opción 1: Ejecutar Backend y Frontend por separado (Recomendado)

#### Terminal 1 - Backend (API)

```powershell
# Desde la raíz del proyecto
python -m uvicorn backend.app:app --reload --host 127.0.0.1 --port 5000
```

El backend estará disponible en `http://127.0.0.1:5000`

#### Terminal 2 - Frontend (Interfaz web)

```powershell
# Desde la raíz del proyecto
cd .\frontend
python -m http.server 8080 --bind 127.0.0.1
```

El frontend estará disponible en `http://127.0.0.1:8080`

### Opción 2: Ejecutar ambos con un script

```powershell
python run_all.py
```

Este script inicia automáticamente:
- Backend en `http://127.0.0.1:5000`
- Frontend en `http://127.0.0.1:8080`

### Opción 3: Ejecutar el simulador en línea de comandos

```powershell
python Main.py
```

Este modo permite ingresar parámetros interactivamente en la consola.

## 📖 Uso

### Desde el Frontend Web

1. Abre `http://127.0.0.1:8080` en tu navegador
2. Haz clic en el botón **"Simular"** (esquina superior)
3. **Cargar valores por defecto** (opcional): Carga un ejemplo predefinido
4. **Agregar Paquetes**: 
   - Ingresa la fila y columna de cada paquete
   - Usa el botón **"+ Agregar Paquete"** para añadir más
5. **Simular**: Ejecuta la simulación con los parámetros ingresados
6. **Resultados**: 
   - Visualiza el costo total, movimientos y posición final
   - Observa el grid del almacén con colores diferenciados:
     - **Verde**: Almacenamiento normal
     - **Amarillo**: Pasillos (mayor costo)
     - **I**: Posición de inicio
     - **P**: Ubicación de paquetes
     - **F**: Posición final
   - Revisa la tabla detallada de movimientos
7. **Exportar a Excel**: Descargar el reporte en formato .xlsx

### Desde la Línea de Comandos

```powershell
python Main.py
```

Sigue las instrucciones interactivas:
- Ingresa cantidad de paquetes
- Define ubicación de cada paquete (fila, columna)
- Elige si deseas costos personalizados
- Visualiza resultados y tablas automáticamente

## 🔌 Endpoints de la API

### GET `/defaults`
Retorna los valores por defecto de la simulación.

**Respuesta:**
```json
{
  "paquetes": [[2,0], [6,3], [0,5], ...],
  "inicio": [0, 0],
  "costo_celda": 2.7,
  "costo_pasillo": 5.0
}
```

### POST `/simulate`
Ejecuta una simulación con parámetros específicos.

**Cuerpo de la solicitud:**
```json
{
  "paquetes": [[2,0], [6,3], [0,5]],
  "inicio": [0, 0],
  "costo_celda": 2.7,
  "costo_pasillo": 5.0
}
```

**Respuesta:**
```json
{
  "total_cost": 190.10,
  "pos_final": [8, 11],
  "pasos": [
    {
      "Desde": "(0,0)",
      "Hacia": "(2,0)",
      "Pasos": 2,
      "Costo": 5.4,
      "Es Pasillo": "No",
      "Columna Vacía": "No",
      "Acumulado": 5.4,
      "Descripción": "Moverse horizontalmente..."
    },
    ...
  ],
  "ruta": [[0,0], [2,0], ...]
}
```

### POST `/export`
Genera y descarga un archivo Excel con el reporte de la simulación.

**Parámetros**: Iguales a `/simulate`

**Respuesta**: Archivo Excel descargable

### POST `/consolidate`
**Nuevo**: Consolida múltiples órdenes de pedido en una lista de picking optimizada minimizando distancia de recorrido.

**Cuerpo de la solicitud:**
```json
{
  "ordenes": [
    {
      "id_orden": "ORD001",
      "items": [[2, 0, 1, "SKU-001"], [6, 3, 2, "SKU-002"]]
    },
    {
      "id_orden": "ORD002", 
      "items": [[0, 5, 1, "SKU-003"], [3, 6, 3, "SKU-004"]]
    }
  ]
}
```

**Respuesta:**
```json
{
  "picking_list": [
    {
      "fila": 2,
      "col": 0,
      "cantidad": 1,
      "skus": {"SKU-001": 1},
      "ordenes": ["ORD001"]
    },
    ...
  ],
  "rutas": [0, 3, 5, 6, 8, 9, 11],
  "estadisticas": {
    "total_items": 10,
    "ordenes": 2,
    "ubicaciones_unicas": 7,
    "distancia_estimada": 45.2,
    "columnas_visitadas": [0, 3, 5, 6, 8, 9, 11]
  }
}
```

### GET `/warehouse-config`
Retorna la configuración del almacén incluyendo ubicación de pasillos.

**Respuesta:**
```json
{
  "filas": 9,
  "columnas": 12,
  "pasillos": [1, 4, 7, 10],
  "costo_celda": 2.7,
  "costo_pasillo": 5.0
}
```

### POST `/cycle-count`
Genera un plan priorizado de conteo cíclico que asegura que cada referencia sea inventariada al menos `frecuencia_minima` veces en el periodo (por defecto 5 veces en 365 días).

**Cuerpo de la solicitud (ejemplo):**
```json
{
  "ubicaciones": [
    {"fila": 2, "col": 0, "sku": "SKU-001", "movimientos": 10, "conteos_ultimos_365dias": 1},
    {"fila": 4, "col": 3, "sku": "SKU-002", "movimientos": 2, "conteos_ultimos_365dias": 5}
  ],
  "frecuencia_minima": 5
}
```

**Respuesta (ejemplo):**
```json
{
  "plan": [
    {
      "sku": "SKU-001",
      "fila": 2,
      "col": 0,
      "conteos_ultimos_365dias": 1,
      "faltantes": 4,
      "score": 400,
      "fechas_planificadas": ["2025-11-27", "2026-01-26", "2026-03-27", "2026-05-26"]
    },
    ...
  ],
  "estadisticas": {
    "total_items": 2,
    "items_con_faltantes": 1,
    "total_counts_scheduled": 4
  }
}
```

## 📁 Estructura del Proyecto

```
Hackaton/
├── Main.py                 # Punto de entrada interactivo (CLI)
├── run_all.py             # Script para ejecutar backend + frontend
├── run_frontend.ps1       # Script PowerShell para ejecutar frontend
├── requirements.txt       # Dependencias del proyecto
├── README.md              # Este archivo
│
├── backend/               # Módulo del backend (FastAPI)
│   ├── __init__.py
│   ├── app.py            # Aplicación FastAPI y endpoints
│   ├── config.py         # Configuración y constantes
│   ├── robot.py          # Clase RobotAlmacen (simulador)
│   ├── entrada.py        # Validación de entrada y CLI
│   ├── optimizador.py    # Algoritmos de optimización de rutas
│   ├── visualizador.py   # Visualización ASCII del almacén
│   ├── exportador.py     # Exportación de resultados
│   └── consolidador.py   # NUEVO: Consolidación de órdenes de picking
│
└── frontend/              # Interfaz web
    ├── index.html        # HTML principal
    ├── app.js            # Lógica JavaScript
    ├── styles.css        # Estilos (incluidos en index.html)
    └── favicon.ico       # Icono de la página
```

## ⚙️ Configuración

### Parámetros de Simulación

Modifica `backend/config.py` para cambiar parámetros globales:

```python
FILAS = 9                  # Número de filas del almacén
COLUMNAS = 12              # Número de columnas
PASILLOS = [1, 4, 7, 10]   # Índices de columnas pasillos (costo mayor)
COSTO_CELDA = 2.7          # Costo por celda normal
COSTO_PASILLO = 5.0        # Costo por celda en pasillo
PAQUETES = [...]           # Paquetes por defecto
INICIO = [0, 0]            # Posición de inicio
```

## 🐛 Solución de Problemas

### Error: "No se puede cargar el archivo... porque la ejecución de scripts está deshabilitada"

**Solución** (en PowerShell):
```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

### Error: "ModuleNotFoundError: No module named 'fastapi'"

**Solución**:
```powershell
pip install fastapi uvicorn
```

### El frontend no conecta al backend (error CORS)

Asegúrate de que:
1. El backend esté ejecutando en `http://127.0.0.1:5000`
2. El frontend acceda a `http://127.0.0.1:8080` (no `localhost` directamente)

### La exportación a Excel falla

Instala las dependencias requeridas:
```powershell
pip install pandas openpyxl
```

## 📝 Ejemplo de Uso Completo

1. **Inicia el backend:**
   ```powershell
   python -m uvicorn backend.app:app --reload --host 127.0.0.1 --port 5000
   ```

2. **En otra terminal, inicia el frontend:**
   ```powershell
   cd .\frontend
   python -m http.server 8080 --bind 127.0.0.1
   ```

3. **Abre el navegador:**
   ```
   http://127.0.0.1:8080
   ```

4. **Interactúa:**
   - Haz clic en "Simular"
   - Haz clic en "Cargar valores por defecto"
   - Haz clic en "Simular" nuevamente
   - Revisa los resultados y exporta a Excel si lo deseas

## 🎯 Características Técnicas

### Backend
- **Framework**: FastAPI
- **Servidor**: Uvicorn
- **Tipo de archivo**: Python 3.8+
- **CORS**: Habilitado para desarrollo

### Frontend
- **HTML5**: Estructura semántica
- **CSS3**: Estilos modernos (grid, flexbox)
- **JavaScript (ES6)**: Lógica interactiva sin frameworks externos

### Simulador
- **Optimización**: Algoritmo greedy + búsqueda exhaustiva para pequeños conjuntos
- **Visualización**: Grid interactivo en el frontend, ASCII en terminal
- **Exportación**: Excel (pandas + openpyxl) o CSV/TXT (fallback)

### Consolidación de Picking (Nuevo)
- **Algoritmo**: Agrupa paquetes por columna y ordena de arriba a abajo
- **Optimización**: Minimiza distancia de recorrido en picking tasks
- **Entrada**: Múltiples órdenes con SKUs y cantidades
- **Salida**: Lista consolidada y ordenada, rutas optimizadas, estadísticas

**Flujo de Consolidación:**
1. Recibe múltiples órdenes de pedido
2. Consolida items duplicados en la misma ubicación
3. Agrupa por columnas (zonas)
4. Ordena dentro de cada zona (fila ascendente)
5. Calcula distancia manhattan estimada
6. Retorna picking list optimizada con rutas y estadísticas

## 📄 Licencia

Proyecto educativo desarrollado como parte de un hackathon.

## ✅ Estado final y notas de pruebas

- Se integraron las correcciones detectadas durante la fase de pruebas:
  - `backend/robot.py` refactorizado para evitar recursión y descomponer movimientos diagonales o que crucen pasillos mediante columnas de transición (`0` y `8`).
  - `backend/optimizador.py` ajustado para devolver (pasos, costo) y evaluar rutas vía columnas de transición.
  - Frontend (`frontend/app.js`) preparado para renderizar la `ruta` con segmentos ortogonales (L-shaped) y puntos clave numerados.
- Se añadieron utilidades para validar la ruta generada localmente:
  - `scripts/validate_response.py` y `scripts/validate_now.py` para validar `simulate_response.json`.
  - `tests/utils.py` contiene el validador reutilizable (diagonales y cruces de pasillos).

Sigue las instrucciones en la sección "🚀 Ejecución" para levantar el backend y el frontend. Si quieres que haga un commit o cree un `release` con estos cambios, dime y lo preparo.
---

**¿Preguntas o sugerencias?** Revisa los archivos del proyecto o ejecuta `python Main.py` para más detalles.
