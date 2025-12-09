/**
 * DHT 溫濕度監測儀表板 - JavaScript
 * 生物機電工程概論 期末專題
 */

// ========== 設定 ==========
const CONFIG = {
    API_BASE: '',  // 相對路徑，同一伺服器
    UPDATE_INTERVAL: 5000,  // 數據更新間隔（毫秒）
    CHART_HOURS: 24,  // 預設圖表時間範圍
};

// ========== 全域變數 ==========
let historyChart = null;
let lastTemperature = null;
let lastHumidity = null;

// ========== DOM 元素 ==========
const elements = {
    // 狀態
    statusIndicator: document.getElementById('status-indicator'),
    statusText: document.getElementById('status-text'),
    lastUpdate: document.getElementById('last-update'),

    // 即時數據
    currentTemp: document.getElementById('current-temp'),
    currentHumidity: document.getElementById('current-humidity'),
    currentHeatIndex: document.getElementById('current-heat-index'),
    currentPpm: document.getElementById('current-ppm'),
    airQualityLevel: document.getElementById('air-quality-level'),

    // 趨勢
    tempTrend: document.getElementById('temp-trend'),
    humidityTrend: document.getElementById('humidity-trend'),
    comfortLevel: document.getElementById('comfort-level'),

    // 統計
    avgTemp: document.getElementById('avg-temp'),
    maxTemp: document.getElementById('max-temp'),
    minTemp: document.getElementById('min-temp'),
    avgHumidity: document.getElementById('avg-humidity'),
    maxHumidity: document.getElementById('max-humidity'),
    minHumidity: document.getElementById('min-humidity'),

    // 系統資訊
    totalReadings: document.getElementById('total-readings'),

    // 圖表
    chartCanvas: document.getElementById('history-chart'),
    rangeButtons: document.querySelectorAll('.range-btn'),
};

// ========== API 呼叫 ==========
async function fetchAPI(endpoint) {
    try {
        const response = await fetch(`${CONFIG.API_BASE}${endpoint}`);
        if (!response.ok) throw new Error(`HTTP ${response.status}`);
        return await response.json();
    } catch (error) {
        console.error(`API 錯誤 (${endpoint}):`, error);
        return null;
    }
}

// ========== 數據更新 ==========
async function updateCurrentData() {
    const result = await fetchAPI('/api/current');

    if (result && result.success) {
        const data = result.data;

        // 更新溫度
        if (data.temperature !== null) {
            const temp = parseFloat(data.temperature);
            elements.currentTemp.textContent = temp.toFixed(1);
            updateTrend(elements.tempTrend, temp, lastTemperature);
            lastTemperature = temp;
        }

        // 更新濕度
        if (data.humidity !== null) {
            const humidity = parseFloat(data.humidity);
            elements.currentHumidity.textContent = humidity.toFixed(1);
            updateTrend(elements.humidityTrend, humidity, lastHumidity);
            lastHumidity = humidity;
        }

        // 更新體感溫度
        if (data.heat_index !== null) {
            elements.currentHeatIndex.textContent = parseFloat(data.heat_index).toFixed(1);
        }

        // 更新 PPM 空氣品質
        if (data.air_quality !== null && data.air_quality !== undefined) {
            const ppm = parseFloat(data.air_quality);
            elements.currentPpm.textContent = ppm.toFixed(0);
            updateAirQualityLevel(ppm);
        }

        // 更新舒適度
        updateComfortLevel(data.temperature, data.humidity);

        // 更新狀態
        updateStatus('online', '連線中');

        // 更新時間
        updateLastUpdateTime();

    } else {
        updateStatus('offline', '離線');
    }
}

async function updateStats() {
    const result = await fetchAPI('/api/stats?hours=24');

    if (result && result.success && result.stats.count > 0) {
        const stats = result.stats;

        // 溫度統計
        elements.avgTemp.textContent = `${stats.temperature.avg}°C`;
        elements.maxTemp.textContent = `${stats.temperature.max}°C`;
        elements.minTemp.textContent = `${stats.temperature.min}°C`;

        // 濕度統計
        elements.avgHumidity.textContent = `${stats.humidity.avg}%`;
        elements.maxHumidity.textContent = `${stats.humidity.max}%`;
        elements.minHumidity.textContent = `${stats.humidity.min}%`;
    }
}

