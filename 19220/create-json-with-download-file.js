const BASE_URL = "https://sapl.acari.rn.leg.br";

// Seleciona todos os <td>s da tabela (ajuste seletor conforme necessário)
const tds = document.querySelectorAll('table td');

const resultados = Array.from(tds).map(td => {
  const resultado = {};

 // Titulo
  const tituloLink = td.querySelector('strong a');
  if (tituloLink) {
    resultado["Titulo"] = tituloLink.textContent.trim();
  }



  // Ementa
  const ementa = td.querySelector('div.dont-break-out')?.textContent.trim();
  if (ementa) {
    resultado["Ementa"] = ementa;
  }

  // Link PDF
  const linkOriginal = Array.from(td.querySelectorAll('a')).find(a => a.textContent.includes("Texto Original"));
  if (linkOriginal) {
    resultado["Link PDF"] = BASE_URL + linkOriginal.getAttribute('href');
  }

  // Campos <strong> + conteúdo (exceto Autor(es) e Data Anexação)
  td.querySelectorAll('strong').forEach(strong => {
    const rawLabel = strong.textContent.trim().replace(/:$/, '');
    if (["Autor(es)", "Data Anexação"].includes(rawLabel)) return;

    const valueNode = strong.nextSibling;
    if (valueNode && valueNode.nodeType === Node.TEXT_NODE) {
      const value = valueNode.textContent.trim().replace(/^\u00a0/, '');
      if (value) {
        resultado[rawLabel] = value;
      }
    }
  });

  return resultado;
});

// Exibe o resultado no console
console.log(JSON.stringify(resultados, null, 2));

// Gera e baixa o arquivo JSON
const blob = new Blob([JSON.stringify(resultados, null, 2)], { type: "application/json" });
const url = URL.createObjectURL(blob);
const a = document.createElement("a");
a.href = url;
a.download = "materias-sapl.json";
document.body.appendChild(a);
a.click();
document.body.removeChild(a);
URL.revokeObjectURL(url);
