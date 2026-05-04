// ── State ───────────────────────────────────────────────
let allExpenses   = [];
let allCategories = [];
let categoryChart = null;
let monthlyChart  = null;

// ── Init ────────────────────────────────────────────────
document.addEventListener('DOMContentLoaded', () => {
  loadCategories();
  loadDashboard();
  setDefaultDate();
});

// ── Fetch Helpers ───────────────────────────────────────
async function api(url, method = 'GET', body = null) {
  const opts = {
    method,
    headers: { 'Content-Type': 'application/json' }
  };
  if (body) opts.body = JSON.stringify(body);
  const res  = await fetch(url, opts);
  return res.json();
}

// ── Load Categories ─────────────────────────────────────
async function loadCategories() {
  allCategories = await api('/api/categories');

  // Fill modal dropdown
  const sel = document.getElementById('f-category');
  sel.innerHTML = allCategories.map(c =>
    `<option value="${c.id}">${c.icon} ${c.name}</option>`
  ).join('');

  // Fill filter dropdown
  const filter = document.getElementById('filter-category');
  filter.innerHTML = `<option value="">All Categories</option>` +
    allCategories.map(c =>
      `<option value="${c.name}">${c.icon} ${c.name}</option>`
    ).join('');
}

// ── Dashboard ───────────────────────────────────────────
async function loadDashboard() {
  const data = await api('/api/analytics');

  // Summary cards
  const s = data.summary;
  if (s && Object.keys(s).length) {
    document.getElementById('total-spent').textContent  = `₹${s.total_spent.toLocaleString()}`;
    document.getElementById('this-month').textContent   = `₹${s.this_month.toLocaleString()}`;
    document.getElementById('avg-expense').textContent  = `₹${s.average_expense.toLocaleString()}`;
    document.getElementById('highest-expense').textContent = `₹${s.highest_expense.amount.toLocaleString()}`;
  }

  // Charts
  renderCategoryChart(data.categories);
  renderMonthlyChart(data.monthly);

  // Load expenses for table
  allExpenses = await api('/api/expenses');
}

// ── Category Donut Chart ────────────────────────────────
function renderCategoryChart(categories) {
  const ctx = document.getElementById('categoryChart').getContext('2d');
  if (categoryChart) categoryChart.destroy();

  categoryChart = new Chart(ctx, {
    type: 'doughnut',
    data: {
      labels: categories.map(c => c.category),
      datasets: [{
        data:            categories.map(c => c.amount),
        backgroundColor: ['#FF6384','#36A2EB','#FFCE56','#4BC0C0','#9966FF','#FF9F40','#C9CBCF','#7CFC00'],
        borderWidth: 2,
        borderColor: getComputedStyle(document.documentElement)
                       .getPropertyValue('--surface') || '#fff'
      }]
    },
    options: {
      responsive: true,
      plugins: {
        legend: { position: 'bottom', labels: { padding: 16, font: { size: 12 } } }
      },
      cutout: '65%'
    }
  });
}

// ── Monthly Bar Chart ───────────────────────────────────
function renderMonthlyChart(monthly) {
  const ctx = document.getElementById('monthlyChart').getContext('2d');
  if (monthlyChart) monthlyChart.destroy();

  monthlyChart = new Chart(ctx, {
    type: 'bar',
    data: {
      labels: monthly.map(m => m.month),
      datasets: [{
        label:           'Spending (₹)',
        data:            monthly.map(m => m.amount),
        backgroundColor: '#6c63ff',
        borderRadius:    6,
        borderSkipped:   false
      }]
    },
    options: {
      responsive: true,
      plugins: { legend: { display: false } },
      scales: {
        y: {
          beginAtZero: true,
          grid: { color: 'rgba(0,0,0,0.05)' },
          ticks: { callback: v => `₹${v.toLocaleString()}` }
        },
        x: { grid: { display: false } }
      }
    }
  });
}

// ── Expenses Table ──────────────────────────────────────
function renderExpenses(expenses) {
  const tbody = document.getElementById('expenses-table');
  if (!expenses.length) {
    tbody.innerHTML = `<tr><td colspan="6" style="text-align:center;padding:32px;color:var(--text-muted)">No expenses found. Add one or load demo data!</td></tr>`;
    return;
  }
  tbody.innerHTML = expenses.map(e => `
    <tr>
      <td><strong>${e.title}</strong></td>
      <td>
        <span class="category-badge" style="color:${e.color}">
          ${e.icon} ${e.category}
        </span>
      </td>
      <td><strong>₹${parseFloat(e.amount).toLocaleString()}</strong></td>
      <td>${formatDate(e.expense_date)}</td>
      <td style="color:var(--text-muted)">${e.note || '—'}</td>
      <td>
        <div class="action-btns">
          <button class="btn-edit"   onclick="editExpense(${e.id})">✏️ Edit</button>
          <button class="btn-delete" onclick="deleteExpense(${e.id})">🗑️</button>
        </div>
      </td>
    </tr>
  `).join('');
}

// ── Filter Expenses ─────────────────────────────────────
function filterExpenses() {
  const search = document.getElementById('search-input').value.toLowerCase();
  const cat    = document.getElementById('filter-category').value;

  const filtered = allExpenses.filter(e => {
    const matchSearch = e.title.toLowerCase().includes(search) ||
                        (e.note || '').toLowerCase().includes(search);
    const matchCat    = !cat || e.category === cat;
    return matchSearch && matchCat;
  });

  renderExpenses(filtered);
}

