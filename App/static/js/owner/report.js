let orderValueChart, trafficChart;

  // Initialise both Chart.js charts
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
    trafficChart    = makeChart('trafficChart',    'line', 'Transactions',         '#ff6384');
  }

  // Fetch report data from Flask API
  async function loadReport(period = 'week') {
    try {
      const res = await fetch(`/api/owner/report?period=${period}`);
      if (!res.ok) throw new Error(`Server error ${res.status}`);
      const data = await res.json();
      updateCharts(data);
      updateTables(data);
    } catch (err) {
      console.error('Report load failed:', err);
      alert('Failed to load report data. Check the console for details.');
    }
  }

  function updateCharts(data) {
    orderValueChart.data.labels                  = data.daily_labels;
    orderValueChart.data.datasets[0].data        = data.avg_order_values;
    orderValueChart.update();

    trafficChart.data.labels                     = data.daily_labels;
    trafficChart.data.datasets[0].data           = data.traffic;
    trafficChart.update();
  }

  function updateTables(data) {
    // Top-selling items
    const topBody = document.getElementById('top-selling-body');
    if (data.top_selling.length === 0) {
      topBody.innerHTML = '<tr><td colspan="3">No data yet</td></tr>';
    } else {
      topBody.innerHTML = data.top_selling
        .map(item => `<tr><td>${item.rank}</td><td>${item.name}</td><td>${item.quantity}</td></tr>`)
        .join('');
    }

    // Frequently bought together
    const pairingBody = document.getElementById('pairing-body');
    if (data.frequently_bought_together.length === 0) {
      pairingBody.innerHTML = '<tr><td colspan="3">No data yet</td></tr>';
    } else {
      pairingBody.innerHTML = data.frequently_bought_together
        .map(p => `<tr><td>${p.item1}</td><td>${p.item2}</td><td>${p.count}</td></tr>`)
        .join('');
    }
  }

  document.addEventListener('DOMContentLoaded', () => {
    initCharts();
    loadReport('week');

    const toggle = document.getElementById('dropdown-toggle');
    const menu   = document.getElementById('dropdown-menu');

    // Toggle menu open/closed
    toggle.addEventListener('click', (e) => {
      e.stopPropagation();
      menu.classList.toggle('open');
    });

    // Pick an option
    menu.querySelectorAll('li').forEach(li => {
      li.addEventListener('click', () => {
        toggle.innerHTML = li.textContent + ' <span style="margin-left:6px;">▾</span>';
        menu.classList.remove('open');
        loadReport(li.dataset.value);
      });
    });

    //Close if clicking outside
    document.addEventListener('click', () => menu.classList.remove('open'));
  });