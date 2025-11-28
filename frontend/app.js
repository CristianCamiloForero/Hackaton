// API Configuration
const apiBase = 'http://127.0.0.1:5000';

// Warehouse Configuration
const PASILLOS = [1, 4, 7, 10]; // Columnas que son pasillos
let ALMACENES = []; // Cargado desde backend

// DOM Elements
const startBtn = document.getElementById('startBtn');
const ctaSection = document.getElementById('ctaSection');
const formSection = document.getElementById('formSection');
const resultsSection = document.getElementById('resultsSection');
const simulationForm = document.getElementById('simulationForm');
const cancelBtn = document.getElementById('cancelBtn');
const loadDefaultsBtn = document.getElementById('loadDefaultsBtn');
const runBtn = document.getElementById('runBtn');
const exportBtn = document.getElementById('exportBtn');
const backToFormBtn = document.getElementById('backToFormBtn');
const addTabBtn = document.getElementById('addTabBtn');
const tabsHeader = document.getElementById('tabsHeader');
const tabsContent = document.getElementById('tabsContent');
const summaryList = document.getElementById('summaryList');
const notification = document.getElementById('notification');
const notificationIcon = document.getElementById('notificationIcon');
const notificationText = document.getElementById('notificationText');
const resultStats = document.getElementById('resultStats');
const tableArea = document.getElementById('tableArea');
const warehouseGrid = document.getElementById('warehouseGrid');
const modeTabs = document.querySelectorAll('.mode-tab');
const packageSummary = document.getElementById('packageSummary');
// Consolidation UI removed (JSON input not exposed to users)
const consolidateSection = document.getElementById('consolidateSection');
const ordersInput = document.getElementById('ordersInput');
const loadSampleOrdersBtn = document.getElementById('loadSampleOrdersBtn');
const cycleSection = document.getElementById('cycleSection');
const cycleInput = document.getElementById('cycleInput');
const loadCycleDefaultsBtn = document.getElementById('loadCycleDefaultsBtn');
const cycleFreqInput = document.getElementById('cycleFreqInput');
const weightFaltantes = document.getElementById('weightFaltantes');
const weightMovimientos = document.getElementById('weightMovimientos');
const weightCriticidad = document.getElementById('weightCriticidad');
const runCycleBtn = document.getElementById('runCycleBtn');
const cycleResults = document.getElementById('cycleResults');
const addCycleRowBtn = document.getElementById('addCycleRowBtn');
const clearCycleBtn = document.getElementById('clearCycleBtn');
const cycleTableBody = document.querySelector('#cycleTable tbody');
const inputSKU = document.getElementById('inputSKU');
const inputFila = document.getElementById('inputFila');
const inputCol = document.getElementById('inputCol');
const inputMov = document.getElementById('inputMov');
const inputConteos = document.getElementById('inputConteos');
const inputCrit = document.getElementById('inputCrit');
const inputCantidad = document.getElementById('inputCantidad');
const loadInventoryBtn = document.getElementById('loadInventoryBtn');

// Hardcoded inventory sample (quemado) to simulate stock review
const HARDCODED_INVENTORY = [
  { sku: 'AUDIO-001', almacen: 'Audio', cantidad: 120, fila: 0, col: 0 },
  { sku: 'AUDIO-002', almacen: 'Audio', cantidad: 45, fila: 1, col: 2 },
  { sku: 'COMP-101', almacen: 'Cómputo', cantidad: 230, fila: 2, col: 4 },
  { sku: 'COMP-102', almacen: 'Cómputo', cantidad: 12, fila: 3, col: 5 },
  { sku: 'REFR-555', almacen: 'Refrigeración', cantidad: 6, fila: 5, col: 7 },
  { sku: 'AC-900', almacen: 'Aire Acondicionado', cantidad: 85, fila: 8, col: 10 }
];

// State
let packageCount = 1;
let lastPayload = null;
let lastResult = null;
let currentMode = 'simple'; // 'simple' or 'consolidate'
let lastCyclePlan = null;

// Initialize
init();

function init() {
  setupEventListeners();
  loadWarehouseConfig();
  // Create the first package tab
  addPackageTab();
  updateSummary();
}

async function loadWarehouseConfig() {
  try {
    const res = await fetch(apiBase + '/warehouse-config');
    const config = await res.json();
    if (config.pasillos) {
      window.PASILLOS = config.pasillos;
    }
    if (config.almacenes) {
      window.ALMACENES = config.almacenes;
    }
  } catch (err) {
    console.warn('No se pudo cargar configuración del almacén:', err);
  }
}

function setupEventListeners() {
  startBtn.addEventListener('click', showForm);
  cancelBtn.addEventListener('click', hideForm);
  backToFormBtn.addEventListener('click', backToForm);
  loadDefaultsBtn.addEventListener('click', loadDefaults);
  addTabBtn.addEventListener('click', addPackageTab);
  simulationForm.addEventListener('submit', runSimulation);
  exportBtn.addEventListener('click', exportToExcel);
  
  // Mode tabs
  modeTabs.forEach(tab => {
    tab.addEventListener('click', (e) => {
      e.preventDefault();
      switchMode(tab.dataset.mode);
    });
  });
  
  // consolidation JSON UI removed: do not register JSON handlers
  if (loadSampleOrdersBtn) {
    // kept for backward compatibility (hidden element); no-op
  }
  if (loadCycleDefaultsBtn) loadCycleDefaultsBtn.addEventListener('click', loadCycleDefaults);
  if (runCycleBtn) runCycleBtn.addEventListener('click', runCycleCount);
  if (addCycleRowBtn) addCycleRowBtn.addEventListener('click', addCycleRow);
  if (clearCycleBtn) clearCycleBtn.addEventListener('click', clearCycleTable);
  if (loadInventoryBtn) loadInventoryBtn.addEventListener('click', loadInventorySample);
}

// Navigation Functions
function showForm() {
  ctaSection.style.display = 'none';
  formSection.classList.add('active');
  resultsSection.classList.remove('active');
}

function hideForm() {
  formSection.classList.remove('active');
  resultsSection.classList.remove('active');
  ctaSection.style.display = 'block';
}

function backToForm() {
  resultsSection.classList.remove('active');
  formSection.classList.add('active');
}

// Mode Switching
function switchMode(mode) {
  currentMode = mode;
  
  // Update tab highlighting
  modeTabs.forEach(tab => {
    tab.classList.toggle('active', tab.dataset.mode === mode);
  });
  
  // Toggle visibility
  if (mode === 'simple') {
    packageSummary.style.display = 'block';
    if (consolidateSection) consolidateSection.style.display = 'none';
    if (cycleSection) cycleSection.style.display = 'none';
  } else if (mode === 'cycle') {
    packageSummary.style.display = 'none';
    if (consolidateSection) consolidateSection.style.display = 'none';
    if (cycleSection) cycleSection.style.display = 'block';
  } else {
    // default fallback
    packageSummary.style.display = 'block';
    if (consolidateSection) consolidateSection.style.display = 'none';
    if (cycleSection) cycleSection.style.display = 'none';
  }

  if (mode === 'simple') showNotification('Modo: Simulación Simple');
  else if (mode === 'cycle') showNotification('Modo: Conteo Cíclico');
}

