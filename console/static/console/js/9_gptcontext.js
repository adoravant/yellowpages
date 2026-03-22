/* --- builder.js --- */

/* -----------------------------
   TYPE LABELS
----------------------------- */
const TYPE_LABELS = {
    number: "int",
    text: "str",
    logic: "bool",
    list: "list",
    queryset: "qs",
    unknown: "?"
};

/* -----------------------------
   RESOLVER DOT NOTATION
----------------------------- */
function resolveVariableType(path) {
    if (!path) return null;
    const parts = path.split(".");
    let current = window.VARIABLE_SCHEMA;
    for (let p of parts) {
        if (!current || typeof current !== "object") return null;
        current = current[p];
    }
    return typeof current === "string" ? current : null;
}

/* -----------------------------
   CREATE RULE ROW
----------------------------- */
function createRuleRow() {
    const div = document.createElement("div");
    div.className = "logic-row";

    div.innerHTML = `
        <div style="position:relative">
            <input class="variable-input" placeholder="lead.email">
            <div class="suggestions" style="display:none"></div>
        </div>
        <input class="type-display" placeholder="type" disabled style="width:40px; opacity:0.6;">
        <select class="op-selector"></select>
        <div class="value-container">
            <input class="val-input" placeholder="value">
        </div>
        <button type="button" class="rule-del">✕</button>
    `;

    const varInput = div.querySelector(".variable-input");
    const suggestionBox = div.querySelector(".suggestions");
    const opSel = div.querySelector(".op-selector");
    const valContainer = div.querySelector(".value-container");
    const typeDisplay = div.querySelector(".type-display");
    const delBtn = div.querySelector(".rule-del");

    /* -----------------------------
       UPDATE OPERATORS
    ----------------------------- */
    const updateOps = () => {
        let type = resolveVariableType(varInput.value.trim());
        if (!type) {
            const base = varInput.value.split(".")[0];
            type = window.VARIABLE_TYPES?.[base];
        }

        typeDisplay.value = TYPE_LABELS[type] || type || "?";

        const ops = (window.OPERATOR_CATEGORIES || {})[type] || [];
        opSel.innerHTML = "";
        ops.forEach(o => {
            const opt = document.createElement("option");
            if (typeof o === "string") {
                opt.value = o;
                opt.innerText = o;
            } else {
                opt.value = o.v;
                opt.innerText = o.t;
            }
            opSel.appendChild(opt);
        });

        if (type === "logic") {
            valContainer.innerHTML = `
                <select class="val-input">
                    <option value="true">TRUE</option>
                    <option value="false">FALSE</option>
                </select>
            `;
        } else {
            valContainer.innerHTML = `<input class="val-input" placeholder="value">`;
        }

        const valInput = valContainer.querySelector(".val-input");
        valInput.addEventListener("input", updateLogicString);
        valInput.addEventListener("change", updateLogicString);

        valInput.addEventListener("keydown", e => {
            if (e.key === "Enter" || e.key === "Tab") {
                e.preventDefault();
                const addRuleBtn = div.closest(".logic-group").querySelector("button[onclick^='addRule']");
                if (addRuleBtn) addRuleBtn.focus();
            }
        });

        updateLogicString();
    };

    /* -----------------------------
       AUTOCOMPLETE
    ----------------------------- */
    let selectedIndex = -1;

    const renderSuggestions = () => {
        const items = Array.from(suggestionBox.children);
        items.forEach((it, i) => it.classList.toggle("selected", i === selectedIndex));
        if (selectedIndex >= 0 && items[selectedIndex]) {
            items[selectedIndex].scrollIntoView({ block: "nearest" });
        }
    };

    const updateSuggestions = () => {
        const q = varInput.value.trim();
        suggestionBox.innerHTML = "";
        selectedIndex = -1;
        if (!q) {
            suggestionBox.style.display = "none";
            return;
        }

        const matches = (window.VARIABLES || [])
            .filter(v => v.toLowerCase().includes(q.toLowerCase()));
        matches.forEach(m => {
            const d = document.createElement("div");
            d.className = "suggestion";
            d.innerText = m;
            d.onclick = () => {
                varInput.value = m;
                suggestionBox.style.display = "none";
                updateOps();
            };
            suggestionBox.appendChild(d);
        });

        const parts = q.split(".");
        let current = window.VARIABLE_SCHEMA;
        for (let i = 0; i < parts.length - 1; i++) current = current?.[parts[i]];

        if (current && typeof current === "object") {
            const last = parts[parts.length - 1].toLowerCase();
            Object.keys(current).forEach(key => {
                if (key.toLowerCase().includes(last)) {
                    const suggestion = document.createElement("div");
                    suggestion.className = "suggestion";
                    suggestion.innerText = [...parts.slice(0, -1), key].join(".");
                    suggestion.onclick = () => {
                        varInput.value = suggestion.innerText;
                        suggestionBox.style.display = "none";
                        updateOps();
                    };
                    suggestionBox.appendChild(suggestion);
                }
            });
        }

        const firstSelectable = Array.from(suggestionBox.children)
            .findIndex(el => !el.innerText.toLowerCase().endsWith(".id"));
        selectedIndex = firstSelectable >= 0 ? firstSelectable : -1;
        renderSuggestions();

        suggestionBox.style.display = suggestionBox.children.length ? "block" : "none";
    };

    varInput.addEventListener("input", updateSuggestions);

    varInput.addEventListener("keydown", e => {
        const items = Array.from(suggestionBox.children);
        if (!items.length) return;

        if (e.key === "ArrowDown") {
            e.preventDefault();
            selectedIndex = selectedIndex < items.length - 1 ? selectedIndex + 1 : 0;
            renderSuggestions();
        } else if (e.key === "ArrowUp") {
            e.preventDefault();
            selectedIndex = selectedIndex > 0 ? selectedIndex - 1 : items.length - 1;
            renderSuggestions();
        } else if (e.key === "Enter" || e.key === "Tab") {
            e.preventDefault();
            if (selectedIndex >= 0 && items[selectedIndex]) {
                varInput.value = items[selectedIndex].innerText;
                suggestionBox.style.display = "none";
                selectedIndex = -1;
                updateOps();
            }
            opSel.focus();
        }
    });

    opSel.addEventListener("keydown", e => {
        if (e.key === "Enter" || e.key === "Tab") {
            e.preventDefault();
            const valInput = valContainer.querySelector(".val-input");
            if (valInput) valInput.focus();
        }
    });

    opSel.addEventListener("change", updateLogicString);
    delBtn.addEventListener("click", () => {
        div.remove();
        updateLogicString();
    });

    return div;
}

