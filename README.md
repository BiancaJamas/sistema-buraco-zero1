# sistema-buraco-zero

## 📋 Sobre o Projeto
O **Sistema Buraco Zero** é uma aplicação web desenvolvida como parte do Projeto Integrador da UNIVESP. O objetivo do sistema é facilitar a comunicação entre os cidadãos e a administração pública, permitindo o registro de ocorrências urbanas (como buracos em vias públicas), acompanhamento de status e gestão administrativa.

## 🚀 Funcionalidades
* **Cadastro de Ocorrências:** Permite ao cidadão enviar relato com foto, descrição, localização e coordenadas.
* **Painel Público:** Exibe o panorama geral e ranking de bairros com ocorrências.
* **Área Administrativa:** Permite ao administrador fazer login seguro, visualizar detalhes das denúncias e atualizar o status (Pendente, Em Andamento, Concluído).
* **API Integrada:** Disponibiliza endpoint em JSON (`/api/denuncias`) para consulta dos dados.

## 🛠️ Tecnologias Utilizadas
* **Backend:** Python com Flask
* **Banco de Dados:** SQLite
* **Frontend:** HTML5, CSS3, JavaScript (com foco em acessibilidade e responsividade)
* **Servidor (Deploy/Configuração):** Gunicorn

## ♿ Acessibilidade
O projeto conta com preocupações de acessibilidade estrutural, incluindo:
* Uso de marcação semântica em HTML5.
* Atributos de internacionalização (`lang="pt-BR"`).
* Rótulos descritivos (`label for` e `aria-label`).

## 🧪 Testes Automatizados
O sistema possui testes unitários básicos configurados utilizando a biblioteca `unittest` do Python para validação de rotas e páginas principais.