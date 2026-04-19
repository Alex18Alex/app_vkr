// Глобальные переменные
let currentDatasetId = null;

// Инициализация
document.addEventListener('DOMContentLoaded', function() {
    console.log('DOM loaded');
    loadDatasets();
    setupFileUpload();
});

// Загрузка списка датасетов
async function loadDatasets() {
    try {
        const response = await fetch('/api/datasets');
        const datasets = await response.json();
        const select = document.getElementById('datasetSelect');
        if (!select) return;

        select.innerHTML = '<option value="">Выберите датасет...</option>';
        datasets.forEach(dataset => {
            const option = document.createElement('option');
            option.value = dataset.id;
            option.textContent = `${dataset.name} (${new Date(dataset.upload_date).toLocaleDateString()})`;
            select.appendChild(option);
        });

        const urlParams = new URLSearchParams(window.location.search);
        const datasetId = urlParams.get('dataset_id');
        if (datasetId && datasets.length > 0) {
            select.value = datasetId;
            loadAnalyticsData(datasetId);
        } else if (datasets.length > 0) {
            select.value = datasets[0].id;
            loadAnalyticsData(datasets[0].id);
        }

        select.addEventListener('change', function() {
            if (this.value) {
                loadAnalyticsData(this.value);
            }
        });
    } catch (error) {
        console.error('Error loading datasets:', error);
    }
}

// Загрузка данных аналитики
async function loadAnalyticsData(datasetId) {
    if (currentDatasetId === datasetId) return;
    currentDatasetId = datasetId;

    console.log('Loading analytics for dataset:', datasetId);

    // Показываем индикаторы загрузки для всех графиков
    showLoadingIndicators();

    try {
        // Загружаем KPI и таблицу
        const response = await fetch(`/api/analytics/${datasetId}`);
        const data = await response.json();

        updateKPICards(data.kpi);
        updateDebtorsTable(data.charts.debtors_data);

        // Загружаем все графики через DataVisualizer
        await loadChart('/api/chart/dynamics', datasetId, 'dynamicsChart', 'dynamicsLoading');
        await loadChart('/api/chart/service-structure', datasetId, 'serviceChart', 'serviceLoading');
        await loadChart('/api/chart/aging', datasetId, 'agingChart', 'agingLoading');
        await loadChart('/api/chart/risk', datasetId, 'riskChart', 'riskLoading');

    } catch (error) {
        console.error('Error loading analytics:', error);
    }
}

// Показать индикаторы загрузки
function showLoadingIndicators() {
    const loadingElements = ['dynamicsLoading', 'serviceLoading', 'agingLoading', 'riskLoading'];
    const imgElements = ['dynamicsChart', 'serviceChart', 'agingChart', 'riskChart'];

    loadingElements.forEach(id => {
        const el = document.getElementById(id);
        if (el) el.style.display = 'block';
    });
    imgElements.forEach(id => {
        const el = document.getElementById(id);
        if (el) el.style.display = 'none';
    });
}

// Загрузка одного графика
async function loadChart(apiUrl, datasetId, imgId, loadingId) {
    const img = document.getElementById(imgId);
    if (!img) {
        // Элемента нет на этой странице, просто выходим
        console.log(`Element ${imgId} not found on this page, skipping`);
        return;
    }

    const loading = document.getElementById(loadingId);

    try {
        const response = await fetch(`${apiUrl}?dataset_id=${datasetId}`);
        const data = await response.json();

        if (data.image) {
            img.src = 'data:image/png;base64,' + data.image;
            img.style.display = 'block';
            if (loading) loading.style.display = 'none';
        } else if (data.error) {
            console.error(`Error in ${apiUrl}:`, data.error);
            if (loading) loading.innerHTML = `<span class="text-danger">Ошибка: ${data.error}</span>`;
        }
    } catch (error) {
        console.error(`Error loading ${imgId}:`, error);
        if (loading) loading.innerHTML = '<span class="text-danger">Ошибка загрузки</span>';
    }
}

