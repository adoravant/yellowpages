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