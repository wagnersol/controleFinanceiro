
function consultaBalanco() {
  const parametrosBusca = {
    "ativo": document.getElementById("input_ativo").checked, 
    "passivo": document.getElementById("input_passivo").checked,
    "nome_cliente": document.getElementById("nome_cliente").value
  }

  let opcoes = {
    method: "POST",
    mode: "cors", // no-cors, *cors, same-origin
    credentials: "same-origin", // include, *same-origin, omit
    headers: {"Content-Type": "application/json"},
    body: JSON.stringify(parametrosBusca)
  }
  carregandoInicio()

  fetch("http://127.0.0.1:9000/executa_consulta_balanco", opcoes)
    .then((response) => response.json())
    .then((dados) => {
      formataBalanco(dados)
      carregandoFim()
    })

}

function formataBalanco(dados) {
  let tabela = document.getElementById("tabela_balanco")
  let html = ''
  let total = 0;

  for (dados_nota of dados) {
    let saldo = dados_nota[1] - dados_nota[2]
    total = total + saldo 
  
    html += '<tr>' // linha da tabela
    
    html += '<td>' // nome cliente
    html += dados_nota[0]
    html += '</td>'
    
    html += '<td>' // saldo
    html += formataMoeda(saldo)
    html += '</td>'

    html += '<td>' // data  
    html += dados_nota[3]
    html += '</td>'
    
    html += '</tr>'  
  }

  let data_hoje = new Date();

  html += '<tr>' // linha da tabela
    
  html += '<td>'
  html += '<strong>Total (' + dados.length + ' clientes):</strong>'
  html += '</td>'
  
  html += '<td>' // saldo
  html += formataMoeda(total)
  html += '</td>'

  let dia = data_hoje.getDay()
  if (dia < 10) {
    dia = "0" + dia
  }

  html += '<td>' // data  
  html += dia + "-" + data_hoje.getMonth() + "-" + data_hoje.getFullYear()
  html += '</td>'
  
  html += '</tr>'

  tabela.innerHTML = html
}


function checkboxClicado() {
  consultaBalanco()
}

function submitFormularioConsulta(evento) {
  evento.preventDefault();
  consultaBalanco();
}

function carregandoInicio() {
  document.querySelectorAll('.carregando')[0].classList.remove('carregando-inativo')
}

function carregandoFim() {
  document.querySelectorAll('.carregando')[0].classList.add('carregando-inativo')
}

function formataMoeda(numero) {
  return new Intl.NumberFormat('pt-BR', { style: 'currency', currency: 'BRL' }).format(numero);
}