async function updateSystemInfo() {
    const result = await fetchAPI('/api/status');

    if (result && result.success) {
        elements.totalReadings.textContent = result.total_readings.toLocaleString();

        // 根據感測器狀態更新
        if (result.sensor_status === 'online') {
            updateStatus('online', '連線中');
        } else if (result.sensor_status === 'delayed') {
            updateStatus('delayed', '延遲');
        } else {
            updateStatus('offline', '離線');
        }
    }
}

async function updateChart(hours = CONFIG.CHART_HOURS) {
    const result = await fetchAPI(`/api/history?hours=${hours}`);

    if (result && result.success && result.data.length > 0) {
        renderChart(result.data);
    }
}

// ========== UI 更新函數 ==========
function updateStatus(status, text) {
    elements.statusIndicator.className = `status-indicator ${status}`;
    elements.statusText.textContent = text;
}

function updateLastUpdateTime() {
    const now = new Date();
    const timeStr = now.toLocaleTimeString('zh-TW', {
        hour: '2-digit',
        minute: '2-digit',
        second: '2-digit'
    });
    elements.lastUpdate.textContent = `最後更新: ${timeStr}`;
}

function updateTrend(element, current, previous) {
    if (previous === null) return;

    const diff = current - previous;
    const trendIcon = element.querySelector('.trend-icon');
    const trendText = element.querySelector('.trend-text');

    element.classList.remove('up', 'down', 'stable');

    if (diff > 0.5) {
        element.classList.add('up');
        trendIcon.textContent = '↑';
        trendText.textContent = `上升 ${diff.toFixed(1)}`;
    } else if (diff < -0.5) {
        element.classList.add('down');
        trendIcon.textContent = '↓';
        trendText.textContent = `下降 ${Math.abs(diff).toFixed(1)}`;
    } else {
        element.classList.add('stable');
        trendIcon.textContent = '→';
        trendText.textContent = '穩定';
    }
}

function updateComfortLevel(temperature, humidity) {
    let level = '';
    let emoji = '';

    const temp = parseFloat(temperature);
    const hum = parseFloat(humidity);

    if (temp >= 20 && temp <= 26 && hum >= 40 && hum <= 60) {
        level = '非常舒適';
        emoji = '😊';
    } else if (temp >= 18 && temp <= 28 && hum >= 30 && hum <= 70) {
        level = '舒適';
        emoji = '🙂';
    } else if (temp > 30 || hum > 80) {
        level = '悶熱';
        emoji = '🥵';
    } else if (temp < 15) {
        level = '寒冷';
        emoji = '🥶';
    } else if (hum < 30) {
        level = '乾燥';
        emoji = '🏜️';
    } else {
        level = '一般';
        emoji = '😐';
    }

    elements.comfortLevel.textContent = `舒適度: ${emoji} ${level}`;
}

function updateAirQualityLevel(ppm) {
    let level = '';
    let emoji = '';

    if (ppm <= 400) {
        level = '優良';
        emoji = '🌿';
    } else if (ppm <= 600) {
        level = '良好';
        emoji = '👍';
    } else if (ppm <= 1000) {
        level = '普通';
        emoji = '😐';
    } else if (ppm <= 2000) {
        level = '不良';
        emoji = '⚠️';
    } else {
        level = '危險';
        emoji = '🚨';
    }

    elements.airQualityLevel.textContent = `狀態: ${emoji} ${level}`;
}

