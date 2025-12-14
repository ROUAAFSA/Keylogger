let serverRunning = false;
let autoRefresh = true;
let startTime = null;
let uptimeInterval = null;
let logRefreshInterval = null;

// Toggle server on/off
async function toggleServer() {
    if (serverRunning) {
        await stopServer();
    } else {
        await startServer();
    }
}

// Start server
async function startServer() {
    if (serverRunning) return;

    try {
        const response = await fetch('/api/start', { method: 'POST' });
        const data = await response.json();

        if (data.success) {
            serverRunning = true;
            startTime = Date.now();

            updateServerUI(true);
            document.getElementById('session-id').textContent = data.session_id;

            updateUptime();
            uptimeInterval = setInterval(updateUptime, 1000);

            if (autoRefresh) {
                logRefreshInterval = setInterval(loadLogs, 2000);
            }

            loadLogs();
            console.log('✓ Server started');
        }
    } catch (error) {
        console.error('Error:', error);
        alert('Failed to start server: ' + error.message);
    }
}

// Stop server
async function stopServer() {
    if (!serverRunning) return;

    try {
        const response = await fetch('/api/stop', { method: 'POST' });
        const data = await response.json();

        if (data.success) {
            serverRunning = false;
            startTime = null;

            updateServerUI(false);

            if (uptimeInterval) clearInterval(uptimeInterval);
            if (logRefreshInterval) clearInterval(logRefreshInterval);

            console.log('✓ Server stopped');
        }
    } catch (error) {
        console.error('Error:', error);
        alert('Failed to stop server: ' + error.message);
    }
}

// Update server UI
function updateServerUI(running) {
    const toggle = document.getElementById('server-toggle');
    const toggleInner = toggle.querySelector('div');
    const statusBadge = document.getElementById('server-status-badge');
    const stateText = document.getElementById('server-state-text');
    const systemStatus = document.getElementById('system-status');
    const btnStart = document.getElementById('btn-start');
    const btnStop = document.getElementById('btn-stop');

    if (running) {
        toggle.className = 'relative w-14 h-8 rounded-full transition-colors cursor-pointer bg-teal-500';
        toggleInner.className = 'absolute top-1 w-6 h-6 bg-white rounded-full shadow-md transition-transform translate-x-7';
        statusBadge.className = 'px-3 py-1 rounded-full text-xs font-semibold whitespace-nowrap bg-green-100 text-green-700';
        statusBadge.textContent = 'Online';
        stateText.textContent = 'Running';
        systemStatus.innerHTML = '<div class="w-2 h-2 bg-green-500 rounded-full animate-pulse"></div><span class="text-sm font-medium text-green-700">Server Online</span>';

        btnStart.disabled = true;
        btnStart.className = 'flex-1 px-6 py-3 bg-slate-200 text-slate-400 font-semibold rounded-lg cursor-not-allowed whitespace-nowrap';

        btnStop.disabled = false;
        btnStop.className = 'flex-1 px-6 py-3 bg-red-500 text-white font-semibold rounded-lg hover:bg-red-600 transition-colors cursor-pointer whitespace-nowrap';
    } else {
        toggle.className = 'relative w-14 h-8 rounded-full transition-colors cursor-pointer bg-slate-300';
        toggleInner.className = 'absolute top-1 w-6 h-6 bg-white rounded-full shadow-md transition-transform translate-x-1';
        statusBadge.className = 'px-3 py-1 rounded-full text-xs font-semibold whitespace-nowrap bg-red-100 text-red-700';
        statusBadge.textContent = 'Offline';
        stateText.textContent = 'Stopped';
        systemStatus.innerHTML = '<div class="w-2 h-2 bg-red-500 rounded-full"></div><span class="text-sm font-medium text-red-700">Server Offline</span>';

        btnStart.disabled = false;
        btnStart.className = 'flex-1 px-6 py-3 bg-teal-500 text-white font-semibold rounded-lg hover:bg-teal-600 transition-colors cursor-pointer whitespace-nowrap';

        btnStop.disabled = true;
        btnStop.className = 'flex-1 px-6 py-3 bg-slate-200 text-slate-400 font-semibold rounded-lg cursor-not-allowed whitespace-nowrap';
    }
}

