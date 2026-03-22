// --- CONFIGURACIÓN DE DATOS ---


const filterData = {
    chats: ['Waiting', 'Active', 'Closed'],
    files: ['Docs', 'Images', 'Contracts'],
    milestones: ['Discovery', 'Qualify', 'Offer'],
    intel: ['Tech', 'Business', 'Pain']
};

// --- MATRIX ACTION (STAGING) ---
function triggerMatrixAction(element, id, label) {
    const input = document.getElementById("msgInput");
    
    if (!input) {
        console.error("ERROR: No encuentro msgInput");
        return;
    }

    // Cargar texto (staging)
    input.value = label;

    // Sacar foco para permitir hotkeys
    input.blur();
    if (element) element.blur();

    console.log("Matrix loaded:", label);
}

// --- ENVÍO (COMMIT) ---
function sendMessage(){
    const input = document.getElementById("msgInput");
    if (!input) return;

    const text = input.value.trim();
    if(!text) return;

    addMsg("agent", text);

    input.value = "";
    input.blur();
}

// --- RENDER CHAT ---
function addMsg(type, text) {
    const chat = document.getElementById("chat");
    if (!chat) {
        console.error("No existe #chat");
        return;
    }

    const div = document.createElement("div");
    div.className = "msg " + type;
    div.innerText = text;

    chat.appendChild(div);
    chat.scrollTop = chat.scrollHeight;
}

// --- UI HELPERS ---
function switchPane(btn, pane){
    document.querySelectorAll(".tab-btn").forEach(b => b.classList.remove("active"));
    btn.classList.add("active");

    document.querySelectorAll(".pane-content").forEach(p => p.classList.add("d-none"));
    const target = document.querySelector(`[data-pane="${pane}"]`);
    if(target) target.classList.remove("d-none");

    const container = document.getElementById('filterContainer');
    if(container && filterData[pane]) {
        container.innerHTML = filterData[pane]
            .map(f => `<button class="btn-filter">${f}</button>`)
            .join('');
    }
}

function addNote(){
    const input = document.getElementById("noteInput");
    if(!input || !input.value.trim()) return;

    const list = document.getElementById("notes");
    const div = document.createElement("div");
    div.className = "note";

    const now = new Date();
    const time = `${now.getHours()}:${now.getMinutes().toString().padStart(2, '0')}`;
    
    div.innerHTML = `<b>${time}</b> - ${input.value}`;
    list.prepend(div);
    input.value = "";
}

function toggleDiag(el){
    el.classList.toggle("done");
}

// --- INIT ---
document.addEventListener("DOMContentLoaded", () => {
    const defaultTab = document.querySelector('.tab-btn');
    if(defaultTab) switchPane(defaultTab, 'chats');
});

// --- HOTKEY SYSTEM FINAL ---
// ================================
// HOTKEY SYSTEM (MATRIX + INPUT)
// ================================

window.addEventListener('keydown', function(e){
    const input = document.getElementById("msgInput");
    if (!input) return;

    const key = e.key;
    const active = document.activeElement;

    // ================================
    // KEY MAP (ESPEJO VISUAL)
    // ================================
    const keyMap = {
        '7': 'avance-0',
        '8': 'avance-1',
        '9': 'avance-2',

        '4': 'stall-0',
        '5': 'stall-1',
        '6': 'stall-2',

        '1': 'close-0',
        '2': 'close-1',
        '3': 'close-2',
    };

    // ================================
    // 1. NUMEROS → DISPARAR MATRIX
    // ================================
    if (keyMap[key] && active !== input) {
        e.preventDefault();

        const [group, index] = keyMap[key].split('-');

        const botones = document.querySelectorAll(`.btn-${group}`);
        const btn = botones[parseInt(index)];

        if (btn) {
            triggerMatrixAction(
                btn,
                btn.dataset.id || "",
                btn.dataset.label || btn.innerText.trim()
            );

            // feedback visual
            btn.style.outline = "2px solid white";
            setTimeout(() => btn.style.outline = "none", 150);
        }

        return;
    }

    // ================================
    // 2. KEY 0 → EDITAR ADELANTE
    // ================================
    if ((key === '0' || e.keyCode === 96) && active !== input) {
        e.preventDefault();

        input.value = input.value.trimStart();
        input.focus();
        input.setSelectionRange(0, 0);

        return;
    }

    //================================
    // 3. ENTER → EDITAR ATRÁS / ENVIAR
    // ================================
    if (key === 'Enter') {
        e.preventDefault();

        if (active === input) {
            // enviar
            if (input.value.trim() !== "") {
                sendMessage();
            }
        } else {
            // editar al final CON espacio garantizado
            let val = input.value.trimEnd();

            // agregamos espacio sí o sí
            val = val + " ";

            input.value = val;
            input.focus();

            const len = val.length;
            input.setSelectionRange(len, len); // cursor después del espacio
        }

        return;
    }

}, true);