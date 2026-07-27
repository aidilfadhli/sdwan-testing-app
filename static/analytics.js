/**
 * Analytics Dashboard & Interactive Filter Chips (Phase 4)
 */

document.addEventListener('DOMContentLoaded', () => {
  initAnalyticsCharts();
  bindFilterChips();
});

let donutChartInstance = null;
let barChartInstance = null;

function initAnalyticsCharts() {
  const analyticsDataElement = document.getElementById('analytics-json-data');
  if (!analyticsDataElement) return;

  try {
    const data = JSON.parse(analyticsDataElement.textContent);
    renderDonutChart(data.summary);
    renderBarChart(data.throughput);
    renderTopFailedItems(data.top_failed_items);
  } catch (err) {
    console.error('Failed to parse analytics JSON:', err);
  }
}

function renderDonutChart(summary) {
  const ctx = document.getElementById('chart-pass-fail');
  if (!ctx || typeof Chart === 'undefined') return;

  if (donutChartInstance) {
    donutChartInstance.destroy();
  }

  const passVal = summary.pass || 0;
  const failVal = summary.fail || 0;
  const total = summary.total || 0;

  donutChartInstance = new Chart(ctx, {
    type: 'doughnut',
    data: {
      labels: ['PASS', 'FAIL'],
      datasets: [{
        data: [passVal, failVal],
        backgroundColor: ['#10b981', '#ef4444'],
        borderWidth: 2,
        borderColor: '#ffffff',
        hoverOffset: 4
      }]
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      plugins: {
        legend: {
          position: 'bottom',
          labels: {
            font: { family: 'Inter, system-ui, sans-serif', size: 12, weight: '600' },
            padding: 14,
            usePointStyle: true
          }
        },
        tooltip: {
          callbacks: {
            label: function(context) {
              const val = context.raw || 0;
              const pct = total > 0 ? ((val / total) * 100).toFixed(1) : 0;
              return ` ${context.label}: ${val} (${pct}%)`;
            }
          }
        }
      },
      cutout: '72%'
    }
  });
}

function renderBarChart(throughput) {
  const ctx = document.getElementById('chart-throughput');
  if (!ctx || typeof Chart === 'undefined') return;

  if (barChartInstance) {
    barChartInstance.destroy();
  }

  barChartInstance = new Chart(ctx, {
    type: 'bar',
    data: {
      labels: throughput.labels || [],
      datasets: [
        {
          label: 'PASS',
          data: throughput.pass_data || [],
          backgroundColor: '#10b981',
          borderRadius: 4
        },
        {
          label: 'FAIL',
          data: throughput.fail_data || [],
          backgroundColor: '#ef4444',
          borderRadius: 4
        }
      ]
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      scales: {
        x: {
          grid: { display: false },
          ticks: { font: { family: 'Inter, system-ui, sans-serif', size: 11 } }
        },
        y: {
          beginAtZero: true,
          ticks: { precision: 0, font: { family: 'Inter, system-ui, sans-serif', size: 11 } },
          grid: { color: 'rgba(226, 232, 240, 0.6)' }
        }
      },
      plugins: {
        legend: {
          position: 'top',
          labels: {
            font: { family: 'Inter, system-ui, sans-serif', size: 12, weight: '600' },
            usePointStyle: true
          }
        }
      }
    }
  });
}

function renderTopFailedItems(failedItems) {
  const container = document.getElementById('top-failed-container');
  if (!container) return;

  if (!failedItems || failedItems.length === 0) {
    container.innerHTML = `<div class="empty-failed"><i data-lucide="check-circle-2" style="color:#10b981; width:28px; height:28px;"></i><p>Tidak ada item gagal pada filter ini.</p></div>`;
    if (typeof lucide !== 'undefined') lucide.createIcons();
    return;
  }

  const maxCount = Math.max(...failedItems.map(i => i.count), 1);

  let html = '<ul class="failed-list">';
  failedItems.forEach(item => {
    const pct = Math.round((item.count / maxCount) * 100);
    html += `
      <li class="failed-item">
        <div class="failed-info">
          <span class="failed-name" title="${item.name}">${item.name}</span>
          <span class="failed-count">${item.count}x gagal</span>
        </div>
        <div class="failed-bar-bg">
          <div class="failed-bar-fill" style="width: ${pct}%;"></div>
        </div>
      </li>
    `;
  });
  html += '</ul>';
  container.innerHTML = html;
}

function bindFilterChips() {
  const filterSelects = document.querySelectorAll('.filter-select[data-filter]');
  filterSelects.forEach(select => {
    select.addEventListener('change', () => {
      const filterKey = select.getAttribute('data-filter');
      const filterVal = select.value;

      const url = new URL(window.location.href);
      if (filterVal === 'all') {
        url.searchParams.delete(filterKey);
      } else {
        url.searchParams.set(filterKey, filterVal);
      }
      // Reset to page 1 when filter or limit changes
      url.searchParams.delete('page');

      window.location.href = url.toString();
    });
  });
}

function changePage(pageNum) {
  const url = new URL(window.location.href);
  url.searchParams.set('page', pageNum);
  window.location.href = url.toString();
}
