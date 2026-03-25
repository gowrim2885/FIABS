// Budget Forecast Chart
const ctx1 = document.getElementById('budgetForecastChart');
new Chart(ctx1, {
  type: 'line',
  data: {
    labels: ['2026', '2027', '2028', '2029', '2030'],
    datasets: [{
      label: 'Total Budget Forecast',
      data: [100, 120, 140, 160, 180],
      borderColor: 'blue',
      fill: false
    }]
  }
});

// Forecasting Chart
const ctx2 = document.getElementById('forecastChart');
new Chart(ctx2, {
  type: 'bar',
  data: {
    labels: ['Health', 'Education', 'Defense', 'Infrastructure'],
    datasets: [{
      label: 'Forecasted Budget (in Millions)',
      data: [50, 70, 90, 60],
      backgroundColor: ['red', 'green', 'blue', 'orange']
    }]
  }
});

// Risk Simulation Chart
const ctx3 = document.getElementById('riskChart');
new Chart(ctx3, {
  type: 'pie',
  data: {
    labels: ['Recession', 'Inflation Surge', 'Natural Disaster'],
    datasets: [{
      data: [25, 15, 10],
      backgroundColor: ['purple', 'yellow', 'cyan']
    }]
  }
});

// Resource Allocation Chart
const ctx4 = document.getElementById('allocationChart');
new Chart(ctx4, {
  type: 'radar',
  data: {
    labels: ['ROI', 'Impact', 'Risk'],
    datasets: [{
      label: 'Health',
      data: [80, 70, 60],
      borderColor: 'red'
    },{
      label: 'Education',
      data: [70, 85, 50],
      borderColor: 'blue'
    }]
  }
});

// DSS Query Simulation
function runDSS() {
  const query = document.getElementById('queryInput').value;
  let output = "";
  if(query.toLowerCase().includes("funding")) {
    output = "Recommendation: Increase funding for Education due to high socio-economic impact.";
  } else {
    output = "No recommendation available for this query.";
  }
  document.getElementById('dssOutput').innerText = output;
}
