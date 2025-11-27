# 🚀 Simulador Robot de Almacén - Guía Rápida

## Inicio Rápido

### Opción 1: Terminal con scripts (Recomendado)

#### Terminal 1 - Iniciar Backend
```powershell
cd C:\Users\Aprendiz\Downloads\Hackaton
.\start_backend.ps1
```

#### Terminal 2 - Iniciar Frontend
```powershell
cd C:\Users\Aprendiz\Downloads\Hackaton
.\start_frontend.ps1
```

#### Acceder a la aplicación
- **Frontend**: http://127.0.0.1:8080
- **Backend API Docs**: http://127.0.0.1:5000/docs

---

### Opción 2: Manual (Sin scripts)

#### Terminal 1 - Backend
```powershell
cd C:\Users\Aprendiz\Downloads\Hackaton
python -m uvicorn backend.app:app --reload --host 127.0.0.1 --port 5000
```

#### Terminal 2 - Frontend
```powershell
cd C:\Users\Aprendiz\Downloads\Hackaton\frontend
python -m http.server 8080 --bind 127.0.0.1
```

---

## 📋 Características

### 1. **Simulación Simple**
- Agrega paquetes (ubicaciones fila x columna)
- Visualiza la ruta óptima del robot
- Exporta resultados a Excel

### 2. **Conteo Cíclico** ✨ (Nuevo)
- **Entrada amigable**: SKU, Cantidad, Ubicación, Movimientos, Conteos históricos, Criticidad
- **Generación de plan**: Prioriza referencias por:
  - Faltantes (cuántos conteos faltan para llegar a mínimo 5/año)
  - Movimientos (actividad)
  - Criticidad (importancia)
- **Resultados**:
  - Tabla de plan priorizado
  - Inventario total (suma de cantidades)
  - Salidas (suma de movimientos)
  - Fechas planificadas para cada conteo
- **Exportación**: Descarga como CSV (fallback local) o Excel (si backend disponible)

---

## 🎯 Usar Conteo Cíclico

1. **Abrir Frontend** → http://127.0.0.1:8080
2. **Clic en "Iniciar Simulación"**
3. **Ir a pestaña "Conteo Cíclico"**
4. **Opción A - Cargar Inventario Quemado** (Demo rápida):
   - Botón: "Cargar Inventario Quemado"
   - Se llenan 6 SKUs de ejemplo con cantidades realistas
   
5. **Opción B - Agregar manualmente**:
   - SKU: `AUDIO-001`
   - Cantidad: `120`
   - Fila: `1` (rango 1-12)
   - Col: `1` (rango 1-9)
   - Movimientos: `12`
   - Conteos ult. 365: `1`
   - Criticidad: `3` (escala 1-5)
   - Click: "Agregar"

6. **Generar Plan**:
   - Botón: "Generar Plan"
   - Espera a que aparezcan resultados

7. **Ver Resultados**:
   - Resumen: Total items, con faltantes, conteos programados, **inventario total**, **salidas**
   - Tabla: Plan priorizado con fechas

8. **Exportar**:
   - Botón: "Exportar a Excel"
   - Se descarga `plan_conteo.csv` o `plan_conteo.xlsx`

---

## ⚙️ Configuración

### Backend (`backend/config.py`)
- **FILAS**: 9 (0-8)
- **COLUMNAS**: 12 (0-11)
- **PASILLOS**: Columnas 1, 4, 7, 10
- **ALMACENES** (Zonas):
  - Audio (cols 0-2) → Azul
  - Cómputo (cols 3-5) → Verde
  - Refrigeración (cols 6-8) → Rojo
  - Aire Acondicionado (cols 9-11) → Púrpura

### Pesos de Conteo (Personalizables)
- **Faltantes**: 100 (cuánto peso al déficit)
- **Movimientos**: 1 (actividad)
- **Criticidad**: 50 (importancia)

---

## 🛠️ Solución de Problemas

### "No genera nada al iniciar el plan"
**Solución**: 
- Verifica que el frontend tenga filas agregadas (botón "Cargar Inventario Quemado" es lo más rápido)
- Si el backend no está disponible, el plan se genera **localmente en el navegador** (sin servidor)
- El resultado se puede exportar como CSV local sin necesidad de backend

### "Error al exportar"
- Si Backend disponible → Usa Excel (openpyxl)
- Si Backend no disponible → Usa CSV local
- En ambos casos descargas correctamente

### "Port 5000 ya está en uso"
```powershell
# Encontrar qué usa el puerto
Get-Process | Where-Object {$_.Handles -match "5000"}

# Usar otro puerto
python -m uvicorn backend.app:app --host 127.0.0.1 --port 5001
```

---

## 📦 Dependencias

### Instaladas
```
fastapi
uvicorn
openpyxl (opcional, para Excel backend)
```

### Sin dependencias (Frontend funciona localmente)
- Motor de conteo cíclico: **100% JavaScript**
- Exportación CSV: **100% JavaScript**
- Cero requerimientos externos para funcionamiento básico

---

## 📊 Flujo de Datos

```
Usuario UI Frontend
    ↓
Ingresa SKU, Cantidad, Ubicación
    ↓
Click "Generar Plan"
    ↓
Intenta Backend /cycle-count
    ├→ ✓ Disponible: Usa backend Python
    └→ ✗ Falla: Usa motor JavaScript local
    ↓
Calcula Totales (Inventario, Salidas)
    ↓
Muestra Tabla Priorizada + Estadísticas
    ↓
Click "Exportar a Excel"
    ├→ ✓ Backend disponible: XLSX (openpyxl)
    └→ ✗ Backend falla: CSV (JavaScript)
    ↓
Descarga Archivo
```

---

## 🔄 Ejemplo de Plan Generado

**Entrada**:
- AUDIO-001: 120 unidades, 1 conteo en 365 días, criticidad 3
- COMP-101: 230 unidades, 3 conteos, criticidad 2

**Salida**:
| SKU | Fila | Col | Faltantes | Score | Fechas |
|-----|------|-----|-----------|-------|--------|
| AUDIO-001 | 0 | 0 | 4 | 450 | 2025-11-28, 2025-12-27, ... |
| COMP-101 | 2 | 4 | 2 | 250 | 2025-12-05, 2026-01-04 |

**Estadísticas**:
- Total items: 2
- Items con faltantes: 2
- Conteos programados: 6
- **Inventario total: 350 unidades**
- **Salidas (movimientos): 17 traslados**

---

## ✨ Características Futuras

- [ ] Edición inline de filas en la tabla
- [ ] Asignación por equipo/turno
- [ ] Calendario visual de conteos
- [ ] Excel con múltiples hojas (resumen + detalle)

---

**Versión**: 1.0  
**Última actualización**: 27 de Noviembre, 2025
