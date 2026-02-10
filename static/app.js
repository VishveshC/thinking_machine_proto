// ============================================================================
// FraudGuard - Main JavaScript File
// ============================================================================

// Dark Theme Toggle
function initThemeToggle() {
    const themeToggle = document.getElementById('themeToggle');
    const html = document.documentElement;

    // Load saved theme
    const savedTheme = localStorage.getItem('theme') || 'light';
    html.setAttribute('data-theme', savedTheme);

    if (themeToggle) {
        themeToggle.checked = savedTheme === 'dark';

        themeToggle.addEventListener('change', function () {
            const theme = this.checked ? 'dark' : 'light';
            html.setAttribute('data-theme', theme);
            localStorage.setItem('theme', theme);
        });
    }
}

// Webcam Face Recognition
let videoStream = null;

function updateFaceVerificationButton(isVerified) {
    const faceButton = document.getElementById('faceVerificationButton');
    if (!faceButton) {
        return;
    }

    if (isVerified) {
        faceButton.classList.remove('btn-outline-primary');
        faceButton.classList.add('btn-success');
        faceButton.innerHTML = '<i class="fas fa-check me-2"></i>Face Verified';
    } else {
        faceButton.classList.remove('btn-success');
        faceButton.classList.add('btn-outline-primary');
        faceButton.innerHTML = '<i class="fas fa-camera me-2"></i>Verify Face';
    }
}

function startWebcam() {
    const video = document.getElementById('webcam');
    const canvas = document.getElementById('faceCanvas');

    if (navigator.mediaDevices && navigator.mediaDevices.getUserMedia) {
        navigator.mediaDevices.getUserMedia({ video: true })
            .then(function (stream) {
                videoStream = stream;
                video.srcObject = stream;
                video.play();

                // Simulate face detection after 2 seconds
                setTimeout(() => {
                    captureFace();
                }, 2000);
            })
            .catch(function (error) {
                console.log("Webcam error: " + error);
                // Fallback: auto-verify after 1 second
                setTimeout(() => {
                    document.getElementById('faceVerificationStatus').textContent = 'Face verified! (Demo mode)';
                    document.getElementById('faceVerificationStatus').className = 'text-success mt-2';
                    document.getElementById('face_verification').checked = true;
                    updateFaceVerificationButton(true);
                    setTimeout(() => {
                        const modal = bootstrap.Modal.getInstance(document.getElementById('faceRecognitionModal'));
                        if (modal) modal.hide();
                    }, 1500);
                }, 1000);
            });
    }
}

function captureFace() {
    const video = document.getElementById('webcam');
    const canvas = document.getElementById('faceCanvas');
    const context = canvas.getContext('2d');

    // Draw video frame to canvas
    canvas.width = video.videoWidth;
    canvas.height = video.videoHeight;
    context.drawImage(video, 0, 0, canvas.width, canvas.height);

    // Simulate face recognition (always returns true for demo)
    document.getElementById('faceVerificationStatus').textContent = 'Face recognized successfully!';
    document.getElementById('faceVerificationStatus').className = 'text-success mt-2';
    document.getElementById('face_verification').checked = true;
    updateFaceVerificationButton(true);

    // Stop camera
    if (videoStream) {
        videoStream.getTracks().forEach(track => track.stop());
    }

    // Close modal after 1.5 seconds
    setTimeout(() => {
        const modal = bootstrap.Modal.getInstance(document.getElementById('faceRecognitionModal'));
        if (modal) modal.hide();
    }, 1500);
}

function showFaceRecognition() {
    const modalEl = document.getElementById('faceRecognitionModal');
    if (!modalEl) {
        // Fallback: auto-verify without modal
        console.log("Face recognition modal not found, auto-verifying");
        document.getElementById('face_verification').checked = true;
        updateFaceVerificationButton(true);
        return;
    }

    const modal = new bootstrap.Modal(modalEl);
    modal.show();

    // Reset status
    const statusEl = document.getElementById('faceVerificationStatus');
    if (statusEl) {
        statusEl.textContent = 'Initializing camera...';
        statusEl.className = 'text-muted mt-2';
    }

    // Start webcam after modal is shown
    modalEl.addEventListener('shown.bs.modal', function () {
        startWebcam();
    }, { once: true });
}