// Load Sample Orders
function loadSampleOrders() {
  const sampleOrders = [
    {
      id_orden: 'ORD001',
      items: [[2, 0, 1, 'SKU-001'], [6, 3, 2, 'SKU-002']]
    },
    {
      id_orden: 'ORD002',
      items: [[0, 5, 1, 'SKU-003'], [3, 6, 3, 'SKU-004']]
    },
    {
      id_orden: 'ORD003',
      items: [[4, 8, 2, 'SKU-005'], [1, 9, 1, 'SKU-006'], [2, 0, 1, 'SKU-007']]
    }
  ];
  
  ordersInput.value = JSON.stringify(sampleOrders, null, 2);
  showNotification('Órdenes de ejemplo cargadas');
}

// Notification Functions
function showNotification(message, type = 'success') {
  notificationText.textContent = message;
  
  if (type === 'error') {
    notificationIcon.innerHTML = `
      <svg width="24" height="24" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
        <circle cx="12" cy="12" r="10" fill="#ef4444"/>
        <path d="M8 8l8 8M16 8l-8 8" stroke="white" stroke-width="2" stroke-linecap="round"/>
      </svg>
    `;
  } else {
    notificationIcon.innerHTML = `
      <svg width="24" height="24" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
        <circle cx="12" cy="12" r="10" fill="#10b981"/>
        <path d="M8 12l2 2 4-4" stroke="white" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
      </svg>
    `;
  }
  
  notification.className = `notification ${type} show`;
  
  setTimeout(() => {
    notification.classList.remove('show');
  }, 4000);
}

// Tab Management
function addPackageTab() {
  const newIndex = packageCount;
  packageCount++;
  
  // Create tab button
  const tabBtn = document.createElement('button');
  tabBtn.className = 'tab-button';
  tabBtn.dataset.tab = newIndex;
  tabBtn.innerHTML = `
    <svg width="16" height="16" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
      <rect x="3" y="3" width="18" height="18" rx="2" stroke="currentColor" stroke-width="2"/>
    </svg>
    Paquete ${newIndex + 1}
  `;
  tabBtn.addEventListener('click', () => switchTab(newIndex));
  tabsHeader.appendChild(tabBtn);
  
  // Create tab pane
  const tabPane = document.createElement('div');
  tabPane.className = 'tab-pane';
  tabPane.dataset.pane = newIndex;
  tabPane.innerHTML = `
    <div class="form-grid">
      <div class="form-group">
        <label>
          <svg width="20" height="20" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg" style="display: inline-block; vertical-align: middle; margin-right: 6px;">
            <path d="M12 5v14M5 12h14" stroke="#2563eb" stroke-width="2" stroke-linecap="round"/>
          </svg>
          Fila
          <div class="label-description">Coordenada vertical del paquete</div>
        </label>
        <input type="number" class="package-row" data-index="${newIndex}" value="0" min="0" />
      </div>

      <div class="form-group">
        <label>
          <svg width="20" height="20" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg" style="display: inline-block; vertical-align: middle; margin-right: 6px;">
            <path d="M12 5v14M5 12h14" stroke="#2563eb" stroke-width="2" stroke-linecap="round"/>
          </svg>
          Columna
          <div class="label-description">Coordenada horizontal del paquete</div>
        </label>
        <input type="number" class="package-col" data-index="${newIndex}" value="0" min="0" />
      </div>
    </div>

    <div class="tab-actions">
      <button type="button" class="btn-danger remove-tab-btn" data-index="${newIndex}">
        <svg width="18" height="18" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
          <path d="M6 6l12 12M18 6L6 18" stroke="currentColor" stroke-width="2" stroke-linecap="round"/>
        </svg>
        Eliminar Paquete
      </button>
    </div>
  `;
  
  tabsContent.appendChild(tabPane);
  
  // Add event listeners
  const removeBtn = tabPane.querySelector('.remove-tab-btn');
  removeBtn.addEventListener('click', () => removePackageTab(newIndex));
  
  const inputs = tabPane.querySelectorAll('input');
  inputs.forEach(input => {
    input.addEventListener('input', updateSummary);
  });
  
  switchTab(newIndex);
  updateSummary();
  showNotification('Paquete agregado correctamente');
}

function switchTab(index) {
  // Update buttons
  document.querySelectorAll('.tab-button').forEach(btn => {
    btn.classList.toggle('active', btn.dataset.tab == index);
  });
  
  // Update panes
  document.querySelectorAll('.tab-pane').forEach(pane => {
    pane.classList.toggle('active', pane.dataset.pane == index);
  });
}

function removePackageTab(index) {
  const remaining = document.querySelectorAll('.tab-button').length;
  
  if (remaining <= 1) {
    showNotification('Debe haber al menos un paquete', 'error');
    return;
  }
  
  // Remove tab button
  const tabBtn = document.querySelector(`.tab-button[data-tab="${index}"]`);
  if (tabBtn) tabBtn.remove();
  
  // Remove tab pane
  const tabPane = document.querySelector(`.tab-pane[data-pane="${index}"]`);
  if (tabPane) tabPane.remove();
  
  // Switch to first tab if current was removed
  const firstTab = document.querySelector('.tab-button');
  if (firstTab && !document.querySelector('.tab-button.active')) {
    switchTab(firstTab.dataset.tab);
  }
  
  updateSummary();
  showNotification('Paquete eliminado');
}

function updateSummary() {
  const packages = getAllPackages();
  
  summaryList.innerHTML = packages.map((pkg, idx) => `
    <div class="summary-item">
      <svg width="16" height="16" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
        <rect x="3" y="3" width="18" height="18" rx="2" stroke="currentColor" stroke-width="2"/>
      </svg>
      P${idx + 1}: (${pkg[0]}, ${pkg[1]})
    </div>
  `).join('');
}

function getAllPackages() {
  const packages = [];
  const rowInputs = document.querySelectorAll('.package-row');
  const colInputs = document.querySelectorAll('.package-col');
  
  for (let i = 0; i < rowInputs.length; i++) {
    const row = parseInt(rowInputs[i].value) || 0;
    const col = parseInt(colInputs[i].value) || 0;
    packages.push([row, col]);
  }
  
  return packages;
}

