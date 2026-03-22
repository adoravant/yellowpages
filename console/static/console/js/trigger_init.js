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