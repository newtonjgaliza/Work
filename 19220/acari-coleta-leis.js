const BASE_URL = "https://sapl.acari.rn.leg.br";

// Função para remover acentos dos nomes dos meses
function removerAcentos(str) {
  return str.normalize("NFD").replace(/[\u0300-\u036f]/g, "");
}

// Dicionário de meses com nomes sem acentos
const meses = {
  janeiro: '01', fevereiro: '02', marco: '03', abril: '04',
  maio: '05', junho: '06', julho: '07', agosto: '08',
  setembro: '09', outubro: '10', novembro: '11', dezembro: '12'
};

// Seleciona todos os <td>s dentro de <tr>
const tds = document.querySelectorAll('table tr td');

const resultados = Array.from(tds).map(td => {
  const resultado = {};

  // Título
  const tituloElement = td.querySelector('a strong');
  if (tituloElement) {
    const titulo = tituloElement.textContent.trim();
    resultado["Titulo"] = titulo;

    // Extrair e formatar a data do título
    const dataRegex = /de (\d{2}) de (\w+) de (\d{4})/i;
    const match = titulo.match(dataRegex);
    if (match) {
      let [_, dia, mesNome, ano] = match;
      mesNome = removerAcentos(mesNome.toLowerCase());
      const mes = meses[mesNome];
      if (mes) {
        resultado["Data"] = `${dia.padStart(2, '0')}/${mes}/${ano}`;
      }
    }
  }

  // Ementa
  const ementaStrong = Array.from(td.querySelectorAll('strong')).find(strong =>
    strong.textContent.trim().startsWith('Ementa')
  );
  if (ementaStrong) {
    let node = ementaStrong.nextSibling;
    while (node && (!node.textContent || node.textContent.trim() === '')) {
      node = node.nextSibling;
    }
    if (node && node.textContent) {
      resultado["Ementa"] = node.textContent.trim();
    }
  }

  // Link PDF
  const linkOriginal = Array.from(td.querySelectorAll('a')).find(a =>
    a.textContent.includes("Texto Original")
  );
  if (linkOriginal) {
    const href = linkOriginal.getAttribute('href');
    resultado["Link PDF"] = BASE_URL + href;
  }

  return resultado["Titulo"] ? resultado : null;
}).filter(Boolean); // Remove nulls

// Buscar número da página atual pelo conteúdo do <a class="page-link"> ativo ou com valor
const numeroPagina = document.querySelector('a.page-link[href*="page="]')?.textContent.trim() || '1';

// Exibe o resultado no console
console.log(JSON.stringify(resultados, null, 2));

// Gera e baixa o arquivo JSON com nome baseado no número da página
const blob = new Blob([JSON.stringify(resultados, null, 2)], { type: "application/json" });
const url = URL.createObjectURL(blob);
const a = document.createElement("a");
a.href = url;
a.download = `acari-leis-${numeroPagina}.json`;
document.body.appendChild(a);
a.click();
document.body.removeChild(a);
URL.revokeObjectURL(url);