// Load Defaults
async function loadDefaults() {
  try {
    const res = await fetch(apiBase + '/defaults');
    
    if (!res.ok) {
      showNotification('Error: No se pudo conectar con el backend', 'error');
      return;
    }
    
    const data = await res.json();
    
    if (!data || !data.paquetes || !Array.isArray(data.paquetes)) {
      showNotification('Error: datos de defaults inválidos', 'error');
      return;
    }
    
    // Clear existing tabs except first
    const existingTabs = document.querySelectorAll('.tab-button');
    for (let idx = existingTabs.length - 1; idx >= 1; idx--) {
      const tab = existingTabs[idx];
      const index = tab.dataset.tab;
      const tabBtn = document.querySelector(`.tab-button[data-tab="${index}"]`);
      const tabPane = document.querySelector(`.tab-pane[data-pane="${index}"]`);
      if (tabBtn) tabBtn.remove();
      if (tabPane) tabPane.remove();
    }
    
    // Reset counter
    packageCount = data.paquetes.length;
    
    // Set first package
    const firstRow = document.querySelector('.package-row[data-index="0"]');
    const firstCol = document.querySelector('.package-col[data-index="0"]');
    if (firstRow) firstRow.value = data.paquetes[0][0];
    if (firstCol) firstCol.value = data.paquetes[0][1];
    
    // Add remaining packages
    for (let i = 1; i < data.paquetes.length; i++) {
      const newIndex = i;
      
      const tabBtn = document.createElement('button');
      tabBtn.className = 'tab-button';
      tabBtn.dataset.tab = newIndex;
      tabBtn.innerHTML = `
        <svg width="16" height="16" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
          <rect x="3" y="3" width="18" height="18" rx="2" stroke="currentColor" stroke-width="2"/>
        </svg>
        Paquete ${newIndex + 1}
      `;
      tabBtn.addEventListener('click', () => switchTab(newIndex));
      tabsHeader.appendChild(tabBtn);
      
      const tabPane = document.createElement('div');
      tabPane.className = 'tab-pane';
      tabPane.dataset.pane = newIndex;
      tabPane.innerHTML = `
        <div class="form-grid">
          <div class="form-group">
            <label>
              <svg width="20" height="20" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg" style="display: inline-block; vertical-align: middle; margin-right: 6px;">
                <path d="M12 5v14M5 12h14" stroke="#2563eb" stroke-width="2" stroke-linecap="round"/>
              </svg>
              Fila
              <div class="label-description">Coordenada vertical del paquete</div>
            </label>
            <input type="number" class="package-row" data-index="${newIndex}" value="${data.paquetes[i][0]}" min="0" />
          </div>

          <div class="form-group">
            <label>
              <svg width="20" height="20" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg" style="display: inline-block; vertical-align: middle; margin-right: 6px;">
                <path d="M12 5v14M5 12h14" stroke="#2563eb" stroke-width="2" stroke-linecap="round"/>
              </svg>
              Columna
              <div class="label-description">Coordenada horizontal del paquete</div>
            </label>
            <input type="number" class="package-col" data-index="${newIndex}" value="${data.paquetes[i][1]}" min="0" />
          </div>
        </div>

        <div class="tab-actions">
          <button type="button" class="btn-danger remove-tab-btn" data-index="${newIndex}">
            <svg width="18" height="18" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
              <path d="M6 6l12 12M18 6L6 18" stroke="currentColor" stroke-width="2" stroke-linecap="round"/>
            </svg>
            Eliminar Paquete
          </button>
        </div>
      `;
      
      tabsContent.appendChild(tabPane);
      
      const removeBtn = tabPane.querySelector('.remove-tab-btn');
      removeBtn.addEventListener('click', () => removePackageTab(newIndex));
      
      const inputs = tabPane.querySelectorAll('input');
      inputs.forEach(input => {
        input.addEventListener('input', updateSummary);
      });
    }
    
    switchTab(0);
    updateSummary();
    showNotification('✓ Ejemplo cargado: ' + data.paquetes.length + ' paquetes');
  } catch (err) {
    console.error('Error en loadDefaults:', err);
    showNotification('Error al cargar ejemplo: ' + err.message, 'error');
  }
}

// Run Simulation
async function runSimulation(e) {
  e.preventDefault();
  
  if (currentMode === 'simple') {
    await runSimpleSimulation();
  } else if (currentMode === 'cycle') {
    await runCycleCount();
  } else if (currentMode === 'cycle') {
    // When submitting the form while in cycle mode, call runCycleCount
    await runCycleCount();
  }
}

// Cycle Count: load defaults into textarea
function loadCycleDefaults() {
  const sample = [
    { fila: 0, col: 0, sku: 'AUDIO-001', cantidad: 120, movimientos: 12, conteos_ultimos_365dias: 1, criticidad: 3 },
    { fila: 2, col: 4, sku: 'COMP-101', cantidad: 230, movimientos: 5, conteos_ultimos_365dias: 3, criticidad: 2 },
    { fila: 5, col: 7, sku: 'REFR-555', cantidad: 6, movimientos: 2, conteos_ultimos_365dias: 0, criticidad: 4 },
    { fila: 8, col: 10, sku: 'AC-900', cantidad: 85, movimientos: 0, conteos_ultimos_365dias: 4, criticidad: 1 }
  ];
  clearCycleTable();
  sample.forEach(s => appendCycleRow(s));
  showNotification('Ejemplo de ubicaciones cargado para Conteo Cíclico');
}

function appendCycleRow(item) {
  const tr = document.createElement('tr');
  // Display filas/cols as 1-based to user (internally we use 0-based)
  const displayFila = (typeof item.fila === 'number') ? (Number(item.fila) + 1) : (item.fila ?? '');
  const displayCol = (typeof item.col === 'number') ? (Number(item.col) + 1) : (item.col ?? '');
  tr.innerHTML = `
    <td>${item.sku || ''}</td>
    <td>${item.cantidad ?? ''}</td>
    <td>${displayFila}</td>
    <td>${displayCol}</td>
    <td>${item.movimientos ?? 0}</td>
    <td>${item.conteos_ultimos_365dias ?? 0}</td>
    <td>${item.criticidad ?? 0}</td>
    <td><button type="button" class="btn-danger small remove-row">Eliminar</button></td>
  `;
  if (cycleTableBody) cycleTableBody.appendChild(tr);
  const btn = tr.querySelector('.remove-row');
  btn.addEventListener('click', () => tr.remove());
}