// ========== 圖表 ==========
function renderChart(data) {
    // 準備數據
    const labels = data.map(d => new Date(d.timestamp));
    const temperatures = data.map(d => d.temperature);
    const humidities = data.map(d => d.humidity);
    const ppmData = data.map(d => d.air_quality);

    // 如果圖表已存在，銷毀它
    if (historyChart) {
        historyChart.destroy();
    }

    // 建立新圖表
    const ctx = elements.chartCanvas.getContext('2d');

    historyChart = new Chart(ctx, {
        type: 'line',
        data: {
            labels: labels,
            datasets: [
                {
                    label: '溫度 (°C)',
                    data: temperatures,
                    borderColor: '#ff6b6b',
                    backgroundColor: 'rgba(255, 107, 107, 0.1)',
                    fill: true,
                    tension: 0.4,
                    pointRadius: 2,
                    pointHoverRadius: 6,
                    yAxisID: 'y-temp',
                },
                {
                    label: '濕度 (%)',
                    data: humidities,
                    borderColor: '#4ecdc4',
                    backgroundColor: 'rgba(78, 205, 196, 0.1)',
                    fill: true,
                    tension: 0.4,
                    pointRadius: 2,
                    pointHoverRadius: 6,
                    yAxisID: 'y-humidity',
                },
                {
                    label: '空氣品質 (PPM)',
                    data: ppmData,
                    borderColor: '#9b59b6', /* ppm-color */
                    backgroundColor: 'rgba(155, 89, 182, 0.1)', /* ppm-glow */
                    fill: true,
                    tension: 0.4,
                    pointRadius: 2,
                    pointHoverRadius: 6,
                    yAxisID: 'y-ppm',
                }
            ]
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
                        color: '#a0a0c0',
                        font: {
                            family: "'Noto Sans TC', sans-serif",
                        },
                        usePointStyle: true,
                        padding: 20,
                    }
                },
                tooltip: {
                    backgroundColor: 'rgba(20, 20, 50, 0.9)',
                    titleColor: '#ffffff',
                    bodyColor: '#a0a0c0',
                    borderColor: 'rgba(255, 255, 255, 0.1)',
                    borderWidth: 1,
                    cornerRadius: 8,
                    padding: 12,
                    callbacks: {
                        label: function (context) {
                            let label = context.dataset.label || '';
                            if (label) {
                                label += ': ';
                            }
                            if (context.parsed.y !== null) {
                                if (context.dataset.yAxisID === 'y-ppm') {
                                    label += context.parsed.y.toFixed(0);
                                } else {
                                    label += context.parsed.y.toFixed(1);
                                }
                            }
                            return label;
                        },
                        title: function (tooltipItems) {
                            const date = new Date(tooltipItems[0].parsed.x);
                            return date.toLocaleString('zh-TW', {
                                month: 'short',
                                day: 'numeric',
                                hour: '2-digit',
                                minute: '2-digit'
                            });
                        }
                    }
                }
            },
            scales: {
                x: {
                    type: 'time',
                    time: {
                        unit: 'hour',
                        displayFormats: {
                            hour: 'HH:mm'
                        }
                    },
                    grid: {
                        color: 'rgba(255, 255, 255, 0.05)',
                    },
                    ticks: {
                        color: '#6060a0',
                        maxRotation: 0,
                    }
                },
                'y-temp': {
                    type: 'linear',
                    position: 'left',
                    title: {
                        display: true,
                        text: '溫度 (°C)',
                        color: '#ff6b6b',
                    },
                    grid: {
                        color: 'rgba(255, 107, 107, 0.1)',
                    },
                    ticks: {
                        color: '#ff6b6b',
                    }
                },
                'y-humidity': {
                    type: 'linear',
                    position: 'right',
                    title: {
                        display: true,
                        text: '濕度 (%)',
                        color: '#4ecdc4',
                    },
                    grid: {
                        drawOnChartArea: false,
                    },
                    ticks: {
                        color: '#4ecdc4',
                    },
                    min: 0,
                    max: 100,
                },
                'y-ppm': {
                    type: 'linear',
                    position: 'right',
                    title: {
                        display: true,
                        text: 'PPM',
                        color: '#9b59b6',
                    },
                    grid: {
                        drawOnChartArea: false,
                    },
                    ticks: {
                        color: '#9b59b6',
                    },
                    min: 0,
                    // max: 2000
                }
            }
        }
    });
}

// ========== 事件處理 ==========
function setupEventListeners() {
    // 時間範圍按鈕
    elements.rangeButtons.forEach(btn => {
        btn.addEventListener('click', () => {
            // 更新 active 狀態
            elements.rangeButtons.forEach(b => b.classList.remove('active'));
            btn.classList.add('active');

            // 更新圖表
            const hours = parseInt(btn.dataset.hours);
            CONFIG.CHART_HOURS = hours;
            updateChart(hours);
        });
    });

    // 暫時清空按鈕
    const softClearBtn = document.getElementById('btn-soft-clear');
    if (softClearBtn) {
        softClearBtn.addEventListener('click', handleSoftClear);
    }

    // 永久清空按鈕
    const hardClearBtn = document.getElementById('btn-hard-clear');
    if (hardClearBtn) {
        hardClearBtn.addEventListener('click', handleHardClear);
    }
}

