const btnCopiar = document.querySelector(".btn-copiar");
const textoParaCopiar = document.getElementById("textoParaCopiar");

btnCopiar.addEventListener("click", async () => {
    try {
        await navigator.clipboard.writeText(textoParaCopiar.value);
        alert("Texto copiado: " + textoParaCopiar.value);
    } catch (err) {
        console.error('Erro ao copiar texto: ', err);
    }
});