function addCycleRow() {
  const item = {
    sku: inputSKU ? inputSKU.value.trim() : '',
    cantidad: inputCantidad ? Number(inputCantidad.value || 0) : 0,
    // User enters 1-based values; validate then convert to 0-based for internal storage
    fila: inputFila ? Number(inputFila.value || 0) : 0,
    col: inputCol ? Number(inputCol.value || 0) : 0,
    movimientos: inputMov ? Number(inputMov.value || 0) : 0,
    conteos_ultimos_365dias: inputConteos ? Number(inputConteos.value || 0) : 0,
    criticidad: inputCrit ? Number(inputCrit.value || 0) : 0
  };
  if (!item.sku) {
    showNotification('Ingrese SKU antes de agregar', 'error');
    return;
  }

  // Validate cantidad
  if (!Number.isFinite(item.cantidad) || item.cantidad < 0) {
    showNotification('Cantidad inválida: debe ser 0 o mayor', 'error');
    return;
  }

  // Validate ranges: filas 1..12, columnas 1..9
  const userFila = Number(item.fila);
  const userCol = Number(item.col);
  if (!Number.isInteger(userFila) || userFila < 1 || userFila > 12) {
    showNotification('Fila inválida: debe ser entero entre 1 y 12', 'error');
    return;
  }
  if (!Number.isInteger(userCol) || userCol < 1 || userCol > 9) {
    showNotification('Columna inválida: debe ser entero entre 1 y 9', 'error');
    return;
  }

  // Convert to 0-based for storage
  const internal = Object.assign({}, item, { fila: userFila - 1, col: userCol - 1 });
  appendCycleRow(internal);
  // clear inputs
  if (inputSKU) inputSKU.value = '';
  if (inputMov) inputMov.value = '';
  if (inputConteos) inputConteos.value = '';
  if (inputCrit) inputCrit.value = '';
  if (inputCantidad) inputCantidad.value = '';
}

function clearCycleTable() {
  if (cycleTableBody) cycleTableBody.innerHTML = '';
}

function getCycleItemsFromTable() {
  const rows = cycleTableBody ? Array.from(cycleTableBody.querySelectorAll('tr')) : [];
  return rows.map(r => {
    const cols = r.querySelectorAll('td');
    // Table shows 1-based fila/col to user; convert back to 0-based for backend
    // New column order: 0:SKU, 1:Cantidad, 2:Fila, 3:Col, 4:Mov, 5:Conteos, 6:Crit
    const cantidad = Number(cols[1].textContent || 0);
    const userFila = Number(cols[2].textContent || 0);
    const userCol = Number(cols[3].textContent || 0);
    return {
      sku: cols[0].textContent.trim(),
      cantidad: cantidad,
      fila: Math.max(0, userFila - 1),
      col: Math.max(0, userCol - 1),
      movimientos: Number(cols[4].textContent || 0),
      conteos_ultimos_365dias: Number(cols[5].textContent || 0),
      criticidad: Number(cols[6].textContent || 0)
    };
  });
}

function loadInventorySample() {
  clearCycleTable();
  HARDCODED_INVENTORY.forEach(it => appendCycleRow({
    sku: it.sku,
    cantidad: it.cantidad,
    fila: it.fila,
    col: it.col,
    movimientos: Math.max(0, Math.floor(it.cantidad / 5)),
    conteos_ultimos_365dias: 1,
    criticidad: it.cantidad < 20 ? 5 : (it.cantidad < 100 ? 3 : 1)
  }));
  showNotification('Inventario quemado cargado en la tabla');
}

async function runCycleCount() {
  // Collect items from the friendly table (converting to 0-based indices)
  const ubicaciones = getCycleItemsFromTable();
  if (!ubicaciones || ubicaciones.length === 0) {
    showNotification('Agrega al menos una ubicación al plan antes de generar', 'error');
    return;
  }

  const frecuencia = cycleFreqInput ? parseInt(cycleFreqInput.value || '5') : 5;

  const weights = {
    faltantes: Number(weightFaltantes ? weightFaltantes.value : 100),
    movimientos: Number(weightMovimientos ? weightMovimientos.value : 1),
    criticidad: Number(weightCriticidad ? weightCriticidad.value : 50)
  };

  const payload = { ubicaciones, frecuencia_minima: frecuencia, weights };

  showNotification('Generando plan de conteo...');
  // Try backend first; if it fails, generate plan client-side
  try {
    const res = await fetch(apiBase + '/cycle-count', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload)
    });

    if (!res.ok) throw new Error('Backend no disponible: ' + res.statusText);

    const data = await res.json();
    if (data.error) {
      throw new Error(data.detail || data.error || 'Error en backend');
    }

    // Compute user-friendly inventory totals client-side
    const totalInventario = ubicaciones.reduce((s, it) => s + (Number(it.cantidad || 0)), 0);
    const totalSalidas = ubicaciones.reduce((s, it) => s + (Number(it.movimientos || 0)), 0);
    data.estadisticas = data.estadisticas || {};
    data.estadisticas.total_inventario = totalInventario;
    data.estadisticas.total_salidas = totalSalidas;

    renderCycleResults(data);
    formSection.classList.remove('active');
    resultsSection.classList.add('active');
    showNotification('Plan de conteo generado (desde backend)');
    return;
  } catch (err) {
    console.warn('Backend ciclo falla, usando motor local:', err);
  }

  // Fallback: generate plan client-side
  try {
    const local = generateCyclePlanJS(ubicaciones, frecuencia, weights, {});
    // attach inventory totals
    local.estadisticas = local.estadisticas || {};
    local.estadisticas.total_inventario = ubicaciones.reduce((s, it) => s + (Number(it.cantidad || 0)), 0);
    local.estadisticas.total_salidas = ubicaciones.reduce((s, it) => s + (Number(it.movimientos || 0)), 0);
    renderCycleResults(local);
    formSection.classList.remove('active');
    resultsSection.classList.add('active');
    showNotification('Plan de conteo generado (motor local)');
  } catch (err) {
    showNotification('Error al generar el plan localmente: ' + err, 'error');
  }
}


/**
 * Fallback JS implementation of the ConteoCiclico generator.
 * Mirrors backend logic so UI works even without server.
 */