// ── AI Insights ─────────────────────────────────────────
async function loadInsights() {
  const data = await api('/api/analytics');
  const container = document.getElementById('insights-container');

  if (!data.insights || !data.insights.length) {
    container.innerHTML = `<p style="color:var(--text-muted)">No insights yet. Add expenses or load demo data first!</p>`;
    return;
  }

  container.innerHTML = data.insights.map(i => `
    <div class="insight-card ${i.type}">
      <div class="insight-icon">${i.icon}</div>
      <div class="insight-text">${i.message}</div>
    </div>
  `).join('');
}

// ── Section Navigation ──────────────────────────────────
function showSection(name) {
  // Hide all sections
  ['dashboard','expenses','insights'].forEach(s => {
    document.getElementById(`section-${s}`).style.display = 'none';
  });

  // Show selected
  document.getElementById(`section-${name}`).style.display = 'block';
  document.getElementById('page-title').textContent =
    name.charAt(0).toUpperCase() + name.slice(1);

  // Update nav active state
  document.querySelectorAll('.nav-item').forEach(el => el.classList.remove('active'));
  event.target.classList.add('active');

  // Load data for section
  if (name === 'expenses') renderExpenses(allExpenses);
  if (name === 'insights') loadInsights();
}

// ── Modal ───────────────────────────────────────────────
function openModal() {
  document.getElementById('modal-title').textContent = 'Add Expense';
  document.getElementById('expense-id').value = '';
  document.getElementById('f-title').value    = '';
  document.getElementById('f-amount').value   = '';
  document.getElementById('f-note').value     = '';
  setDefaultDate();
  document.getElementById('modal-overlay').style.display = 'block';
  document.getElementById('modal').style.display         = 'block';
}

function closeModal() {
  document.getElementById('modal-overlay').style.display = 'none';
  document.getElementById('modal').style.display         = 'none';
}

function setDefaultDate() {
  const today = new Date().toISOString().split('T')[0];
  const dateInput = document.getElementById('f-date');
  if (dateInput) dateInput.value = today;
}

// ── Save Expense (Add or Edit) ──────────────────────────
async function saveExpense() {
  const id     = document.getElementById('expense-id').value;
  const title  = document.getElementById('f-title').value.trim();
  const amount = document.getElementById('f-amount').value;
  const cat    = document.getElementById('f-category').value;
  const date   = document.getElementById('f-date').value;
  const note   = document.getElementById('f-note').value.trim();

  if (!title || !amount || !cat || !date) {
    showToast('⚠️ Please fill all required fields!');
    return;
  }

  const body = { title, amount: parseFloat(amount), category_id: parseInt(cat), expense_date: date, note };

  if (id) {
    await api(`/api/expenses/${id}`, 'PUT', body);
    showToast('✅ Expense updated!');
  } else {
    await api('/api/expenses', 'POST', body);
    showToast('✅ Expense added!');
  }

  closeModal();
  allExpenses = await api('/api/expenses');
  loadDashboard();
}

// ── Edit Expense ────────────────────────────────────────
function editExpense(id) {
  const e = allExpenses.find(x => x.id === id);
  if (!e) return;

  document.getElementById('modal-title').textContent = 'Edit Expense';
  document.getElementById('expense-id').value = e.id;
  document.getElementById('f-title').value    = e.title;
  document.getElementById('f-amount').value   = e.amount;
  document.getElementById('f-date').value     = e.expense_date;
  document.getElementById('f-note').value     = e.note || '';

  // Set category dropdown
  const cat = allCategories.find(c => c.name === e.category);
  if (cat) document.getElementById('f-category').value = cat.id;

  document.getElementById('modal-overlay').style.display = 'block';
  document.getElementById('modal').style.display         = 'block';
}

// ── Delete Expense ──────────────────────────────────────
async function deleteExpense(id) {
  if (!confirm('Delete this expense?')) return;
  await api(`/api/expenses/${id}`, 'DELETE');
  showToast('🗑️ Expense deleted!');
  allExpenses = allExpenses.filter(e => e.id !== id);
  renderExpenses(allExpenses);
  loadDashboard();
}

// ── Demo Data ───────────────────────────────────────────
async function loadDemo() {
  showToast('⏳ Loading demo data...');
  await api('/api/demo', 'POST');
  allExpenses = await api('/api/expenses');
  await loadDashboard();
  showToast('🎲 Demo data loaded!');
}

async function clearDemo() {
  if (!confirm('Clear all demo data?')) return;
  await api('/api/demo', 'DELETE');
  allExpenses = await api('/api/expenses');
  await loadDashboard();
  showToast('🗑️ Demo data cleared!');
}

// ── Theme Toggle ─────────────────────────────────────────
function toggleTheme() {
  const html = document.documentElement;
  const isDark = html.getAttribute('data-theme') === 'dark';
  html.setAttribute('data-theme', isDark ? 'light' : 'dark');
  document.querySelector('.theme-btn').textContent = isDark ? '🌙 Dark Mode' : '☀️ Light Mode';

  // Redraw charts for new theme
  loadDashboard();
}

// ── Toast Notification ───────────────────────────────────
function showToast(msg) {
  let toast = document.querySelector('.toast');
  if (!toast) {
    toast = document.createElement('div');
    toast.className = 'toast';
    document.body.appendChild(toast);
  }
  toast.textContent = msg;
  toast.classList.add('show');
  setTimeout(() => toast.classList.remove('show'), 3000);
}

// ── Format Date ──────────────────────────────────────────
function formatDate(dateStr) {
  const d = new Date(dateStr);
  return d.toLocaleDateString('en-IN', { day: 'numeric', month: 'short', year: 'numeric' });
  async function doLogout() {
  await api('/api/logout', 'POST');
  window.location.href = '/';
}
}