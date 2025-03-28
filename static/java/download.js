document.getElementById("download-button").onclick = async function () {
    const chatBox = document.getElementById("chat-box");
    const recommendationsList = document.getElementById("recommendations-list");

    if (!chatBox || chatBox.children.length === 0) {
        alert("No hay conversaciones disponibles para descargar.");
        return;
    }

    const conversationText = Array.from(chatBox.children)
        .map(child => child.textContent.trim())
        .join("\n\n");

    const recommendationsText = Array.from(recommendationsList.children)
        .map(child => {
            if (child.querySelector('a')) {
                const link = child.querySelector('a');
                return `${link.textContent}: ${link.href}`;
            } else {
                return child.textContent.trim();
            }
        })
        .join("\n\n");

    const fullText = `Conversación:\n${conversationText}\n\nRecomendaciones:\n${recommendationsText}`;

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

        const pdfBlob = pdf.output("blob");

        // Solicitar correo del usuario
        const userEmail = prompt("Ingresa tu correo electrónico para recibir el PDF:");

        if (!userEmail || !userEmail.includes("@")) {
            alert("Correo inválido.");
            return;
        }

        // Enviar el PDF al servidor
        const formData = new FormData();
        formData.append("file", pdfBlob, "conversation.pdf");
        formData.append("email", userEmail);

        const response = await fetch("/send-pdf-email", {
            method: "POST",
            body: formData
        });

        if (response.ok) {
            alert("¡PDF enviado correctamente al correo!");
        } else {
            throw new Error("Error al enviar el PDF.");
        }

    } catch (error) {
        console.error("Error:", error);
        alert("Ocurrió un error al generar o enviar el archivo PDF.");
    }
};
