# Sistema Bancário Orientado a Objetos em Python

Este projeto é uma evolução do sistema bancário anterior, agora implementado **com programação orientada a objetos (POO)** e seguindo o **modelo UML** definido pelo professor.  

O código utiliza **classes para clientes, contas, histórico e transações** (depósito e saque), substituindo o uso de dicionários e listas simples para manipulação dos dados.

---

## Funcionalidades

- **Cadastro de clientes** (CPF único, nome, data de nascimento e endereço)
- **Abertura de contas** vinculadas a clientes existentes
- **Depósitos** com registro no histórico
- **Saques** com:
  - Limite diário de valor por saque
  - Limite de quantidade de saques por dia
- **Emissão de extrato** formatado com histórico de transações
- **Listagem de contas cadastradas**
- **Controle por objetos**, conforme modelagem UML

---

## Estrutura de Classes

O sistema foi modelado com as seguintes classes:

| Classe        | Responsabilidade |
|---------------|------------------|
| **Transacao** (interface) | Interface para operações bancárias (método `registrar`) |
| **Deposito**  | Implementa a transação de depósito |
| **Saque**     | Implementa a transação de saque com regras de limite |
| **Historico** | Registra todas as transações da conta |
| **Conta**     | Estrutura básica de uma conta (número, agência, saldo) |
| **ContaCorrente** | Conta com limite de valor e quantidade de saques por dia |
| **Cliente**   | Representa um cliente e gerencia suas contas |
| **PessoaFisica** | Cliente pessoa física com CPF, nome e data de nascimento |

---
## Exemplo de Uso
================ MENU ================
[nu] Novo usuário
[nc] Nova conta
[lc] Listar contas
[d]  Depositar
[s]  Sacar
[e]  Extrato
[q]  Sair
=> nu
CPF (somente números): 12345678900
Nome completo: João da Silva
Data de nascimento (dd-mm-aaaa): 10-05-1990
Endereço (logradouro, nro - bairro - cidade/UF): Rua X, 100 - Centro - João Pessoa/PB
Usuário criado com sucesso.

---

## Observações

Cada cliente pode ter mais de uma conta, mas uma conta pertence a somente um cliente.
O número da agência é fixo: "0001".
Os dados são mantidos em memória (não há persistência em banco ou arquivo nesta versão).