function generateCyclePlanJS(ubicaciones, frecuencia_minima = 5, weights = {faltantes:100, movimientos:1, criticidad:50}, zone_weights = {}) {
  const hoy = new Date();
  const periodo_dias = 365;

  const enriched = ubicaciones.map(item => {
    const sku = item.sku || item.ref || `${item.fila}-${item.col}`;
    const movimientos = Number(item.movimientos || 0);
    const conteos_365 = Number(item.conteos_ultimos_365dias || 0);
    const criticidad = Number(item.criticidad || 0);
    const cantidad = Number(item.cantidad || 0);

    const faltantes = Math.max(0, Number(frecuencia_minima) - conteos_365);

    // zone bonus from ALMACENES if available
    let zona_bonus = 0;
    try {
      if (window.ALMACENES && Array.isArray(window.ALMACENES)) {
        const almacen = window.ALMACENES.find(a => Array.isArray(a.columnas) && a.columnas.includes(Number(item.col)));
        if (almacen && zone_weights && zone_weights[almacen.nombre]) {
          zona_bonus = Number(zone_weights[almacen.nombre]) || 0;
        }
      }
    } catch (e) {}

    const score = (
      faltantes * Number(weights.faltantes || 100) +
      movimientos * Number(weights.movimientos || 1) +
      criticidad * Number(weights.criticidad || 50) +
      zona_bonus
    );

    return {
      sku,
      fila: item.fila,
      col: item.col,
      cantidad,
      movimientos,
      conteos_ultimos_365dias: conteos_365,
      faltantes,
      score
    };
  });

  enriched.sort((a,b) => {
    if (b.score === a.score) return (a.sku || '').localeCompare(b.sku || '');
    return b.score - a.score;
  });

  const plan = [];
  let total_counts_scheduled = 0;
  enriched.forEach(it => {
    const needed = it.faltantes;
    const fechas = [];
    if (needed > 0) {
      const interval = Math.max(1, Math.floor(periodo_dias / needed));
      for (let k=0;k<needed;k++) {
        const d = new Date(hoy.getTime());
        d.setDate(d.getDate() + k * interval);
        fechas.push(d.toISOString().slice(0,10));
      }
      total_counts_scheduled += needed;
    } else {
      const d = new Date(hoy.getTime());
      d.setDate(d.getDate() + Math.floor(periodo_dias/2));
      fechas.push(d.toISOString().slice(0,10));
    }

    plan.push({
      sku: it.sku,
      fila: it.fila,
      col: it.col,
      conteos_ultimos_365dias: it.conteos_ultimos_365dias,
      faltantes: it.faltantes,
      score: it.score,
      fechas_planificadas: fechas
    });
  });

  const estadisticas = {
    total_items: enriched.length,
    items_con_faltantes: enriched.filter(x => x.faltantes>0).length,
    total_counts_scheduled
  };

  return { plan, estadisticas };
}

function renderCycleResults(data) {
  if (!cycleResults) return;
  const plan = data.plan || [];
  const stats = data.estadisticas || {};
  // Store enriched plan + stats for later export or review
  lastCyclePlan = { plan: plan, estadisticas: stats };

  let html = `<div class="cycle-stats">`;
  html += `<strong>Total items:</strong> ${stats.total_items || 0} &nbsp; `;
  html += `<strong>Items con faltantes:</strong> ${stats.items_con_faltantes || 0} &nbsp; `;
  html += `<strong>Conteos programados:</strong> ${stats.total_counts_scheduled || 0}`;
  // Optional inventory totals
  if (stats.total_inventario !== undefined) html += ` &nbsp; <strong>Inventario total:</strong> ${stats.total_inventario}`;
  if (stats.total_salidas !== undefined) html += ` &nbsp; <strong>Salidas (movimientos):</strong> ${stats.total_salidas}`;
  html += `</div>`;

  html += `<div style="margin-top:8px;"><button id="exportCycleBtn" class="btn-secondary">Exportar a Excel</button></div>`;
  html += `<table class="cycle-table"><thead><tr><th>#</th><th>SKU</th><th>Ubicación</th><th>Conteos</th><th>Faltantes</th><th>Score</th><th>Fechas planificadas</th></tr></thead><tbody>`;
  plan.forEach((p, idx) => {
    html += `<tr>`;
    html += `<td>${idx+1}</td>`;
    html += `<td>${p.sku}</td>`;
    html += `<td>${p.fila}, ${p.col}</td>`;
    html += `<td>${p.conteos_ultimos_365dias}</td>`;
    html += `<td>${p.faltantes}</td>`;
    html += `<td>${Number(p.score).toFixed(1)}</td>`;
    html += `<td>${(p.fechas_planificadas || []).join(', ')}</td>`;
    html += `</tr>`;
  });
  html += `</tbody></table>`;

  cycleResults.innerHTML = html;
  const exportBtn = document.getElementById('exportCycleBtn');
  if (exportBtn) exportBtn.addEventListener('click', exportCycleToExcel);
}

async function exportCycleToExcel() {
  if (!lastCyclePlan) {
    showNotification('No hay plan para exportar', 'error');
    return;
  }

  try {
    const planToSend = lastCyclePlan && lastCyclePlan.plan ? lastCyclePlan.plan : lastCyclePlan;
    
    // Intentar backend primero
    try {
      const res = await fetch(apiBase + '/export-cycle', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ plan: planToSend })
      });

      if (res.ok) {
        const blob = await res.blob();
        const disposition = res.headers.get('Content-Disposition') || '';
        let filename = 'plan_conteo.xlsx';
        const match = /filename=\"?([^\";]+)/.exec(disposition);
        if (match) filename = match[1];

        const url = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = filename;
        document.body.appendChild(a);
        a.click();
        a.remove();
        window.URL.revokeObjectURL(url);
        showNotification('Descarga iniciada: ' + filename);
        return;
      }
    } catch (e) {
      console.warn('Backend export falló, usando generador local:', e);
    }

    // Fallback: generar CSV localmente
    const csvContent = generateCycleCSV(planToSend);
    const blob = new Blob([csvContent], { type: 'text/csv;charset=utf-8;' });
    const url = window.URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = 'plan_conteo.csv';
    document.body.appendChild(a);
    a.click();
    a.remove();
    window.URL.revokeObjectURL(url);
    showNotification('CSV descargado (generador local)');
  } catch (err) {
    showNotification('Error al exportar: ' + err, 'error');
  }
}

/**
 * Generar CSV localmente desde un plan de conteo.
 */
function generateCycleCSV(plan) {
  const rows = [];
  rows.push(['SKU', 'Fila', 'Columna', 'Conteos Ult. 365 dias', 'Faltantes', 'Score', 'Fechas Planificadas']);
  
  if (Array.isArray(plan)) {
    plan.forEach(p => {
      rows.push([
        p.sku || '',
        p.fila || '',
        p.col || '',
        p.conteos_ultimos_365dias || 0,
        p.faltantes || 0,
        (typeof p.score === 'number' ? p.score.toFixed(2) : p.score),
        (Array.isArray(p.fechas_planificadas) ? p.fechas_planificadas.join('; ') : '')
      ]);
    });
  }
  
  // Convertir a CSV (escapar comillas)
  return rows.map(row => 
    row.map(cell => 
      typeof cell === 'string' && cell.includes(',') 
        ? `"${cell.replace(/"/g, '""')}"` 
        : cell
    ).join(',')
  ).join('\n');
}

async function runSimpleSimulation() {
  const packages = getAllPackages();
  
  if (packages.length === 0) {
    showNotification('Debes agregar al menos un paquete', 'error');
    return;
  }
  
  const payload = {
    paquetes: packages,
    inicio: [0, 0],
    costo_celda: 2.7,
    costo_pasillo: 5.0
  };
  
  lastPayload = payload;
  
  const originalText = runBtn.innerHTML;
  runBtn.innerHTML = `
    <svg class="loading" width="20" height="20" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
      <circle cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4" opacity="0.25"/>
      <path d="M12 2a10 10 0 0110 10" stroke="currentColor" stroke-width="4" stroke-linecap="round"/>
    </svg>
    Procesando...
  `;
  runBtn.disabled = true;
  
  try {
    const res = await fetch(apiBase + '/simulate', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload)
    });
    
    const data = await res.json();
    
    if (data.error) {
      showNotification('Error: ' + (data.detail || data.error), 'error');
      return;
    }
    
    lastResult = data;
    displayResults(data);
    
    formSection.classList.remove('active');
    resultsSection.classList.add('active');
    exportBtn.disabled = false;
    
    showNotification('Simulación completada exitosamente');
    
  } catch (err) {
    showNotification('Error al ejecutar la simulación: ' + err, 'error');
  } finally {
    runBtn.innerHTML = originalText;
    runBtn.disabled = false;
  }
}