// Toggle auto refresh
function toggleAutoRefresh() {
    autoRefresh = !autoRefresh;
    const toggle = document.getElementById('refresh-toggle');
    const toggleInner = toggle.querySelector('div');

    if (autoRefresh) {
        toggle.className = 'relative w-14 h-8 rounded-full transition-colors cursor-pointer bg-teal-500';
        toggleInner.className = 'absolute top-1 w-6 h-6 bg-white rounded-full shadow-md transition-transform translate-x-7';

        if (serverRunning && !logRefreshInterval) {
            logRefreshInterval = setInterval(loadLogs, 2000);
        }
    } else {
        toggle.className = 'relative w-14 h-8 rounded-full transition-colors cursor-pointer bg-slate-300';
        toggleInner.className = 'absolute top-1 w-6 h-6 bg-white rounded-full shadow-md transition-transform translate-x-1';

        if (logRefreshInterval) {
            clearInterval(logRefreshInterval);
            logRefreshInterval = null;
        }
    }
}

// Update uptime
function updateUptime() {
    if (!startTime) return;

    const elapsed = Math.floor((Date.now() - startTime) / 1000);
    const hours = Math.floor(elapsed / 3600);
    const minutes = Math.floor((elapsed % 3600) / 60);
    const seconds = elapsed % 60;

    document.getElementById('uptime').textContent =
        `${String(hours).padStart(2, '0')}:${String(minutes).padStart(2, '0')}:${String(seconds).padStart(2, '0')}`;
}

// Load logs
async function loadLogs() {
    try {
        const response = await fetch('/api/logs');
        const data = await response.json();

        const container = document.getElementById('logs-container');
        const emptyState = document.getElementById('empty-state');

        if (data.logs && data.logs.length > 0) {
            if (emptyState) emptyState.style.display = 'none';

            container.innerHTML = '';

            data.logs.forEach(log => {
                const div = document.createElement('div');

                if (log.includes('===')) {
                    div.className = 'flex items-start gap-3 p-3 rounded-lg border bg-blue-50 border-blue-200 text-blue-700';
                    div.innerHTML = `
                        <i class="ri-information-line text-lg mt-0.5"></i>
                        <div class="flex-1 min-w-0">
                            <p class="text-sm font-medium">${escapeHtml(log)}</p>
                        </div>`;
                } else {
                    div.className = 'flex items-start gap-3 p-3 rounded-lg border bg-slate-50 border-slate-200 text-slate-700';
                    div.innerHTML = `
                        <i class="ri-file-text-line text-lg mt-0.5"></i>
                        <div class="flex-1 min-w-0">
                            <p class="text-sm font-mono">${escapeHtml(log)}</p>
                        </div>`;
                }

                container.appendChild(div);
            });

            container.scrollTop = container.scrollHeight;
            document.getElementById('log-count').textContent = data.logs.length;
            document.getElementById('total-logs').textContent = data.logs.length;
        } else {
            if (emptyState) emptyState.style.display = 'flex';
        }
    } catch (error) {
        console.error('Error loading logs:', error);
    }
}

// Escape HTML
function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

// Refresh logs manually
function refreshLogs() {
    loadLogs();
    console.log('✓ Logs refreshed');
}

// Export logs
async function exportLogs() {
    try {
        const response = await fetch('/api/export');
        const blob = await response.blob();

        const url = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `logs_export_${new Date().toISOString().replace(/:/g, '-').split('.')[0]}.txt`;
        document.body.appendChild(a);
        a.click();
        document.body.removeChild(a);
        window.URL.revokeObjectURL(url);

        console.log('✓ Logs exported');
    } catch (error) {
        console.error('Error:', error);
        alert('Failed to export logs');
    }
}

// Delete logs
async function deleteLogs() {
    if (!confirm('Are you sure you want to delete all logs?\n\nThis action cannot be undone!')) {
        return;
    }

    try {
        const response = await fetch('/api/delete', { method: 'POST' });
        const data = await response.json();

        if (data.success) {
            loadLogs();
            console.log('✓ Logs deleted');
        }
    } catch (error) {
        console.error('Error:', error);
        alert('Failed to delete logs');
    }
}

// Clear display
function clearDisplay() {
    const container = document.getElementById('logs-container');
    container.innerHTML = `
        <div class="flex flex-col items-center justify-center h-full text-slate-400" id="empty-state">
            <i class="ri-file-list-line text-6xl mb-4"></i>
            <p class="text-lg font-medium">No logs received yet</p>
            <p class="text-sm mt-2">Start the server and logs will appear here</p>
        </div>`;
    document.getElementById('log-count').textContent = '0';
}

// Open settings
function openSettings() {
    const newInterval = prompt('Enter new send interval (seconds):', '60');
    if (newInterval && !isNaN(newInterval) && newInterval >= 5) {
        fetch('/api/settings', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ send_interval: parseInt(newInterval) })
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                alert(`✓ Send interval updated to ${newInterval} seconds`);
            }
        });
    }
}

// Initial load
window.addEventListener('load', () => {
    loadLogs();
});
