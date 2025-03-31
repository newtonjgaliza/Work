(function() {
    const table = document.getElementById('table');
    if (!table) {
        console.error('Tabela não encontrada');
        return;
    }

    const rows = table.querySelectorAll('tbody tr');
    const resultados = [];

    rows.forEach(row => {
        const cells = row.querySelectorAll('td');
        
        const pdfLink = cells[6].querySelector('a')?.href || '';
        const materiaLink = cells[7].querySelector('a')?.href || '';

        const item = {
            "Edição": cells[0].textContent.trim(),
            "Código": cells[1].textContent.trim(),
            "Titulo": cells[2].textContent.trim(),
            "Tipo": cells[3].textContent.trim(),
            "Setor": cells[4].textContent.trim(),
            "Data": cells[5].textContent.trim(), // Campo novo
            "PDF": pdfLink,
            "Link": materiaLink
        };

        resultados.push(item);
    });

    console.log(JSON.stringify(resultados, null, 2));
})();
