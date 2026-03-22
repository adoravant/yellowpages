document.addEventListener('DOMContentLoaded', function () {

    const matrix = document.getElementById('matrix');
    const label = document.getElementById('matrix-stage-label');

    const STAGES = ['VALIDATION', 'PAIN', 'CALL'];

    let currentStage = 'VALIDATION';

    // =========================
    // ICON MAP (podés ajustar)
    // =========================
    const STAGE_ICONS = {
        VALIDATION: 'search',
        PAIN: 'alert-triangle',
        CALL: 'phone'
    };

    // =========================
    // RENDER
    // =========================
    function render() {

        const data = window.MATRIX_DATA[currentStage];
        if (!data) return;

        label.innerText = currentStage;

        let html = '';

        function renderRow(type, buttons, rowIndex) {

            const stageForRow = STAGES[rowIndex];

            html += `
                <div 
                    class="header-cell-lateral stage-switch ${currentStage === stageForRow ? 'active' : ''}"
                    data-stage="${stageForRow}"
                >
                    <i data-lucide="${STAGE_ICONS[stageForRow]}"></i>
                </div>
            `;

            buttons.forEach(btn => {
                if (btn) {
                    html += `
                        <button 
                            class="matrix-slot action-btn btn-${type.toLowerCase()}"
                            data-id="${btn.id}"
                            data-label="${btn.label}"
                        >
                            <i data-lucide="${btn.icon}"></i>
                            <span>${btn.label}</span>
                        </button>
                    `;
                } else {
                    html += `<div class="matrix-slot empty-slot"></div>`;
                }
            });
        }

        renderRow('AVANCE', data.AVANCE, 0);
        renderRow('STALL', data.STALL, 1);
        renderRow('CLOSE', data.CLOSE, 2);

        matrix.innerHTML = html;

        lucide.createIcons();

        bindEvents();
    }

    // =========================
    // EVENTS
    // =========================
    function bindEvents() {

        // botones
        matrix.querySelectorAll('.matrix-slot.action-btn').forEach(el => {
            el.addEventListener('click', function () {
                triggerMatrixAction(
                    this,
                    this.dataset.id,
                    this.dataset.label
                );
            });
        });

        // 🔥 filtros en iconos laterales
        matrix.querySelectorAll('.stage-switch').forEach(el => {
            el.addEventListener('click', function () {
                currentStage = this.dataset.stage;
                render();
            });
        });
    }

    render();
});


// =========================
// ACTION
// =========================
function triggerMatrixAction(element, btnId, label) {

    const loader = element.querySelector('.loading-overlay');
    if(loader) loader.style.display = 'flex';

    element.style.pointerEvents = 'none';

    if(window.addMsg) addMsg('agent', `Ejecutando: ${label}`);

    fetch(`/engine/matrix-click/${window.LEAD_ID}/${btnId}/`, {
        method: 'POST',
        headers: { 
            'X-CSRFToken': window.CSRF_TOKEN,
            'Content-Type': 'application/json'
        }
    })
    .then(res => res.json())
    .then(data => {
        if(data.status === 'success') {
            location.reload(); 
        } else {
            if(loader) loader.style.display = 'none';
            element.style.pointerEvents = 'all';
            alert("Error: " + data.message);
        }
    })
    .catch(err => {
        if(loader) loader.style.display = 'none';
        element.style.pointerEvents = 'all';
        console.error(err);
    });
}

// =========================
// ACTION
// =========================
function triggerMatrixAction(element, btnId, label) {

    const loader = element.querySelector('.loading-overlay');
    if(loader) loader.style.display = 'flex';

    element.style.pointerEvents = 'none';

    if(window.addMsg) addMsg('agent', `Ejecutando: ${label}`);

    fetch(`/engine/matrix-click/${window.LEAD_ID}/${btnId}/`, {
        method: 'POST',
        headers: { 
            'X-CSRFToken': window.CSRF_TOKEN,
            'Content-Type': 'application/json'
        }
    })
    .then(res => res.json())
    .then(data => {
        if(data.status === 'success') {
            location.reload(); 
        } else {
            if(loader) loader.style.display = 'none';
            element.style.pointerEvents = 'all';
            alert("Error: " + data.message);
        }
    })
    .catch(err => {
        if(loader) loader.style.display = 'none';
        element.style.pointerEvents = 'all';
        console.error(err);
    });
}