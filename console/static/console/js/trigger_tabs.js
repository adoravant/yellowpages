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