/* -----------------------------
   CREATE GROUP
----------------------------- */
function createGroup(isRoot=false){
    const group = document.createElement("div");
    group.className = "logic-group";

    group.innerHTML = `
        <div class="group-header">
            <select class="group-op">
                <option value="AND">ALL</option>
                <option value="OR">ANY</option>
            </select>
            ${!isRoot ? `<button onclick="this.closest('.logic-group').remove();updateLogicString()">✕</button>` : ""}
        </div>

        <div class="nodes"></div>

        <div style="margin-top:5px">
            <button class="add-rule-btn" onclick="addRule(this)">+ Rule</button>
            <button class="add-group-btn">+ Group</button>
        </div>
    `;

    group.querySelector(".group-op").addEventListener("change", updateLogicString);

    const addGroupBtn = group.querySelector(".add-group-btn");
    addGroupBtn.addEventListener("click", () => {
        const nodes = group.querySelector(".nodes");
        const newGroup = createGroup();
        nodes.appendChild(newGroup);
        updateLogicString();

        const newAddRule = newGroup.querySelector("button[onclick^='addRule']");
        if (newAddRule) newAddRule.click();
    });

    return group;
}

/* -----------------------------
   ACTIONS
----------------------------- */
window.addRule = function(btn){
    const group = btn.closest(".logic-group");
    const nodes = group.querySelector(".nodes");
    const newRule = createRuleRow();
    nodes.appendChild(newRule);
    updateLogicString();
    newRule.querySelector(".variable-input").focus();
};

window.addGroup = function(btn){
    const nodes = btn.closest(".logic-group").querySelector(".nodes");
    const newGroup = createGroup();
    nodes.appendChild(newGroup);
    updateLogicString();
};

/* -----------------------------
   PARSE GROUP TO JSON
----------------------------- */
function parseGroup(node){
    const op = node.querySelector(".group-op").value;
    const children = Array.from(node.querySelector(".nodes").children);
    const nodes = [];
    children.forEach(c=>{
        if(c.classList.contains("logic-row")){
            const variable = c.querySelector(".variable-input").value.trim();
            const operator = c.querySelector(".op-selector").value;
            const value = c.querySelector(".val-input").value;
            if(!variable || !operator) return;
            nodes.push({variable, operator, value});
        } else if(c.classList.contains("logic-group")){
            const sub = parseGroup(c);
            if(sub.nodes.length > 0) nodes.push(sub);
        }
    });
    return {group: op, nodes};
}

