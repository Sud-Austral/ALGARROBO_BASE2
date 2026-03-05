// pdf.js - Externalized PDF generation logic
function downloadProjectPDF(projectId) {
    // Checking if proyectos array is available in the global scope
    const proyecto = typeof proyectos !== 'undefined' ? proyectos.find(p => p.id === projectId) : null;
    if (!proyecto) return;

    const printWin = window.open('', '_blank');
    if (!printWin) {
        if (typeof showToast === 'function') {
            showToast('Habilite las ventanas emergentes para descargar el PDF', 'warning');
        } else {
            alert('Habilite las ventanas emergentes para descargar el PDF');
        }
        return;
    }

    const sheet = document.getElementById('printableProjectSheet').cloneNode(true);
    sheet.querySelectorAll('.no-print').forEach(el => el.remove());

    const content = sheet.outerHTML;
    
    // As an external script, template literals with tags like <script> or HTML structure 
    // do not trigger HTML parsing errors in the main browser window.
    const html = `<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>Ficha de Proyecto - ${proyecto.nombre || ''}</title>
    <link href="https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;500;600;700&display=swap" rel="stylesheet">
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">
    <script src="https://cdn.tailwindcss.com"></script>
    <style>
        body { font-family: 'Outfit', sans-serif; padding: 2rem; background: white; }
        .bg-gray-50 { background-color: #f9fafb !important; }
        .bg-indigo-50 { background-color: #eef2ff !important; }
        .bg-purple-50 { background-color: #faf5ff !important; }
        .bg-amber-50 { background-color: #fffbeb !important; }
        @page { margin: 1.5cm; size: letter; }
        * { print-color-adjust: exact; -webkit-print-color-adjust: exact; }
        .max-w-4xl { max-width: 56rem; margin-left: auto; margin-right: auto; }
    </style>
</head>
<body onload="setTimeout(function() { window.print(); setTimeout(function() { window.close(); }, 500); }, 1000);">
    <div class="max-w-4xl mx-auto">
        ${content}
    </div>
</body>
</html>`;

    printWin.document.open();
    printWin.document.write(html);
    printWin.document.close();
}
