// static/console/js/config.js

// --- UTILIDADES ---
let timeout;
function debounceSave() {
    clearTimeout(timeout);
    timeout = setTimeout(() => {
        saveConfig(true); // Guardado silencioso
    }, 800); 
}

// --- RENDER FILAS ---
function renderRows(category) {
    const body = document.getElementById('table-body');
    if (!body) return;

    const data = configData[category] || {};
    body.innerHTML = '';
    
    Object.keys(data).forEach(slug => {
        const row = data[slug];
        const iconName = row.icon || 'list-checks';
        body.innerHTML += `
            <tr class="event-row" data-slug="${slug}">
                <td>
                   
                    <span class="slug">${slug}</span>
                </td>
                <td><div class="toggle-btn js-alert ${row.alert ? 'active' : ''}"></div></td>
                <td><input type="number" class="input-num js-priority" value="${row.priority}"></td>
                <td><div class="toggle-btn js-auto ${row.auto ? 'active' : ''}"></div></td>
                <td><input type="text" class="input-text js-consumes" value="${row.consumes === null ? 'None' : row.consumes}"></td>
                <td><div class="toggle-btn js-active ${row.active ? 'active' : ''}"></div></td>
            </tr>
        `;
    });

    if (window.lucide) lucide.createIcons();
}

// --- MOSTRAR TAB ---
function showTab(cat) {
    document.querySelectorAll('.tab-link').forEach(l => l.classList.remove('active'));
    if (event && event.currentTarget) event.currentTarget.classList.add('active');

    const tabTitle = document.getElementById('tab-title');
    const currentTab = tabs.find(t => t.key === cat);
    if (tabTitle && currentTab) tabTitle.innerText = currentTab.name.toUpperCase();

    renderRows(cat);
}

// --- GUARDADO ---
async function saveConfig(silent = false) {
    const rows = document.querySelectorAll('.event-row');
    if (!rows.length) return;

    const payload = Array.from(rows).map(row => {
        const iconEl = row.querySelector('i[data-lucide]');
        return {
            slug: row.dataset.slug,
            should_alert: row.querySelector('.js-alert').classList.contains('active'),
            alert_priority: parseInt(row.querySelector('.js-priority').value) || 0,
            allowed_auto: row.querySelector('.js-auto').classList.contains('active'),
            max_consumes: row.querySelector('.js-consumes').value === 'None' ? null : parseInt(row.querySelector('.js-consumes').value),
            active: row.querySelector('.js-active').classList.contains('active'),
            icon: iconEl ? iconEl.getAttribute('data-lucide') : 'list-checks'
        };
    });

    try {
        const response = await fetch(saveUrl, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': csrfToken
            },
            body: JSON.stringify(payload)
        });

        if (response.ok && !silent) {
            alert("🎯 Engine DNA Updated Successfully");
            console.log("Auto-save ok");
        }
    } catch (err) {
        console.error("Error en auto-save:", err);
    }
}

// --- EVENTOS ---
document.addEventListener('DOMContentLoaded', () => {
    // Inicializamos la primera categoría que tenga eventos
    let initialCategory = Object.keys(configData).find(cat => Object.keys(configData[cat]).length > 0);

    // Fallback a cualquier tab si no hay datos
    if (!initialCategory && tabs.length > 0) {
        initialCategory = tabs[0].key;
    }

    // Render inicial y actualizar título de tab
    if (initialCategory) {
        renderRows(initialCategory);
        const tabTitle = document.getElementById('tab-title');
        const currentTab = tabs.find(t => t.key === initialCategory);
        if (tabTitle && currentTab) tabTitle.innerText = currentTab.name.toUpperCase();
    }

    // Delegación para toggles
    document.addEventListener('click', (e) => {
        if (e.target.classList.contains('toggle-btn')) {
            e.target.classList.toggle('active');
            saveConfig(true);
        }
    });

    // Delegación para inputs (guardado con debounce)
    const tbody = document.getElementById('table-body');
    if (tbody) {
        tbody.addEventListener('input', (e) => {
            if (e.target.classList.contains('input-num') || e.target.classList.contains('input-text')) {
                debounceSave();
            }
        });
    }
});

// --- TOGGLE COLUMN ---
function toggleColumn(className) {
    const buttons = document.querySelectorAll(`.${className}`);
    const anyInactive = Array.from(buttons).some(btn => !btn.classList.contains('active'));
    buttons.forEach(btn => anyInactive ? btn.classList.add('active') : btn.classList.remove('active'));
    saveConfig(true);
}