/*
const BASE_URL = "https://sapl.acari.rn.leg.br";

// Seleciona todos os <td>s dentro de <tr>
const tds = document.querySelectorAll('table tr td');

const resultados = Array.from(tds).map(td => {
  const resultado = {};

  // Título
  const tituloElement = td.querySelector('a strong');
  if (tituloElement) {
    const titulo = tituloElement.textContent.trim();
    resultado["Titulo"] = titulo;

    // Extrair e formatar a data do título
    const dataRegex = /de (\d{2}) de (\w+) de (\d{4})/i;
    const meses = {
      janeiro: '01', fevereiro: '02', março: '03', abril: '04',
      maio: '05', junho: '06', julho: '07', agosto: '08',
      setembro: '09', outubro: '10', novembro: '11', dezembro: '12'
    };
    const match = titulo.match(dataRegex);
    if (match) {
      const [_, dia, mesNome, ano] = match;
      const mes = meses[mesNome.toLowerCase()];
      if (mes) {
        resultado["Data"] = `${dia.padStart(2, '0')}/${mes}/${ano}`;
      }
    }
  }

  // Ementa
  const ementaStrong = Array.from(td.querySelectorAll('strong')).find(strong =>
    strong.textContent.trim().startsWith('Ementa')
  );
  if (ementaStrong) {
    let node = ementaStrong.nextSibling;
    while (node && (!node.textContent || node.textContent.trim() === '')) {
      node = node.nextSibling;
    }
    if (node && node.textContent) {
      resultado["Ementa"] = node.textContent.trim();
    }
  }

  // Link PDF
  const linkOriginal = Array.from(td.querySelectorAll('a')).find(a =>
    a.textContent.includes("Texto Original")
  );
  if (linkOriginal) {
    const href = linkOriginal.getAttribute('href');
    resultado["Link PDF"] = BASE_URL + href;
  }

  return resultado["Titulo"] ? resultado : null;
}).filter(Boolean); // Remove nulls

// Buscar número da página atual pelo conteúdo do <a class="page-link"> ativo ou com valor
const numeroPagina = document.querySelector('a.page-link[href*="page="]')?.textContent.trim() || '1';

// Exibe o resultado no console
console.log(JSON.stringify(resultados, null, 2));

// Gera e baixa o arquivo JSON com nome baseado no número da página
const blob = new Blob([JSON.stringify(resultados, null, 2)], { type: "application/json" });
const url = URL.createObjectURL(blob);
const a = document.createElement("a");
a.href = url;
a.download = `acari-leis-${numeroPagina}.json`;
document.body.appendChild(a);
a.click();
document.body.removeChild(a);
URL.revokeObjectURL(url);
*/


/*
const BASE_URL = "https://sapl.acari.rn.leg.br";

// Seleciona todos os <td>s dentro de <tr>
const tds = document.querySelectorAll('table tr td');

const resultados = Array.from(tds).map(td => {
  const resultado = {};

  // Título
  const tituloElement = td.querySelector('a strong');
  if (tituloElement) {
    const titulo = tituloElement.textContent.trim();
    resultado["Titulo"] = titulo;

    // Extrair e formatar a data do título
    const dataRegex = /de (\d{2}) de (\w+) de (\d{4})/i;
    const meses = {
      janeiro: '01', fevereiro: '02', março: '03', abril: '04',
      maio: '05', junho: '06', julho: '07', agosto: '08',
      setembro: '09', outubro: '10', novembro: '11', dezembro: '12'
    };
    const match = titulo.match(dataRegex);
    if (match) {
      const [_, dia, mesNome, ano] = match;
      const mes = meses[mesNome.toLowerCase()];
      if (mes) {
        resultado["Data"] = `${dia.padStart(2, '0')}/${mes}/${ano}`;
      }
    }
  }

  // Ementa (encontrar <strong>Ementa:</strong> e buscar próximo TextNode com conteúdo)
  const ementaStrong = Array.from(td.querySelectorAll('strong')).find(strong =>
    strong.textContent.trim().startsWith('Ementa')
  );
  if (ementaStrong) {
    let node = ementaStrong.nextSibling;
    while (node && (!node.textContent || node.textContent.trim() === '')) {
      node = node.nextSibling;
    }
    if (node && node.textContent) {
      resultado["Ementa"] = node.textContent.trim();
    }
  }

  // Link PDF
  const linkOriginal = Array.from(td.querySelectorAll('a')).find(a =>
    a.textContent.includes("Texto Original")
  );
  if (linkOriginal) {
    const href = linkOriginal.getAttribute('href');
    resultado["Link PDF"] = BASE_URL + href;
  }

  // Só retorna se tiver Título
  return resultado["Titulo"] ? resultado : null;
}).filter(Boolean); // Remove nulls

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
*/