// Simulation Data Type Selector
function selectDataType(type) {
    document.getElementById('data_type').value = type;

    // Update button states
    document.querySelectorAll('.data-type-btn').forEach(btn => {
        btn.classList.remove('active', 'btn-primary');
        btn.classList.add('btn-outline-primary');
    });

    const selectedBtn = document.querySelector(`[data-type="${type}"]`);
    if (selectedBtn) {
        selectedBtn.classList.remove('btn-outline-primary');
        selectedBtn.classList.add('active', 'btn-primary');
    }

    // Update placeholder
    const input = document.getElementById('input_data');
    const placeholders = {
        'email': 'Enter email content to analyze...',
        'sms': 'Enter SMS message to analyze...',
        'phone': 'Enter phone number to analyze...'
    };
    if (input) {
        input.placeholder = placeholders[type] || 'Enter data to analyze...';
    }
}

// Balance Chart with Linear Regression - Optimized for Visual Appeal
function createBalanceChart(canvasId, balanceData, projectionDays = 14) {
    const ctx = document.getElementById(canvasId);
    if (!ctx) return;

    // Generate dummy historical data (last 14 days) - Less cluttered
    const historicalDays = 14;
    const dates = [];
    const balances = [];
    const currentBalance = balanceData.current;

    // Generate past data with some variance
    for (let i = historicalDays; i >= 0; i--) {
        const date = new Date();
        date.setDate(date.getDate() - i);
        dates.push(date.toLocaleDateString('en-US', { month: 'short', day: 'numeric' }));

        // Simulate balance changes
        const variance = (Math.random() - 0.5) * 800;
        const balance = currentBalance + variance - (i * 30);
        balances.push(Math.max(0, balance));
    }

    // Linear regression for projection
    const n = balances.length;
    const xValues = Array.from({ length: n }, (_, i) => i);
    const yValues = balances;

    const sumX = xValues.reduce((a, b) => a + b, 0);
    const sumY = yValues.reduce((a, b) => a + b, 0);
    const sumXY = xValues.reduce((sum, x, i) => sum + x * yValues[i], 0);
    const sumX2 = xValues.reduce((sum, x) => sum + x * x, 0);

    const slope = (n * sumXY - sumX * sumY) / (n * sumX2 - sumX * sumX);
    const intercept = (sumY - slope * sumX) / n;

    // Generate future projections
    const projectionDates = [];
    const projectionBalances = [];

    for (let i = 1; i <= projectionDays; i++) {
        const date = new Date();
        date.setDate(date.getDate() + i);
        projectionDates.push(date.toLocaleDateString('en-US', { month: 'short', day: 'numeric' }));

        const projectedBalance = slope * (n + i) + intercept;
        projectionBalances.push(Math.max(0, projectedBalance));
    }

    new Chart(ctx, {
        type: 'line',
        data: {
            labels: [...dates, ...projectionDates],
            datasets: [{
                label: 'Historical Balance',
                data: [...balances, ...Array(projectionDays).fill(null)],
                borderColor: 'rgba(102, 126, 234, 1)',
                backgroundColor: 'rgba(102, 126, 234, 0.1)',
                tension: 0.4,
                fill: true,
                borderWidth: 3,
                pointRadius: 0,
                pointHoverRadius: 6,
                pointHoverBackgroundColor: 'rgba(102, 126, 234, 1)',
                pointHoverBorderColor: '#fff',
                pointHoverBorderWidth: 2
            }, {
                label: 'Projected Balance',
                data: [...Array(historicalDays + 1).fill(null), ...projectionBalances],
                borderColor: 'rgba(118, 75, 162, 1)',
                backgroundColor: 'rgba(118, 75, 162, 0.1)',
                borderDash: [8, 4],
                tension: 0.4,
                fill: true,
                borderWidth: 3,
                pointRadius: 0,
                pointHoverRadius: 6,
                pointHoverBackgroundColor: 'rgba(118, 75, 162, 1)',
                pointHoverBorderColor: '#fff',
                pointHoverBorderWidth: 2
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            interaction: {
                mode: 'index',
                intersect: false,
            },
            plugins: {
                legend: {
                    display: true,
                    position: 'top',
                    labels: {
                        usePointStyle: true,
                        padding: 15,
                        font: {
                            size: 12,
                            weight: '600',
                            family: 'Inter'
                        }
                    }
                },
                tooltip: {
                    mode: 'index',
                    intersect: false,
                    backgroundColor: 'rgba(0, 0, 0, 0.8)',
                    padding: 12,
                    cornerRadius: 8,
                    titleFont: {
                        size: 13,
                        weight: '600'
                    },
                    bodyFont: {
                        size: 12
                    },
                    callbacks: {
                        label: function (context) {
                            let label = context.dataset.label || '';
                            if (label) {
                                label += ': ';
                            }
                            if (context.parsed.y !== null) {
                                label += '₹' + context.parsed.y.toFixed(2);
                            }
                            return label;
                        }
                    }
                }
            },
            scales: {
                y: {
                    beginAtZero: true,
                    grid: {
                        color: 'rgba(0, 0, 0, 0.05)',
                        drawBorder: false
                    },
                    ticks: {
                        callback: function (value) {
                            return '₹' + value.toLocaleString();
                        },
                        font: {
                            size: 11,
                            family: 'Inter'
                        }
                    }
                },
                x: {
                    grid: {
                        display: false,
                        drawBorder: false
                    },
                    ticks: {
                        maxRotation: 45,
                        minRotation: 45,
                        font: {
                            size: 10,
                            family: 'Inter'
                        }
                    }
                }
            }
        }
    });
}

// Investment Chart - Premium Styling
function createInvestmentChart(canvasId) {
    const ctx = document.getElementById(canvasId);
    if (!ctx) return;

    // Dummy investment data
    new Chart(ctx, {
        type: 'doughnut',
        data: {
            labels: ['Tech Stocks', 'Bonds', 'Cryptocurrency', 'Real Estate', 'Cash'],
            datasets: [{
                data: [35, 25, 20, 15, 5],
                backgroundColor: [
                    'rgba(102, 126, 234, 0.9)',
                    'rgba(118, 75, 162, 0.9)',
                    'rgba(79, 172, 254, 0.9)',
                    'rgba(17, 153, 142, 0.9)',
                    'rgba(159, 163, 167, 0.9)'
                ],
                borderWidth: 0,
                hoverOffset: 15
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            cutout: '65%',
            plugins: {
                legend: {
                    position: 'bottom',
                    labels: {
                        usePointStyle: true,
                        padding: 15,
                        font: {
                            size: 12,
                            weight: '600',
                            family: 'Inter'
                        }
                    }
                },
                tooltip: {
                    backgroundColor: 'rgba(0, 0, 0, 0.8)',
                    padding: 12,
                    cornerRadius: 8,
                    titleFont: {
                        size: 13,
                        weight: '600'
                    },
                    bodyFont: {
                        size: 12
                    },
                    callbacks: {
                        label: function (context) {
                            return context.label + ': ' + context.parsed + '%';
                        }
                    }
                }
            }
        }
    });
}

// Initialize on page load
document.addEventListener('DOMContentLoaded', function () {
    initThemeToggle();

    // Clean up webcam on modal close
    const faceModal = document.getElementById('faceRecognitionModal');
    if (faceModal) {
        faceModal.addEventListener('hidden.bs.modal', function () {
            if (videoStream) {
                videoStream.getTracks().forEach(track => track.stop());
                videoStream = null;
            }
        });
    }
});