/* -----------------------------
   RESET BUILDER
----------------------------- */
window.resetBuilder = () => {
    const canvas = document.getElementById("builder-canvas");
    if (!canvas) return;
    canvas.innerHTML = "";
    canvas.appendChild(createGroup(true));

    const jsonView = document.getElementById("json-output");
    if (jsonView) jsonView.innerText = JSON.stringify({ group: "AND", nodes: [] }, null, 2);

    setTimeout(updateLogicString, 50);
};



document.addEventListener("DOMContentLoaded", async () => {

    // 1️⃣ Inicializa builder
    if (window.resetBuilder) await resetBuilder(); // <-- esperar si es async

    // 2️⃣ Inicializa tabs
    const tabBtns = document.querySelectorAll(".tab-btn");
    tabBtns.forEach(btn => {
        btn.addEventListener("click", (e) => {
            const tabName = btn.getAttribute("data-tab");
            if (window.openTab) openTab(e, tabName);
        });
    });

    // Abrimos la primera tab por defecto
    if (window.openTab) openTab(null, 'tab-when');

    // 3️⃣ Inicializa botón copiar JSON
    const copyBtn = document.getElementById("copy-json-btn");
    if(copyBtn){
        copyBtn.addEventListener("click", ()=>{
            const json = getCurrentBuilderJson(); // JSON generado desde el builder

            const errors = validateJsonGroups(json);
            if(errors.length){
                showJsonAlert(errors.join(" | "), 5000);
                return;
            }

            const cleanedJson = cleanJsonGroup(json);

            navigator.clipboard.writeText(JSON.stringify(cleanedJson, null, 2))
                .then(()=> showJsonAlert("JSON copiado al portapapeles!", 2000))
                .catch(()=> showJsonAlert("Error al copiar JSON", 2000));
        });
    }

    // 4️⃣ Actualiza lógica inicial del builder
    // Ejecutar solo después de que el builder esté listo
    if (window.updateLogicString) setTimeout(updateLogicString, 50);

});

/* --- trigger_mermaids.js --- */

const VALID_GROUP_OPERATORS = ["AND","OR"];

/* -----------------------------
   ALERTA TIPO DJANGO
----------------------------- */
function showJsonAlert(msg, duration=4000){
    let alertEl = document.querySelector(".json-alert");
    if(!alertEl){
        alertEl = document.createElement("div");
        alertEl.className = "json-alert";
        document.body.appendChild(alertEl);
    }
    alertEl.textContent = msg;
    alertEl.classList.add("show");
    setTimeout(()=>alertEl.classList.remove("show"), duration);
}

/* -----------------------------
   LIMPIAR & VALIDAR JSON
----------------------------- */
function validateJsonGroups(data){
    const errors = [];
    const traverse = (node, path="root")=>{
        if(node.group && !VALID_GROUP_OPERATORS.includes(node.group)){
            errors.push(`Grupo inválido en "${path}": "${node.group}"`);
        }
        if(node.nodes) node.nodes.forEach((n,i)=>traverse(n, `${path}.nodes[${i}]`));
    };
    traverse(data);
    return errors;
}

function cleanJsonGroup(data){
    if(!data || !data.nodes) return { group:"AND", nodes:[] };
    const groupOp = VALID_GROUP_OPERATORS.includes(data.group) ? data.group : "AND";

    const cleanedNodes = data.nodes
        .map(n=>{
            if(n.group){
                const subClean = cleanJsonGroup(n);
                return subClean.nodes.length > 0 ? subClean : null;
            } else return n;
        })
        .filter(Boolean);

    return { group: groupOp, nodes: cleanedNodes };
}

