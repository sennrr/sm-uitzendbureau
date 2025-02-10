document.addEventListener("DOMContentLoaded", function() {
    console.log("Script geladen!");
    
    const sollicitatieFormulier = document.querySelector("form");
    if (sollicitatieFormulier) {
        sollicitatieFormulier.addEventListener("submit", function(event) {
            event.preventDefault();
            alert("Je sollicitatie is verstuurd!");
            this.submit();
        });
    }
});
