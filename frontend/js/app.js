// Configuration
const API_BASE_URL = "http://127.0.0.1:8001";

let chart; // global variable for prediction chart
let multiYearChart; // global variable for multi-year chart

// Role-Based UI Logic
function updateUI() {
    const role = document.getElementById("role").value;
    
    // Hide all role-specific elements first
    const policyElements = document.querySelectorAll('.role-policy');
    const analystElements = document.querySelectorAll('.role-analyst');
    const publicElements = document.querySelectorAll('.role-public');
    
    [...policyElements, ...analystElements, ...publicElements].forEach(el => {
        el.style.display = 'none';
    });
    
    // Show elements based on selected role
    if (role === 'policy') {
        policyElements.forEach(el => el.style.display = 'block');
    } else if (role === 'analyst') {
        analystElements.forEach(el => el.style.display = 'block');
    } else if (role === 'public') {
        publicElements.forEach(el => el.style.display = 'block');
    }
}

// Initial UI update
window.onload = updateUI;

// Predict GDP function
async function predict() {
    const gdpValue = parseFloat(document.getElementById("gdp").value);
    let input = {
        gdp: gdpValue,
        inflation: parseFloat(document.getElementById("inflation").value),
        population: parseFloat(document.getElementById("population").value),
        unemployment: parseFloat(document.getElementById("unemployment").value),
        interest: parseFloat(document.getElementById("interest").value),
        deficit: parseFloat(document.getElementById("deficit").value),
        revenue: parseFloat(document.getElementById("revenue").value),
        expenditure: parseFloat(document.getElementById("expenditure").value)
    };

    try {
        let res = await fetch(`${API_BASE_URL}/predict`, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify(input)
        });

        let result = await res.json();

        if (result.status === "success") {
            // Show result container
            document.getElementById("resultContainer").style.display = "block";
            
            document.getElementById("prediction").innerText =
                "Predicted GDP: $" + result.predicted_gdp.toLocaleString(undefined, {minimumFractionDigits: 2});
            
            document.getElementById("insight").innerText = result.insight;

            // Advanced Results
            if (result.anomaly.includes("⚠️")) {
                alert(result.anomaly);
            }

            document.getElementById("risk").innerHTML = 
                `Min: $${(result.risk_analysis.min_gdp / 1e12).toFixed(2)}T | ` +
                `Max: $${(result.risk_analysis.max_gdp / 1e12).toFixed(2)}T | ` +
                `Avg: $${(result.risk_analysis.avg_gdp / 1e12).toFixed(2)}T`;

            document.getElementById("explanation").innerHTML = result.explanation.top_factors.join(", ");

            drawChart(input.gdp, result.predicted_gdp);
            
            // Render multi-year forecast chart
            if (result.future_predictions) {
                drawMultiYearChart(input.gdp, result.future_predictions);
            }
        } else {
            alert("Error: " + (result.message || result.error));
        }
    } catch (error) {
        alert("Error: API connection failed. Make sure the backend is running.");
    }
}

// Draw chart function (Bar chart comparison)
function drawChart(currentGDP, predictedGDP) {
    const ctx = document.getElementById('gdpChart');
    
    if (chart) {
        chart.destroy(); 
    }

    chart = new Chart(ctx, {
        type: 'bar',
        data: {
            labels: ['Current GDP', 'Predicted GDP'],
            datasets: [{
                label: 'GDP Comparison (USD)',
                data: [currentGDP, predictedGDP],
                backgroundColor: [
                    'rgba(52, 152, 219, 0.7)', // Blue for current
                    'rgba(46, 204, 113, 0.7)'  // Green for predicted
                ],
                borderColor: [
                    'rgba(52, 152, 219, 1)',
                    'rgba(46, 204, 113, 1)'
                ],
                borderWidth: 1
            }]
        },
        options: {
            responsive: true,
            scales: {
                y: {
                    beginAtZero: false,
                    ticks: {
                        callback: function(value) {
                            return '$' + (value / 1e12).toFixed(2) + 'T';
                        }
                    }
                }
            },
            plugins: {
                legend: { display: false },
                title: { display: true, text: 'GDP Growth Analysis' }
            }
        }
    });
}