// Обновление KPI карточек
function updateKPICards(kpi) {
    const totalDebt = document.getElementById('total-debt');
    const avgDebt = document.getElementById('avg-debt');
    const debtorsPct = document.getElementById('debtors-pct');
    const collectionRate = document.getElementById('collection-rate');

    if (totalDebt) totalDebt.textContent = formatCurrency(kpi.total_debt);
    if (avgDebt) avgDebt.textContent = formatCurrency(kpi.avg_debt_per_account);
    if (debtorsPct) debtorsPct.textContent = kpi.debtors_percentage + '%';
    if (collectionRate) collectionRate.textContent = kpi.collection_rate + '%';
}

// Обновление таблицы должников
function updateDebtorsTable(debtorsData) {
    const tbody = document.querySelector('#debtorsTable tbody');
    if (!tbody) return;
    tbody.innerHTML = '';

    if (!debtorsData || debtorsData.length === 0) {
        tbody.innerHTML = '<tr><td colspan="4" class="text-center">Нет данных о должниках</td></tr>';
        return;
    }

    debtorsData.forEach(debtor => {
        const row = tbody.insertRow();
        row.insertCell(0).textContent = debtor.account_id;
        row.insertCell(1).textContent = debtor.resident_name || '-';
        row.insertCell(2).textContent = debtor.address || '-';
        row.insertCell(3).innerHTML = `<span class="text-danger fw-bold">${formatCurrency(debtor.total_debt)}</span>`;
    });
}

// Форматирование валюты
function formatCurrency(amount) {
    return new Intl.NumberFormat('ru-RU', {
        style: 'currency',
        currency: 'RUB',
        minimumFractionDigits: 0
    }).format(amount);
}

// Обработка загрузки файлов (для страницы upload)
function setupFileUpload() {
    const fileInput = document.getElementById('fileInput');
    const uploadArea = document.getElementById('uploadArea');

    if (uploadArea) {
        uploadArea.addEventListener('click', () => fileInput.click());
        uploadArea.addEventListener('dragover', (e) => {
            e.preventDefault();
            uploadArea.classList.add('dragover');
        });
        uploadArea.addEventListener('dragleave', () => {
            uploadArea.classList.remove('dragover');
        });
        uploadArea.addEventListener('drop', (e) => {
            e.preventDefault();
            uploadArea.classList.remove('dragover');
            if (e.dataTransfer.files.length) {
                fileInput.files = e.dataTransfer.files;
                handleFileUpload();
            }
        });
    }

    if (fileInput) {
        fileInput.addEventListener('change', handleFileUpload);
    }
}

// Обработка загрузки файла
async function handleFileUpload() {
    const fileInput = document.getElementById('fileInput');
    const submitBtn = document.getElementById('submitBtn');
    const statusDiv = document.getElementById('uploadStatus');

    if (!fileInput || !fileInput.files.length) return;

    const formData = new FormData();
    formData.append('file', fileInput.files[0]);

    if (submitBtn) {
        submitBtn.disabled = true;
        submitBtn.textContent = 'Загрузка...';
    }
    if (statusDiv) {
        statusDiv.innerHTML = '<div class="alert alert-info">Загрузка файла...</div>';
    }

    try {
        const response = await fetch('/upload', {
            method: 'POST',
            body: formData
        });

        const result = await response.json();

        if (result.success) {
            if (statusDiv) {
                statusDiv.innerHTML = `<div class="alert alert-success">${result.message}</div>`;
            }
            setTimeout(() => {
                window.location.href = `/analytics?dataset_id=${result.dataset_id}`;
            }, 2000);
        } else {
            if (statusDiv) {
                statusDiv.innerHTML = `<div class="alert alert-danger">Ошибка: ${result.message || result.errors?.join(', ')}</div>`;
            }
        }
    } catch (error) {
        if (statusDiv) {
            statusDiv.innerHTML = `<div class="alert alert-danger">Ошибка сети: ${error.message}</div>`;
        }
    } finally {
        if (submitBtn) {
            submitBtn.disabled = false;
            submitBtn.textContent = 'Загрузить данные';
        }
    }
}