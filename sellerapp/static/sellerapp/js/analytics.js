/**
 * FITFUEL AI - ENTERPRISE ANALYTICS DASHBOARD SCRIPTS
 * Handles dynamic Chart.js graphing, counter animations, search/filter table operations.
 */

document.addEventListener("DOMContentLoaded", function () {
    // 1. Initialize Display Date
    initDateDisplay();

    // 2. Count-Up Animations for statistics cards
    animateCounters();

    // 3. Render Chart.js Visualizations
    initCharts();

    // 4. Set up Recent Orders Table interactions
    initRecentOrdersTable();

    // 5. Setup refresh button handler
    const refreshBtn = document.getElementById('btn-refresh');
    if (refreshBtn) {
        refreshBtn.addEventListener('click', function () {
            // Apply slight loading animation to cards
            const cards = document.querySelectorAll('.stat-card');
            cards.forEach(card => card.classList.add('loading-skeleton'));
            setTimeout(() => {
                window.location.reload();
            }, 600);
        });
    }

    // 6. Fetch AI Insights
    loadAiInsights();

    // 7. Initialize AI Business Insights animations
    initBusinessInsights();
});

/**
 * Display current formatted date in subtitle
 */
function initDateDisplay() {
    const dateEl = document.getElementById("current-date-display");
    if (dateEl) {
        const options = { weekday: 'long', year: 'numeric', month: 'long', day: 'numeric' };
        const today = new Date();
        dateEl.textContent = `As of ${today.toLocaleDateString("en-US", options)} - Real-time metrics.`;
    }
}

/**
 * Animate statistic card counters from 0 to actual value
 */
function animateCounters() {
    const counters = document.querySelectorAll('.card-number');
    counters.forEach(counter => {
        const targetValAttr = counter.getAttribute('data-target');
        const prefix = counter.getAttribute('data-prefix') || '';
        const target = parseFloat(targetValAttr) || 0;
        const isFloat = targetValAttr.includes('.') || prefix === '₹';
        const duration = 1200; // Animation duration in ms
        const startTime = performance.now();

        function updateAnimation(currentTime) {
            const elapsed = currentTime - startTime;
            const progress = Math.min(elapsed / duration, 1);
            
            // Ease-out quad function
            const easeProgress = progress * (2 - progress);
            const currentVal = easeProgress * target;

            if (isFloat) {
                counter.textContent = prefix + currentVal.toFixed(2);
            } else {
                counter.textContent = prefix + Math.floor(currentVal).toLocaleString();
            }

            if (progress < 1) {
                requestAnimationFrame(updateAnimation);
            } else {
                if (isFloat) {
                    counter.textContent = prefix + target.toFixed(2);
                } else {
                    counter.textContent = prefix + target.toLocaleString();
                }
            }
        }
        requestAnimationFrame(updateAnimation);
    });
}

/**
 * Initialize all 6 Chart.js graphs using injected context data
 */