// Multi-Year Forecast Chart
function drawMultiYearChart(currentGDP, futurePredictions) {
    const canvas = document.getElementById('multiYearChart');
    canvas.style.display = 'block';
    
    if (multiYearChart) {
        multiYearChart.destroy();
    }

    const labels = ['Current (2024)', ...futurePredictions.map(p => p.year)];
    const dataPoints = [currentGDP, ...futurePredictions.map(p => p.gdp)];

    multiYearChart = new Chart(canvas, {
        type: 'line',
        data: {
            labels: labels,
            datasets: [{
                label: '5-Year GDP Forecast (USD)',
                data: dataPoints,
                borderColor: '#2ecc71',
                backgroundColor: 'rgba(46, 204, 113, 0.1)',
                fill: true,
                tension: 0.4,
                pointRadius: 5,
                pointBackgroundColor: '#27ae60'
            }]
        },
        options: {
            responsive: true,
            scales: {
                y: {
                    ticks: {
                        callback: function(value) {
                            return '$' + (value / 1e12).toFixed(2) + 'T';
                        }
                    }
                }
            },
            plugins: {
                title: { display: true, text: 'Recursive 5-Year Trend Analysis' }
            }
        }
    });
}

// Upload CSV function
async function upload() {
    let fileInput = document.getElementById("fileInput");
    const role = document.getElementById("role").value;

    if (fileInput.files.length === 0) {
        alert("Please select a file");
        return;
    }

    let formData = new FormData();
    formData.append("file", fileInput.files[0]);

    try {
        let res = await fetch(`${API_BASE_URL}/analyst/upload`, {
            method: "POST",
            headers: { "role": role },
            body: formData
        });

        let data = await res.json();
        if (data.error) {
            alert("Error: " + data.error);
        } else {
            alert(data.message || "Upload successful");
        }
    } catch (error) {
        alert("Upload failed: API connection error.");
    }
}

// Retrain model function
async function retrainModel() {
    const statusDiv = document.getElementById("retrainStatus");
    const role = document.getElementById("role").value;
    
    statusDiv.innerText = "Training in progress... Please wait.";
    statusDiv.style.color = "#e67e22";

    try {
        let res = await fetch(`${API_BASE_URL}/analyst/train`, {
            method: "POST",
            headers: { "role": role }
        });

        let data = await res.json();
        if (data.message && !data.error) {
            statusDiv.innerText = "Success: " + data.message;
            statusDiv.style.color = "#27ae60";
        } else {
            statusDiv.innerText = "Error: " + (data.error || data.message || "Training failed");
            statusDiv.style.color = "#e74c3c";
        }
    } catch (error) {
        statusDiv.innerText = "Error: API connection failed.";
        statusDiv.style.color = "#e74c3c";
    }
}

// Resource Allocation Logic
async function allocateResources() {
    const names = document.getElementsByClassName("dept-name");
    const rois = document.getElementsByClassName("dept-roi");
    const impacts = document.getElementsByClassName("dept-impact");
    const risks = document.getElementsByClassName("dept-risk");

    let departments = [];
    for (let i = 0; i < names.length; i++) {
        departments.push({
            name: names[i].value,
            roi: parseFloat(rois[i].value),
            impact: parseFloat(impacts[i].value),
            risk: parseFloat(risks[i].value)
        });
    }

    try {
        let res = await fetch(`${API_BASE_URL}/allocate`, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ departments: departments })
        });

        let data = await res.json();
        if (data.status === "success") {
            const list = document.getElementById("rankingList");
            list.innerHTML = "";
            data.ranking.forEach((dept, index) => {
                const li = document.createElement("li");
                li.style.padding = "10px";
                li.style.marginBottom = "5px";
                li.style.background = index === 0 ? "#d4edda" : "#f8f9fa";
                li.style.borderRadius = "5px";
                li.style.listStyle = "none";
                li.innerHTML = `<strong>#${index + 1} ${dept.name}</strong> - Priority Score: ${dept.score}`;
                list.appendChild(li);
            });
            document.getElementById("allocationResults").style.display = "block";
        }
    } catch (error) {
        alert("Allocation failed: API connection error.");
    }
}
