(function() {
    function cleanText(el) {
        return el ? el.textContent.trim().replace(/\s+/g, ' ') : '';
    }

    let data = {};
    let currentSection = '';

    document.querySelectorAll('tbody > tr').forEach(tr => {
        if (tr.querySelector('td.h4')) {
            let txt = cleanText(tr.querySelector('td.h4'));
            let match = txt.match(/^\d+\s+(.*)$/);
            currentSection = match ? match[1] : txt;
            if (!data[currentSection]) {
                data[currentSection] = [];
            }
        } else if (tr.className && tr.className.startsWith('pergunta-')) {
            let codigo = tr.className.match(/pergunta-(\d+)/)[1];
            let pergunta = cleanText(tr.querySelectorAll('td')[1]);
            data[currentSection].push({ [pergunta]: codigo });
        }
    });

    // Converte para JSON e baixa
    let jsonStr = JSON.stringify(data, null, 2);
    let blob = new Blob([jsonStr], {type: 'application/json'});
    let a = document.createElement('a');
    a.href = URL.createObjectURL(blob);
    a.download = 'campos_vera_mendes.json';
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
})();