async function runConsolidateSimulation() {
  try {
    const ordersText = ordersInput.value.trim();
    if (!ordersText) {
      showNotification('Debes ingresar las órdenes en formato JSON', 'error');
      return;
    }
    
    let ordenes;
    try {
      ordenes = JSON.parse(ordersText);
    } catch (e) {
      showNotification('Formato JSON inválido: ' + e.message, 'error');
      return;
    }
    
    const payload = { ordenes };
    
    const originalText = runBtn.innerHTML;
    runBtn.innerHTML = `
      <svg class="loading" width="20" height="20" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
        <circle cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4" opacity="0.25"/>
        <path d="M12 2a10 10 0 0110 10" stroke="currentColor" stroke-width="4" stroke-linecap="round"/>
      </svg>
      Consolidando...
    `;
    runBtn.disabled = true;
    
    const res = await fetch(apiBase + '/consolidate', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload)
    });
    
    const result = await res.json();
    
    if (result.error) {
      showNotification('Error: ' + result.error, 'error');
      return;
    }
    
    lastResult = result;
    displayConsolidationResults(result);
    
    formSection.classList.remove('active');
    resultsSection.classList.add('active');
    exportBtn.disabled = false;
    
    showNotification('Consolidación completada exitosamente');
    
  } catch (err) {
    showNotification('Error al consolidar: ' + err, 'error');
  } finally {
    runBtn.innerHTML = originalText;
    runBtn.disabled = false;
  }
}

// Display Results
function displayResults(data) {
  const costTotal = data.total_cost !== undefined ? parseFloat(data.total_cost) : 0;
  const posFinal = data.pos_final || [0, 0];
  const pasos = data.pasos || [];
  
  // Stats
  resultStats.innerHTML = `
    <div class="stat-item">
      <div class="stat-label">Costo Total</div>
      <div class="stat-value">${costTotal.toFixed(2)}</div>
    </div>
    <div class="stat-item">
      <div class="stat-label">Movimientos</div>
      <div class="stat-value">${pasos.length}</div>
    </div>
    <div class="stat-item">
      <div class="stat-label">Posición Final</div>
      <div class="stat-value">(${posFinal[0]}, ${posFinal[1]})</div>
    </div>
  `;
  
  // Warehouse Grid
  renderWarehouseGrid(data);
  
  // Table
  if (pasos && Array.isArray(pasos) && pasos.length > 0) {
    const firstPaso = pasos[0];
    if (firstPaso && typeof firstPaso === 'object') {
      const headers = Object.keys(firstPaso);
      let tableHTML = '<table><thead><tr>';
      headers.forEach(h => {
        tableHTML += `<th>${h}</th>`;
      });
      tableHTML += '</tr></thead><tbody>';
      
      pasos.forEach(paso => {
        if (paso && typeof paso === 'object') {
          tableHTML += '<tr>';
          headers.forEach(h => {
            const value = paso[h] !== undefined ? paso[h] : '';
            tableHTML += `<td>${value}</td>`;
          });
          tableHTML += '</tr>';
        }
      });
      
      tableHTML += '</tbody></table>';
      tableArea.innerHTML = tableHTML;
    } else {
      tableArea.innerHTML = '<p>Formato de pasos inválido</p>';
    }
  } else {
    tableArea.innerHTML = '<p>No hay pasos disponibles</p>';
  }
}

// Render Warehouse Grid with Route Visualization
function renderWarehouseGrid(data) {
  const paquetes = lastPayload.paquetes || [];
  const inicio = lastPayload.inicio || [0, 0];
  const posFinal = data.pos_final || [0, 0];
  const ruta = data.ruta || [];
  
  // Calculate grid dimensions
  let maxRow = Math.max(inicio[0], posFinal[0]);
  let maxCol = Math.max(inicio[1], posFinal[1]);
  
  paquetes.forEach(pkg => {
    maxRow = Math.max(maxRow, pkg[0]);
    maxCol = Math.max(maxCol, pkg[1]);
  });
  
  // Ensure minimum grid size
  maxRow = Math.max(maxRow, 8);
  maxCol = Math.max(maxCol, 11);
  
  const rows = maxRow + 1;
  const cols = maxCol + 1;
  
  // Create grid container wrapper
  warehouseGrid.style.gridTemplateColumns = `repeat(${cols}, 40px)`;
  warehouseGrid.style.position = 'relative';
  warehouseGrid.innerHTML = '';
  
  // Initialize grid data
  const grid = Array(rows).fill(null).map(() => Array(cols).fill(''));
  const cellElements = [];
  
  // Mark start
  grid[inicio[0]][inicio[1]] = 'start';
  
  // Mark packages
  paquetes.forEach(pkg => {
    if (grid[pkg[0]][pkg[1]] !== 'start') {
      grid[pkg[0]][pkg[1]] = 'package';
    }
  });
  
  // Mark end position
  if (grid[posFinal[0]][posFinal[1]] === '') {
    grid[posFinal[0]][posFinal[1]] = 'end';
  }
  
  // Render grid cells
  for (let i = 0; i < rows; i++) {
    cellElements[i] = [];
    for (let j = 0; j < cols; j++) {
      const cell = document.createElement('div');
      
      // Agregar clase base
      let cellClasses = ['grid-cell'];
      
      // Agregar clase de almacén si existe
      if (window.ALMACENES && window.ALMACENES.length > 0) {
        const almacen = window.ALMACENES.find(a => a.columnas.includes(j));
        if (almacen) {
          cellClasses.push('almacen');
          cell.dataset.almacen = almacen.nombre;
          // Aplicar color de almacén como fondo
          cell.style.backgroundColor = almacen.color;
        }
      }
      
      // Agregar clase de pasillo si corresponde
      if (PASILLOS.includes(j)) {
        cellClasses.push('pasillo');
      }
      
      // Agregar clase de contenido
      if (grid[i][j]) {
        cellClasses.push(grid[i][j]);
      }
      
      cell.className = cellClasses.join(' ');
      cell.dataset.row = i;
      cell.dataset.col = j;
      
      // Set text content
      if (grid[i][j] === 'start') {
        cell.textContent = 'I';
        cell.title = `Inicio (${i}, ${j})`;
      } else if (grid[i][j] === 'package') {
        cell.textContent = 'P';
        cell.title = `Paquete (${i}, ${j})`;
      } else if (grid[i][j] === 'end') {
        cell.textContent = 'F';
        cell.title = `Final (${i}, ${j})`;
      } else {
        cell.textContent = '';
        cell.title = `(${i}, ${j})`;
      }
      
      warehouseGrid.appendChild(cell);
      cellElements[i][j] = cell;
    }
  }
  
  // Draw path with arrows if route exists
  if (ruta && ruta.length > 1) {
    drawPath(warehouseGrid, ruta, cellElements);
  }
}