/* -----------------------------
   MERMAID
----------------------------- */
let nodeCount=0;
function cleanText(txt){
    if(!txt||txt==='...') return "empty";
    return txt.toString().replace(/[\[\]\(\)\{\}\-\>\|\"\'\:]/g,"").trim();
}

function generateMermaid(data){
    let code="";
    const currentId=`G${nodeCount++}`;
    const label=data.group||"AND";
    const className=label==="OR"?":::orNode":":::andNode";
    const shape=label==="OR"?`{{${label}}}`:`{${label}}`;
    code+=`${currentId}${shape}${className}\n`;

    if(data.nodes){
        data.nodes.forEach(child=>{
            if(child.group){
                const {subCode,subRootId}=generateMermaid(child);
                code+=subCode;
                code+=`${currentId} --- ${subRootId}\n`;
            } else {
                const leafId=`L${nodeCount++}`;
                const v=cleanText(child.variable);
                const o=cleanText(child.operator);
                const val=cleanText(child.value);
                const ruleText=`("<font color='#3b82f6'><b>${v}</b></font><br/><font color='#f59e0b'>${o}</font><br/><font color='#22c55e'><b>${val}</b></font>")`;
                code+=`${leafId}${ruleText}\n${currentId} --- ${leafId}\n`;
            }
        });
    }

    return { subCode: code, subRootId: currentId };
}

window.renderVisualDNA = async function(json){
    const container = document.getElementById("mermaid-chart");
    if(!container || !json) return;
    if(!window.mermaid){ console.warn("Mermaid no disponible"); return; }

    nodeCount = 0;
    const { subCode } = generateMermaid(json);

    let fullChart = `graph TD\n${subCode}`;
    fullChart += `
        classDef andNode fill:#1e293b,stroke:#3b82f6,stroke-width:2px,color:#fff;
        classDef orNode fill:#451a03,stroke:#f97316,stroke-width:2px,color:#fff;
        classDef default fill:#0f172a,stroke:#1e293b,color:#f1f5f9;
    `;

    try {
        container.innerHTML="";
        const el = document.createElement("div");
        el.className="mermaid";
        el.textContent = fullChart;
        container.appendChild(el);
        await mermaid.run({ nodes:[el] });
    } catch(err){
        console.error("Mermaid error:", err);
    }
};

/* -----------------------------
   APPLY JSON
----------------------------- */
window.applyJsonDNA = function(){
    const jsonView = document.getElementById("json-output");
    try {
        let json = JSON.parse(jsonView.innerText);

        // validar primero
        const errors = validateJsonGroups(json);
        if(errors.length){
            showJsonAlert(errors.join(" | "), 5000);
        }

        // limpiar grupos vacíos
        json = cleanJsonGroup(json);

        // render
        renderVisualDNA(json);

    } catch(err){
        showJsonAlert("JSON inválido",5000);
        console.error(err);
    }
};

/* -----------------------------
   COPY JSON EXISTENTE (FIX)
----------------------------- */
document.addEventListener("DOMContentLoaded", ()=>{
    const copyBtn = document.getElementById("copy-json-btn");
    if(copyBtn){
        copyBtn.addEventListener("click", ()=>{
            const jsonView = document.getElementById("json-output");
            if(!jsonView) return;

            let json;
            try {
                json = JSON.parse(jsonView.innerText);
            } catch(e){
                showJsonAlert("JSON inválido",2000);
                return;
            }

            // Validar grupos primero
            const errors = validateJsonGroups(json);
            if(errors.length){
                showJsonAlert(errors.join(" | "),5000);
                return; // <-- Aquí se detiene la copia
            }

            // Si pasó la validación, copiar
            navigator.clipboard.writeText(JSON.stringify(json, null, 2))
                .then(()=>showJsonAlert("JSON copiado al portapapeles!",2000))
                .catch(()=>showJsonAlert("Error al copiar JSON",2000));
        });
    }
});

/* -----------------------------
   UPDATE LOGIC STRING
----------------------------- */
function updateLogicString(){
    const root = document.querySelector(".logic-group");
    if(!root) return;

    const json = parseGroup(root);
    const jsonView = document.getElementById("json-output");
    if(jsonView) jsonView.innerText = JSON.stringify(json,null,2);

    const logicView = document.getElementById("logic-output");
    if(logicView){
        const stringify = data=>{
            if(!data || !data.nodes || data.nodes.length===0) return "TRUE";
            const parts = data.nodes.map(n=>{
                if(n.group) return `(${stringify(n)})`;
                const val = n.value?.includes(' ') ? `"${n.value}"` : n.value;
                return `${n.variable} ${n.operator} ${val}`;
            });
            return parts.join(` ${data.group} `);
        };
        logicView.innerText = stringify(json);
    }

    if(window.renderVisualDNA) renderVisualDNA(json);
    return json;
};

/* -----------------------------
   INIT
----------------------------- */
document.addEventListener("DOMContentLoaded", ()=>{
    updateLogicString();
});



/* --- tabs.js --- */

/* -----------------------------
   SISTEMA DE TABS
----------------------------- */
window.openTab = function(evt, tabName) {
    const tabContents = document.getElementsByClassName("tab-content");
    for (let i = 0; i < tabContents.length; i++) { 
        tabContents[i].classList.remove("active"); 
        tabContents[i].style.display = "none"; 
    }
    const tabBtns = document.getElementsByClassName("tab-btn");
    for (let i = 0; i < tabBtns.length; i++) { tabBtns[i].classList.remove("active"); }

    const targetTab = document.getElementById(tabName);
    if(targetTab){
        targetTab.classList.add("active");
        targetTab.style.display = "block";
    }

    if (evt) evt.currentTarget.classList.add("active");
};