// ========== 清空功能 ==========
async function handleSoftClear() {
    // 暫時清空 - 只重置前端顯示
    try {
        const response = await fetch('/api/clear/soft', { method: 'POST' });
        const result = await response.json();

        if (result.success) {
            // 重置前端顯示
            elements.currentTemp.textContent = '--.-';
            elements.currentHumidity.textContent = '--.-';
            elements.currentHeatIndex.textContent = '--.-';
            lastTemperature = null;
            lastHumidity = null;

            // 清空圖表
            if (historyChart) {
                historyChart.data.labels = [];
                historyChart.data.datasets.forEach(ds => ds.data = []);
                historyChart.update();
            }

            showNotification('✅ 顯示已重整', 'success');
        } else {
            showNotification('❌ 清空失敗', 'error');
        }
    } catch (error) {
        console.error('Soft clear error:', error);
        showNotification('❌ 連線錯誤', 'error');
    }
}

async function handleHardClear() {
    // 永久清空 - 需要確認
    const confirmed = confirm(
        '⚠️ 永久清空警告 ⚠️\n\n' +
        '這將永久刪除所有歷史數據！\n' +
        '此操作無法復原！\n\n' +
        '確定要繼續嗎？'
    );

    if (!confirmed) return;

    // 二次確認
    const doubleConfirm = confirm(
        '🔴 最後確認 🔴\n\n' +
        '真的要刪除所有數據嗎？'
    );

    if (!doubleConfirm) return;

    try {
        const response = await fetch('/api/clear/hard', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ confirm: true })
        });
        const result = await response.json();

        if (result.success) {
            // 重置所有顯示
            elements.currentTemp.textContent = '--.-';
            elements.currentHumidity.textContent = '--.-';
            elements.currentHeatIndex.textContent = '--.-';
            elements.totalReadings.textContent = '0';
            elements.avgTemp.textContent = '--.-°C';
            elements.maxTemp.textContent = '--.-°C';
            elements.minTemp.textContent = '--.-°C';
            elements.avgHumidity.textContent = '--.-%';
            elements.maxHumidity.textContent = '--.-%';
            elements.minHumidity.textContent = '--.-%';
            lastTemperature = null;
            lastHumidity = null;

            // 清空圖表
            if (historyChart) {
                historyChart.data.labels = [];
                historyChart.data.datasets.forEach(ds => ds.data = []);
                historyChart.update();
            }

            showNotification(`✅ 已刪除 ${result.deleted_count} 筆數據`, 'success');
        } else {
            showNotification('❌ 清空失敗: ' + result.error, 'error');
        }
    } catch (error) {
        console.error('Hard clear error:', error);
        showNotification('❌ 連線錯誤', 'error');
    }
}

function showNotification(message, type = 'info') {
    // 建立通知元素
    const notification = document.createElement('div');
    notification.className = `notification ${type}`;
    notification.textContent = message;

    // 加入頁面
    document.body.appendChild(notification);

    // 觸發動畫
    setTimeout(() => notification.classList.add('show'), 10);

    // 自動移除
    setTimeout(() => {
        notification.classList.remove('show');
        setTimeout(() => notification.remove(), 300);
    }, 3000);
}

// ========== 初始化 ==========
async function init() {
    console.log('🌡️ DHT 監測儀表板初始化中...');

    // 設定事件監聽
    setupEventListeners();

    // 初始數據載入
    await Promise.all([
        updateCurrentData(),
        updateStats(),
        updateSystemInfo(),
        updateChart(CONFIG.CHART_HOURS),
    ]);

    // 設定定期更新
    setInterval(updateCurrentData, CONFIG.UPDATE_INTERVAL);
    setInterval(updateStats, 60000);  // 每分鐘更新統計
    setInterval(() => updateChart(CONFIG.CHART_HOURS), 60000);  // 每分鐘更新圖表
    setInterval(updateSystemInfo, 30000);  // 每 30 秒更新系統資訊

    console.log('✅ 儀表板初始化完成！');
}

// 頁面載入完成後初始化
document.addEventListener('DOMContentLoaded', init);