// Draw Path with Arrows and Numbered Points
function drawPath(container, ruta, cellElements) {
  // Wait for DOM to settle before drawing
  setTimeout(() => {
    // Remove any existing SVG
    const existingSvg = container.querySelector('svg');
    if (existingSvg) {
      existingSvg.remove();
    }
    
    const containerRect = container.getBoundingClientRect();
    
    const svg = document.createElementNS('http://www.w3.org/2000/svg', 'svg');
    svg.style.position = 'absolute';
    svg.style.top = '0px';
    svg.style.left = '0px';
    svg.style.width = '100%';
    svg.style.height = '100%';
    svg.style.pointerEvents = 'none';
    svg.style.zIndex = '10';
    svg.style.overflow = 'visible';
    svg.setAttribute('viewBox', `0 0 ${containerRect.width} ${containerRect.height}`);
    svg.setAttribute('preserveAspectRatio', 'none');
    
    // Add arrow marker definitions
    const defs = document.createElementNS('http://www.w3.org/2000/svg', 'defs');
    const markerArrow = document.createElementNS('http://www.w3.org/2000/svg', 'marker');
    const markerId = 'arrowhead-' + Date.now();
    markerArrow.setAttribute('id', markerId);
    markerArrow.setAttribute('markerWidth', '10');
    markerArrow.setAttribute('markerHeight', '10');
    markerArrow.setAttribute('refX', '9');
    markerArrow.setAttribute('refY', '3');
    markerArrow.setAttribute('orient', 'auto');
    
    const polygon = document.createElementNS('http://www.w3.org/2000/svg', 'polygon');
    polygon.setAttribute('points', '0 0, 10 3, 0 6');
    polygon.setAttribute('fill', '#6366f1');
    markerArrow.appendChild(polygon);
    defs.appendChild(markerArrow);
    svg.appendChild(defs);
    
    // Use ruta tal como la proporciona el backend (ya contiene puntos clave y pasillos)
    const puntosClave = ruta.map((pos, i) => ({ pos, tipo: i === 0 ? 'inicio' : (i === ruta.length - 1 ? 'final' : 'intermedio'), idx: i }));

    // Draw lines entre puntos consecutivos de la ruta (HV-only: L-shapes si es necesario)
    for (let i = 0; i < puntosClave.length - 1; i++) {
      const [row1, col1] = puntosClave[i].pos;
      const [row2, col2] = puntosClave[i + 1].pos;

      const cell1 = cellElements[row1] && cellElements[row1][col1];
      const cell2 = cellElements[row2] && cellElements[row2][col2];

      if (!cell1 || !cell2) continue;

      const rect1 = cell1.getBoundingClientRect();
      const rect2 = cell2.getBoundingClientRect();

      const x1 = rect1.left - containerRect.left + rect1.width / 2;
      const y1 = rect1.top - containerRect.top + rect1.height / 2;
      const x2 = rect2.left - containerRect.left + rect2.width / 2;
      const y2 = rect2.top - containerRect.top + rect2.height / 2;

      // If movement is aligned (same row or same column) draw single segment
      if (row1 === row2 || col1 === col2) {
        const line = document.createElementNS('http://www.w3.org/2000/svg', 'line');
        line.setAttribute('x1', x1);
        line.setAttribute('y1', y1);
        line.setAttribute('x2', x2);
        line.setAttribute('y2', y2);
        line.setAttribute('stroke', '#6366f1');
        line.setAttribute('stroke-width', '3');
        line.setAttribute('marker-end', `url(#${markerId})`);
        line.style.opacity = '0.7';
        svg.appendChild(line);
      } else {
        // Draw L-shape: vertical to target row, then horizontal to target col
        const xm = x1; // corner x: keep source column
        const ym = y2; // corner y: target row

        // First segment: from (x1,y1) to (xm,ym)
        const line1 = document.createElementNS('http://www.w3.org/2000/svg', 'line');
        line1.setAttribute('x1', x1);
        line1.setAttribute('y1', y1);
        line1.setAttribute('x2', xm);
        line1.setAttribute('y2', ym);
        line1.setAttribute('stroke', '#6366f1');
        line1.setAttribute('stroke-width', '3');
        line1.style.opacity = '0.7';
        svg.appendChild(line1);

        // Second segment: from (xm,ym) to (x2,y2) with arrow
        const line2 = document.createElementNS('http://www.w3.org/2000/svg', 'line');
        line2.setAttribute('x1', xm);
        line2.setAttribute('y1', ym);
        line2.setAttribute('x2', x2);
        line2.setAttribute('y2', y2);
        line2.setAttribute('stroke', '#6366f1');
        line2.setAttribute('stroke-width', '3');
        line2.setAttribute('marker-end', `url(#${markerId})`);
        line2.style.opacity = '0.7';
        svg.appendChild(line2);
      }
    }
    
    // Add numbered points solo en puntos clave
    puntosClave.forEach((punto) => {
      const idx = punto.idx;
      const pos = punto.pos;
      const [row, col] = pos;
      const cell = cellElements[row] && cellElements[row][col];
      
      if (!cell) return;
      
      const rect = cell.getBoundingClientRect();
      
      const x = rect.left - containerRect.left + rect.width / 2;
      const y = rect.top - containerRect.top + rect.height / 2;
      
      // Outer circle background (white)
      const outerCircle = document.createElementNS('http://www.w3.org/2000/svg', 'circle');
      outerCircle.setAttribute('cx', x);
      outerCircle.setAttribute('cy', y);
      outerCircle.setAttribute('r', '12');
      outerCircle.setAttribute('fill', '#ffffff');
      outerCircle.setAttribute('stroke', '#999999');
      outerCircle.setAttribute('stroke-width', '2');
      
      svg.appendChild(outerCircle);
      
      // Inner colored circle
      const dot = document.createElementNS('http://www.w3.org/2000/svg', 'circle');
      dot.setAttribute('cx', x);
      dot.setAttribute('cy', y);
      dot.setAttribute('r', '8');
      
      let dotColor = '#6366f1';
      if (punto.tipo === 'inicio') {
        dotColor = '#10b981';
      } else if (punto.tipo === 'final') {
        dotColor = '#ef4444';
      }
      
      dot.setAttribute('fill', dotColor);
      dot.style.cursor = 'pointer';
      dot.setAttribute('title', `Punto ${idx + 1}: (${row}, ${col})`);
      
      svg.appendChild(dot);
      
      // Number label
      const text = document.createElementNS('http://www.w3.org/2000/svg', 'text');
      text.setAttribute('x', x);
      text.setAttribute('y', y + 1);
      text.setAttribute('text-anchor', 'middle');
      text.setAttribute('dominant-baseline', 'central');
      text.setAttribute('font-size', '13');
      text.setAttribute('font-weight', 'bold');
      text.setAttribute('fill', '#ffffff');
      text.setAttribute('pointer-events', 'none');
      text.textContent = idx + 1;
      
      svg.appendChild(text);
    });
    
    container.appendChild(svg);
  }, 50);
}

