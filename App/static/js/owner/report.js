let orderValueChart, trafficChart;
let currentPeriodLabel = 'Last 7 Days';

// ── Charts ────────────────────────────────────────────────────────

function initCharts() {
  const makeChart = (id, type, label, color) => new Chart(
    document.getElementById(id).getContext('2d'),
    {
      type,
      data: {
        labels: [],
        datasets: [{ label, data: [], backgroundColor: color, borderColor: color, fill: false }]
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        plugins: { legend: { display: false } },
        scales: { y: { beginAtZero: true, ticks: { precision: 0 } } }
      }
    }
  );

  orderValueChart = makeChart('orderValueChart', 'bar',  'Avg Order Value ($)', 'rgba(54,162,235,0.7)');
  trafficChart    = makeChart('trafficChart',    'line', 'Transactions',        '#ff6384');
}

// ── Data loading ──────────────────────────────────────────────────

async function loadReport(period = 'week') {
  try {
    const res = await fetch(`/api/owner/report?period=${period}`);
    if (!res.ok) throw new Error(`Server error ${res.status}`);
    const data = await res.json();
    updateCharts(data);
    updateSalesTables(data);
    updateRouteSection(data);
  } catch (err) {
    console.error('Report load failed:', err);
    alert('Failed to load report data. Check the console for details.');
  }
}

// ── Chart updates ─────────────────────────────────────────────────

function updateCharts(data) {
  orderValueChart.data.labels           = data.daily_labels;
  orderValueChart.data.datasets[0].data = data.avg_order_values;
  orderValueChart.update();

  trafficChart.data.labels              = data.daily_labels;
  trafficChart.data.datasets[0].data    = data.traffic;
  trafficChart.update();
}

// ── Sales tables ──────────────────────────────────────────────────

function updateSalesTables(data) {
  const topBody = document.getElementById('top-selling-body');
  topBody.innerHTML = data.top_selling.length === 0
    ? '<tr><td colspan="3">No data yet</td></tr>'
    : data.top_selling
        .map(item => `<tr><td>${item.rank}</td><td>${item.name}</td><td>${item.quantity}</td></tr>`)
        .join('');

  const pairingBody = document.getElementById('pairing-body');
  pairingBody.innerHTML = data.frequently_bought_together.length === 0
    ? '<tr><td colspan="3">No data yet</td></tr>'
    : data.frequently_bought_together
        .map(p => `<tr><td>${p.item1}</td><td>${p.item2}</td><td>${p.count}</td></tr>`)
        .join('');
}

// ── Route performance section ─────────────────────────────────────

function updateRouteSection(data) {
  // Revenue per route stat
  const rprEl = document.getElementById('stat-revenue-per-route');
  rprEl.textContent = data.revenue_per_route > 0
    ? `$${data.revenue_per_route.toLocaleString('en-US', { minimumFractionDigits: 2, maximumFractionDigits: 2 })}`
    : '—';

  // Most profitable routes
  const profitBody = document.getElementById('profitable-routes-body');
  profitBody.innerHTML = data.most_profitable_routes.length === 0
    ? '<tr><td colspan="3">No revenue data yet</td></tr>'
    : data.most_profitable_routes
        .map(r => `
          <tr>
            <td>${r.rank}</td>
            <td>${r.route_name}</td>
            <td>$${r.revenue.toLocaleString('en-US', { minimumFractionDigits: 2, maximumFractionDigits: 2 })}</td>
          </tr>`)
        .join('');

  // Most active routes
  const activeBody = document.getElementById('active-routes-body');
  activeBody.innerHTML = data.most_active_routes.length === 0
    ? '<tr><td colspan="2">No route history yet</td></tr>'
    : data.most_active_routes
        .map(r => `<tr><td>${r.route_name}</td><td>${r.runs}</td></tr>`)
        .join('');

  // Driver activity
  const driverBody = document.getElementById('driver-activity-body');
  driverBody.innerHTML = data.driver_activity.length === 0
    ? '<tr><td colspan="2">No route history yet</td></tr>'
    : data.driver_activity
        .map(d => `<tr><td>${d.driver_name}</td><td>${d.sessions}</td></tr>`)
        .join('');
}

// ── PDF Export ────────────────────────────────────────────────────

async function exportToPDF() {
  const btn = document.getElementById('export-pdf-btn');
  btn.textContent = 'Generating…';
  btn.disabled = true;

  try {
    const { jsPDF } = window.jspdf;
    const target    = document.getElementById('report-printable');

    // Temporarily hide the dropdown & export button from the capture
    const actionsEl = document.querySelector('.report-actions');
    actionsEl.style.visibility = 'hidden';

    const canvas = await html2canvas(target, {
      scale:           2,          // retina quality
      useCORS:         true,
      backgroundColor: '#ffffff',
      logging:         false,
    });

    actionsEl.style.visibility = 'visible';

    const imgData  = canvas.toDataURL('image/png');
    const pdf      = new jsPDF({ orientation: 'portrait', unit: 'mm', format: 'a4' });

    const pageW    = pdf.internal.pageSize.getWidth();
    const pageH    = pdf.internal.pageSize.getHeight();
    const margin   = 10;
    const usableW  = pageW - margin * 2;

    // Scale image to fit page width; paginate if taller than one page
    const imgW     = canvas.width;
    const imgH     = canvas.height;
    const ratio    = usableW / (imgW / (96 / 25.4)); // px → mm at 96 dpi
    const scaledH  = (imgH / (96 / 25.4)) * ratio;

    const usableH  = pageH - margin * 2;
    let   yOffset  = 0;

    while (yOffset < scaledH) {
      if (yOffset > 0) pdf.addPage();

      // Clip the portion of the image for this page
      const srcY    = (yOffset / scaledH) * imgH;
      const srcH    = Math.min((usableH / scaledH) * imgH, imgH - srcY);

      // Create a temporary canvas slice
      const slice   = document.createElement('canvas');
      slice.width   = imgW;
      slice.height  = srcH;
      slice.getContext('2d').drawImage(canvas, 0, srcY, imgW, srcH, 0, 0, imgW, srcH);

      pdf.addImage(slice.toDataURL('image/png'), 'PNG', margin, margin, usableW, (srcH / imgW) * usableW);
      yOffset += usableH;
    }

    const periodText = currentPeriodLabel.replace(/\s+/g, '_');
    pdf.save(`report_${periodText}_${new Date().toISOString().slice(0, 10)}.pdf`);

  } catch (err) {
    console.error('PDF export failed:', err);
    alert('❌ Failed to generate PDF. Please try again.');
  } finally {
    btn.textContent = 'Download PDF';
    btn.disabled    = false;
  }
}

// ── Init ──────────────────────────────────────────────────────────

document.addEventListener('DOMContentLoaded', () => {
  initCharts();
  loadReport('week');

  const toggle = document.getElementById('dropdown-toggle');
  const menu   = document.getElementById('dropdown-menu');

  toggle.addEventListener('click', e => {
    e.stopPropagation();
    menu.classList.toggle('open');
  });

  menu.querySelectorAll('li').forEach(li => {
    li.addEventListener('click', () => {
      currentPeriodLabel = li.textContent.trim();
      toggle.innerHTML   = currentPeriodLabel + ' <span style="margin-left:6px;">▾</span>';
      menu.classList.remove('open');
      loadReport(li.dataset.value);
    });
  });

  document.addEventListener('click', () => menu.classList.remove('open'));

  document.getElementById('export-pdf-btn').addEventListener('click', exportToPDF);
});