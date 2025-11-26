// API Configuration
const apiBase = 'http://127.0.0.1:5000';

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

// State
let packageCount = 1;
let lastPayload = null;
let lastResult = null;

// Initialize
init();

function init() {
  setupEventListeners();
  // Create the first package tab
  addPackageTab();
  updateSummary();
}

function setupEventListeners() {
  startBtn.addEventListener('click', showForm);
  cancelBtn.addEventListener('click', hideForm);
  backToFormBtn.addEventListener('click', backToForm);
  loadDefaultsBtn.addEventListener('click', loadDefaults);
  addTabBtn.addEventListener('click', addPackageTab);
  simulationForm.addEventListener('submit', runSimulation);
  exportBtn.addEventListener('click', exportToExcel);
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
    const data = await res.json();
    
    if (!data || !data.paquetes || !Array.isArray(data.paquetes)) {
      showNotification('Error: datos de defaults inválidos', 'error');
      return;
    }
    
    // Clear existing tabs except first
    const existingTabs = document.querySelectorAll('.tab-button');
    existingTabs.forEach((tab, idx) => {
      if (idx > 0) {
        const index = tab.dataset.tab;
        const tabBtn = document.querySelector(`.tab-button[data-tab="${index}"]`);
        const tabPane = document.querySelector(`.tab-pane[data-pane="${index}"]`);
        if (tabBtn) tabBtn.remove();
        if (tabPane) tabPane.remove();
      }
    });
    
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
    showNotification('Ejemplo cargado correctamente');
  } catch (err) {
    showNotification('Error al cargar ejemplo: ' + err, 'error');
  }
}

// Run Simulation
async function runSimulation(e) {
  e.preventDefault();
  
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

// Render Warehouse Grid
function renderWarehouseGrid(data) {
  const paquetes = lastPayload.paquetes || [];
  const inicio = lastPayload.inicio || [0, 0];
  const posFinal = data.pos_final || [0, 0];
  
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
  
  // Create grid
  warehouseGrid.style.gridTemplateColumns = `repeat(${cols}, 40px)`;
  warehouseGrid.innerHTML = '';
  
  // Initialize grid data
  const grid = Array(rows).fill(null).map(() => Array(cols).fill(''));
  
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
  
  // Render grid
  for (let i = 0; i < rows; i++) {
    for (let j = 0; j < cols; j++) {
      const cell = document.createElement('div');
      cell.className = `grid-cell ${grid[i][j]}`;
      
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
      }
      
      warehouseGrid.appendChild(cell);
    }
  }
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