// Export to Excel
async function exportToExcel() {
  if (!lastPayload) return;
  
  const originalText = exportBtn.innerHTML;
  exportBtn.innerHTML = `
    <svg class="loading" width="20" height="20" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
      <circle cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4" opacity="0.25"/>
      <path d="M12 2a10 10 0 0110 10" stroke="currentColor" stroke-width="4" stroke-linecap="round"/>
    </svg>
    Generando...
  `;
  exportBtn.disabled = true;
  
  try {
    const res = await fetch(apiBase + '/export', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(lastPayload)
    });
    
    const contentType = res.headers.get('content-type') || '';
    
    if (contentType.includes('application/json')) {
      const err = await res.json();
      showNotification('Error al exportar: ' + (err.detail || err.error), 'error');
      return;
    }
    
    const blob = await res.blob();
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = 'reporte_recoleccion.xlsx';
    document.body.appendChild(a);
    a.click();
    a.remove();
    URL.revokeObjectURL(url);
    
    showNotification('Archivo Excel descargado correctamente');
    
  } catch (err) {
    showNotification('Error al exportar: ' + err, 'error');
  } finally {
    exportBtn.innerHTML = originalText;
    exportBtn.disabled = false;
  }
}

// Display Consolidation Results
function displayConsolidationResults(result) {
  const stats = result.estadisticas || {};
  const picking_list = result.picking_list || [];
  
  // Stats
  resultStats.innerHTML = `
    <div class="stat-item">
      <div class="stat-label">Total Items</div>
      <div class="stat-value">${stats.total_items || 0}</div>
    </div>
    <div class="stat-item">
      <div class="stat-label">Órdenes</div>
      <div class="stat-value">${stats.ordenes || 0}</div>
    </div>
    <div class="stat-item">
      <div class="stat-label">Ubicaciones</div>
      <div class="stat-value">${stats.ubicaciones_unicas || 0}</div>
    </div>
    <div class="stat-item">
      <div class="stat-label">Distancia Est.</div>
      <div class="stat-value">${(stats.distancia_estimada || 0).toFixed(1)}</div>
    </div>
  `;
  
  // Simple visualization for consolidation
  warehouseGrid.innerHTML = `
    <div style="padding: 16px; background: #f0f4f8; border-radius: 8px;">
      <h4>Picking Consolidado</h4>
      <p>Total de ubicaciones a visitar: <strong>${picking_list.length}</strong></p>
      <p>Orden de visita por columnas: <strong>${(stats.columnas_visitadas || []).join(', ')}</strong></p>
    </div>
  `;
  
  // Table with picking list
  if (picking_list && Array.isArray(picking_list) && picking_list.length > 0) {
    const headers = ['#', 'FILA', 'COL', 'CANT', 'SKUs', 'ÓRDENES'];
    let tableHTML = '<table><thead><tr>';
    headers.forEach(h => {
      tableHTML += `<th>${h}</th>`;
    });
    tableHTML += '</tr></thead><tbody>';
    
    picking_list.forEach((item, idx) => {
      const skus = Object.keys(item.skus || {}).join(', ');
      const ordenes = (item.ordenes || []).join(', ');
      tableHTML += `<tr>
        <td>${idx + 1}</td>
        <td>${item.fila}</td>
        <td>${item.col}</td>
        <td>${item.cantidad}</td>
        <td>${skus}</td>
        <td>${ordenes}</td>
      </tr>`;
    });
    
    tableHTML += '</tbody></table>';
    tableArea.innerHTML = tableHTML;
  }
}

// Consolidación de múltiples órdenes
async function consolidateOrders(ordenes) {
  try {
    const payload = { ordenes: ordenes };
    const res = await fetch(apiBase + '/consolidate', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload)
    });
    
    const result = await res.json();
    
    if (result.error) {
      showNotification('Error: ' + result.error, 'error');
      return null;
    }
    
    return result;
  } catch (err) {
    showNotification('Error al consolidar órdenes: ' + err, 'error');
    return null;
  }
}

// Ejemplo de uso: consolidar múltiples órdenes
function testConsolidateOrders() {
  const ordenes = [
    {
      id_orden: 'ORD001',
      items: [[2, 0, 1, 'SKU-001'], [6, 3, 2, 'SKU-002']]
    },
    {
      id_orden: 'ORD002',
      items: [[0, 5, 1, 'SKU-003'], [3, 6, 3, 'SKU-004']]
    },
    {
      id_orden: 'ORD003',
      items: [[4, 8, 2, 'SKU-005'], [1, 9, 1, 'SKU-006']]
    }
  ];
  
  consolidateOrders(ordenes).then(result => {
    if (result) {
      console.log('Picking consolidado:', result);
      showNotification(`Consolidado: ${result.estadisticas.total_items} items de ${result.estadisticas.ordenes} órdenes`);
    }
  });
}

// Debug: Inspeccionar pasillos
window.debugPasillos = function() {
  console.log('=== DEBUG PASILLOS ===');
  console.log('PASILLOS global:', window.PASILLOS);
  console.log('Celdas en el DOM:');
  document.querySelectorAll('.grid-cell').forEach((cell, idx) => {
    const col = parseInt(cell.dataset.col);
    const row = parseInt(cell.dataset.row);
    const isPasillo = window.PASILLOS.includes(col);
    const classes = cell.className;
    const bg = window.getComputedStyle(cell).backgroundColor;
    if (isPasillo || classes.includes('pasillo')) {
      console.log(`  [${row},${col}] isPasillo=${isPasillo} classes="${classes}" bg="${bg}"`);
    }
  });
};

window.testPasilloStyles = function() {
  console.log('=== TEST PASILLO STYLES ===');
  // Crear una celda de prueba
  const testCell = document.createElement('div');
  testCell.className = 'grid-cell pasillo';
  testCell.textContent = 'TEST';
  testCell.style.display = 'none';
  document.body.appendChild(testCell);
  
  const bg = window.getComputedStyle(testCell).backgroundColor;
  const border = window.getComputedStyle(testCell).borderColor;
  console.log('Pasillo cell - backgroundColor:', bg);
  console.log('Pasillo cell - borderColor:', border);
  
  testCell.remove();
  
  console.log('\nPara debuggear, abre la consola y ejecuta:');
  console.log('  window.debugPasillos()');
};