function initCharts() {
    const chartDataEl = document.getElementById('analytics-chart-data');
    if (!chartDataEl) return;

    let data = {};
    try {
        let rawText = chartDataEl.textContent;
        // Clean single quotes in Python lists output (e.g. ['Jan', 'Feb'] -> ["Jan", "Feb"])
        let cleanedText = rawText.replace(/'/g, '"');
        data = JSON.parse(cleanedText);
    } catch (e) {
        console.error("Failed to parse chart data JSON:", e);
        return;
    }

    // Default Chart Config Options
    const defaultFontFamily = "'Plus Jakarta Sans', sans-serif";
    Chart.defaults.font.family = defaultFontFamily;
    Chart.defaults.color = "#475569";
    Chart.defaults.plugins.legend.labels.boxWidth = 12;

    // 1. Monthly Revenue Chart (Line)
    const revCtx = document.getElementById('chart-monthly-revenue');
    if (revCtx) {
        new Chart(revCtx, {
            type: 'line',
            data: {
                labels: data.monthly_labels || [],
                datasets: [{
                    label: 'Revenue (₹)',
                    data: data.monthly_revenue || [],
                    borderColor: '#3b82f6',
                    backgroundColor: 'rgba(59, 130, 246, 0.1)',
                    borderWidth: 3.5,
                    fill: true,
                    tension: 0.35,
                    pointBackgroundColor: '#1e3a8a',
                    pointBorderColor: '#ffffff',
                    pointBorderWidth: 2,
                    pointRadius: 4,
                    pointHoverRadius: 6
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: { display: false }
                },
                scales: {
                    y: {
                        beginAtZero: true,
                        grid: { color: 'rgba(0,0,0,0.05)' }
                    },
                    x: {
                        grid: { display: false }
                    }
                }
            }
        });
    }

    // 2. Monthly Orders Chart (Bar)
    const ordCtx = document.getElementById('chart-monthly-orders');
    if (ordCtx) {
        new Chart(ordCtx, {
            type: 'bar',
            data: {
                labels: data.monthly_labels || [],
                datasets: [{
                    label: 'Orders Count',
                    data: data.monthly_orders || [],
                    backgroundColor: '#8b5cf6',
                    hoverBackgroundColor: '#7c3aed',
                    borderRadius: 8,
                    borderSkipped: false
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: { display: false }
                },
                scales: {
                    y: {
                        beginAtZero: true,
                        grid: { color: 'rgba(0,0,0,0.05)' }
                    },
                    x: {
                        grid: { display: false }
                    }
                }
            }
        });
    }

    // 3. Category Sales Chart (Doughnut)
    const catCtx = document.getElementById('chart-category-sales');
    if (catCtx) {
        new Chart(catCtx, {
            type: 'doughnut',
            data: {
                labels: data.category_names || [],
                datasets: [{
                    data: data.category_sales || [],
                    backgroundColor: ['#10b981', '#3b82f6', '#f59e0b', '#ec4899', '#8b5cf6', '#06b6d4'],
                    borderWidth: 3,
                    borderColor: '#ffffff'
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: { position: 'bottom' }
                },
                cutout: '65%'
            }
        });
    }

    // 4. Payment Methods Chart (Pie)
    const payCtx = document.getElementById('chart-payment-methods');
    if (payCtx) {
        new Chart(payCtx, {
            type: 'pie',
            data: {
                labels: data.payment_labels || [],
                datasets: [{
                    data: data.payment_counts || [],
                    backgroundColor: ['#10b981', '#3b82f6', '#f59e0b', '#a855f7'],
                    borderWidth: 2,
                    borderColor: '#ffffff'
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: { position: 'bottom' }
                }
            }
        });
    }

    // 5. Order Status Chart (Polar Area)
    const statCtx = document.getElementById('chart-order-status');
    if (statCtx) {
        new Chart(statCtx, {
            type: 'polarArea',
            data: {
                labels: data.status_labels || [],
                datasets: [{
                    data: data.status_counts || [],
                    backgroundColor: [
                        'rgba(245, 158, 11, 0.7)',  // Pending
                        'rgba(59, 130, 246, 0.7)',  // Confirmed
                        'rgba(139, 92, 246, 0.7)',  // Packed
                        'rgba(6, 182, 212, 0.7)',   // Shipped
                        'rgba(16, 185, 129, 0.7)',  // Delivered
                        'rgba(239, 68, 68, 0.7)'    // Cancelled
                    ],
                    borderWidth: 1,
                    borderColor: '#ffffff'
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: { position: 'bottom' }
                },
                scales: {
                    r: {
                        grid: { color: 'rgba(0,0,0,0.06)' },
                        ticks: { display: false }
                    }
                }
            }
        });
    }

    // 6. Top Selling Products Chart (Horizontal Bar)
    const topCtx = document.getElementById('chart-top-selling');
    if (topCtx) {
        new Chart(topCtx, {
            type: 'bar',
            data: {
                labels: data.top_selling_names || [],
                datasets: [{
                    data: data.top_selling_counts || [],
                    backgroundColor: '#14b8a6',
                    hoverBackgroundColor: '#0f766e',
                    borderRadius: 6
                }]
            },
            options: {
                indexAxis: 'y',
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: { display: false }
                },
                scales: {
                    x: {
                        beginAtZero: true,
                        grid: { color: 'rgba(0,0,0,0.05)' }
                    },
                    y: {
                        grid: { display: false }
                    }
                }
            }
        });
    }
}

/**
 * Handle Client-side search, filtering, and pagination for Recent Orders
 */
function initRecentOrdersTable() {
    const searchInput = document.getElementById('order-search-input');
    const filterSelect = document.getElementById('order-status-filter');
    const prevBtn = document.getElementById('btn-prev-page');
    const nextBtn = document.getElementById('btn-next-page');
    const infoText = document.getElementById('pagination-info-text');
    const tbody = document.getElementById('recent-orders-tbody');
    
    if (!tbody) return;
    const rows = Array.from(tbody.querySelectorAll('.order-row'));
    
    let filteredRows = [...rows];
    let currentPage = 1;
    const pageSize = 10;

    function applySearchAndFilter() {
        const query = searchInput.value.toLowerCase().trim();
        const statusVal = filterSelect.value;

        filteredRows = rows.filter(row => {
            const orderId = row.cells[0].textContent.toLowerCase();
            const customerName = row.querySelector('.customer-name-text').textContent.toLowerCase();
            const customerEmail = row.querySelector('.customer-email-text').textContent.toLowerCase();
            const matchesSearch = orderId.includes(query) || customerName.includes(query) || customerEmail.includes(query);

            const rowStatus = row.getAttribute('data-status');
            const matchesStatus = !statusVal || rowStatus === statusVal;

            return matchesSearch && matchesStatus;
        });

        currentPage = 1;
        renderTableRows();
    }

    function renderTableRows() {
        const totalCount = filteredRows.length;
        const totalPages = Math.ceil(totalCount / pageSize) || 1;

        if (currentPage > totalPages) currentPage = totalPages;
        if (currentPage < 1) currentPage = 1;

        const startIdx = (currentPage - 1) * pageSize;
        const endIdx = Math.min(startIdx + pageSize, totalCount);

        rows.forEach(row => {
            row.style.display = 'none';
        });

        filteredRows.slice(startIdx, endIdx).forEach(row => {
            row.style.display = '';
        });

        if (totalCount === 0) {
            infoText.textContent = 'Showing 0-0 of 0 orders';
        } else {
            infoText.textContent = `Showing ${startIdx + 1}-${endIdx} of ${totalCount} orders`;
        }

        prevBtn.disabled = currentPage === 1;
        nextBtn.disabled = currentPage === totalPages;
    }

    if (searchInput) searchInput.addEventListener('input', applySearchAndFilter);
    if (filterSelect) filterSelect.addEventListener('change', applySearchAndFilter);

    if (prevBtn) {
        prevBtn.addEventListener('click', function () {
            if (currentPage > 1) {
                currentPage--;
                renderTableRows();
            }
        });
    }

    if (nextBtn) {
        nextBtn.addEventListener('click', function () {
            const totalPages = Math.ceil(filteredRows.length / pageSize) || 1;
            if (currentPage < totalPages) {
                currentPage++;
                renderTableRows();
            }
        });
    }

    // Initial render call
    renderTableRows();
}

/**
 * Fetch and render dynamic AI Insights
 */
function loadAiInsights() {
    const grid = document.getElementById('ai-insights-grid');
    if (!grid) return;

    fetch('/seller/api/ai-insights/')
        .then(response => response.json())
        .then(data => {
            if (data.success && Array.isArray(data.insights)) {
                // Clear skeleton loading cards
                grid.innerHTML = '';
                
                data.insights.forEach((insight, index) => {
                    const card = document.createElement('div');
                    card.className = `insight-card type-${insight.type || 'info'}`;
                    card.style.opacity = '0';
                    card.style.transform = 'translateY(15px)';
                    card.style.transition = 'all 0.5s cubic-bezier(0.4, 0, 0.2, 1)';

                    card.innerHTML = `
                        <div class="insight-icon">${insight.icon || '💡'}</div>
                        <div class="insight-content">
                            <h4>${insight.title || 'Insight'}</h4>
                            <p>${insight.text || ''}</p>
                        </div>
                    `;

                    grid.appendChild(card);
                    
                    // Staggered entry animation
                    setTimeout(() => {
                        card.style.opacity = '1';
                        card.style.transform = 'translateY(0)';
                    }, index * 100);
                });
            } else {
                showAiErrorState(grid);
            }
        })
        .catch(err => {
            console.error('Error fetching AI Insights:', err);
            showAiErrorState(grid);
        });
}

function showAiErrorState(grid) {
    grid.innerHTML = `
        <div class="insight-card type-warning" style="grid-column: 1 / -1; display: flex; align-items: center; justify-content: center; padding: 24px; text-align: center;">
            <div class="insight-icon">⚠️</div>
            <div class="insight-content">
                <h4>AI Engine Offline</h4>
                <p>Failed to generate real-time AI Insights. Please try refreshing the dashboard.</p>
            </div>
        </div>
    `;
}

function initBusinessInsights() {
    const cards = document.querySelectorAll('.business-insight-card');
    cards.forEach(card => {
        card.addEventListener('mousemove', function(e) {
            const rect = card.getBoundingClientRect();
            const x = e.clientX - rect.left;
            const y = e.clientY - rect.top;

            const glow = card.querySelector('.card-glow');
            if (glow) {
                glow.style.background = `radial-gradient(circle at ${x}px ${y}px, rgba(255, 255, 255, 0.3) 0%, transparent 60%)`;
                glow.style.transform = 'translate(0, 0)';
            }
        });

        card.addEventListener('mouseleave', function() {
            const glow = card.querySelector('.card-glow');
            if (glow) {
                glow.style.background = 'radial-gradient(circle, rgba(255,255,255,0.15) 0%, transparent 60%)';
            }
        });
    });
}


