document.getElementById("download-button").onclick = function() {
    const chatBox = document.getElementById("chat-box");
    const recommendationsList = document.getElementById("recommendations-list");

    if (!chatBox || chatBox.children.length === 0) {
        alert("No hay conversaciones disponibles para descargar.");
        return;
    }

    // Obtener el texto de la conversación
    const conversationText = Array.from(chatBox.children)
        .map(child => child.textContent.trim())
        .join("\n\n");

    // Obtener el texto de las recomendaciones
    const recommendationsText = Array.from(recommendationsList.children)
        .map(child => {
            if (child.querySelector('a')) {
                // Si es un enlace, obtener el texto y la URL
                const link = child.querySelector('a');
                return `${link.textContent}: ${link.href}`;
            } else {
                // Si no es un enlace, obtener el texto normal
                return child.textContent.trim();
            }
        })
        .join("\n\n");

    // Combinar el texto de la conversación y las recomendaciones
    const fullText = `Conversación:\n${conversationText}\n\nRecomendaciones:\n${recommendationsText}`;

    // Verificar si hay texto para generar el PDF
    if (!fullText) {
        alert("No hay contenido para generar el archivo PDF.");
        return;
    }

    try {
        const { jsPDF } = window.jspdf;
        const pdf = new jsPDF();

        const pageWidth = pdf.internal.pageSize.getWidth();
        const margin = 10;
        const maxLineWidth = pageWidth - margin * 2;

        pdf.setFont("Helvetica", "normal");
        pdf.setFontSize(12);

        const textLines = pdf.splitTextToSize(fullText, maxLineWidth);
        pdf.text(textLines, margin, margin + 10);

        // Descargar el archivo
        pdf.save("conversation_and_recommendations.pdf");
    } catch (error) {
        console.error("Error al generar el PDF:", error);
        alert("Ocurrió un error al generar el archivo PDF. Verifica la consola para más detalles.");
    }
};