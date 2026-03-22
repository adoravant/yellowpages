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