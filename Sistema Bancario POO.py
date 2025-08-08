from __future__ import annotations
from abc import ABC, abstractmethod
from datetime import datetime, date
import textwrap


# ========== Transações ==========

class Transacao(ABC):
    @property
    @abstractmethod
    def valor(self) -> float: ...

    @abstractmethod
    def registrar(self, conta: "Conta") -> bool: ...


class Deposito(Transacao):
    def __init__(self, valor: float):
        self._valor = float(valor)

    @property
    def valor(self) -> float:
        return self._valor

    def registrar(self, conta: "Conta") -> bool:
        sucesso = conta.depositar(self.valor)
        if sucesso:
            conta.historico.adicionar_transacao("DEPÓSITO", self.valor)
        return sucesso


class Saque(Transacao):
    def __init__(self, valor: float):
        self._valor = float(valor)

    @property
    def valor(self) -> float:
        return self._valor

    def registrar(self, conta: "Conta") -> bool:
        sucesso = conta.sacar(self.valor)
        if sucesso:
            conta.historico.adicionar_transacao("SAQUE", self.valor)
        return sucesso


# ========== Histórico ==========

class Historico:
    def __init__(self):
        self.transacoes: list[dict] = []

    def adicionar_transacao(self, tipo: str, valor: float) -> None:
        self.transacoes.append(
            {"tipo": tipo, "valor": float(valor), "quando": datetime.now()}
        )

    def extrato_formatado(self) -> str:
        if not self.transacoes:
            return "Não foram realizadas movimentações."
        linhas = []
        for t in self.transacoes:
            quando = t["quando"].strftime("%d/%m/%Y %H:%M:%S")
            linhas.append(f"{quando}  {t['tipo']:<10} R$ {t['valor']:.2f}")
        return "\n".join(linhas)

    def contagem_saques_no_dia(self, d: date) -> int:
        return sum(
            1 for t in self.transacoes
            if t["tipo"] == "SAQUE" and t["quando"].date() == d
        )


# ========== Contas ==========

class Conta:
    def __init__(self, cliente: "Cliente", numero: int, agencia: str = "0001"):
        self._saldo: float = 0.0
        self.numero: int = int(numero)
        self.agencia: str = str(agencia)
        self.cliente: Cliente = cliente
        self.historico: Historico = Historico()

    @classmethod
    def nova_conta(cls, cliente: "Cliente", numero: int) -> "Conta":
        return cls(cliente=cliente, numero=numero)

    @property
    def saldo(self) -> float:
        return self._saldo

    def depositar(self, valor: float) -> bool:
        if valor <= 0:
            print("Operação falhou: valor de depósito inválido.")
            return False
        self._saldo += valor
        return True

    def sacar(self, valor: float) -> bool:
        if valor <= 0:
            print("Operação falhou: valor de saque inválido.")
            return False
        if valor > self._saldo:
            print("Operação falhou: saldo insuficiente.")
            return False
        self._saldo -= valor
        return True


class ContaCorrente(Conta):
    def __init__(self, cliente: "Cliente", numero: int, agencia: str = "0001",
                 limite: float = 500.0, limite_saques: int = 3):
        super().__init__(cliente, numero, agencia)
        self.limite: float = float(limite)
        self.limite_saques: int = int(limite_saques)

    def sacar(self, valor: float) -> bool:
        # regra adicional: limite de valor e de quantidade por dia
        if valor > self.limite:
            print(f"Operação falhou: saque excede o limite de R$ {self.limite:.2f}.")
            return False
        saques_hoje = self.historico.contagem_saques_no_dia(date.today())
        if saques_hoje >= self.limite_saques:
            print("Operação falhou: número máximo de saques diários excedido.")
            return False
        return super().sacar(valor)


# ========== Clientes ==========

class Cliente:
    def __init__(self, endereco: str):
        self.endereco: str = endereco
        self.contas: list[Conta] = []

    def realizar_transacao(self, conta: Conta, transacao: Transacao) -> None:
        if conta not in self.contas:
            print("Operação falhou: conta não pertence a este cliente.")
            return
        transacao.registrar(conta)

    def adicionar_conta(self, conta: Conta) -> None:
        self.contas.append(conta)


class PessoaFisica(Cliente):
    def __init__(self, cpf: str, nome: str, data_nascimento: str, endereco: str):
        super().__init__(endereco=endereco)
        self.cpf: str = cpf
        self.nome: str = nome
        self.data_nascimento: str = data_nascimento  # pode ser date, mantendo str por simplicidade


# ========== Utilidades do “sistema” (interface de linha de comando) ==========

def menu() -> str:
    opcoes = """
    ================ MENU ================
    [nu] Novo usuário
    [nc] Nova conta
    [lc] Listar contas
    [d]  Depositar
    [s]  Sacar
    [e]  Extrato
    [q]  Sair
    => """
    return input(textwrap.dedent(opcoes)).strip().lower()


def localizar_cliente(cpf: str, clientes: list[PessoaFisica]) -> PessoaFisica | None:
    return next((c for c in clientes if c.cpf == cpf), None)


def localizar_conta(numero: int, contas: list[Conta]) -> Conta | None:
    return next((c for c in contas if c.numero == numero), None)


def op_novo_usuario(clientes: list[PessoaFisica]) -> None:
    cpf = input("CPF (somente números): ").strip()
    if localizar_cliente(cpf, clientes):
        print("Já existe usuário com esse CPF.")
        return
    nome = input("Nome completo: ").strip()
    data_nasc = input("Data de nascimento (dd-mm-aaaa): ").strip()
    endereco = input("Endereço (logradouro, nro - bairro - cidade/UF): ").strip()
    cliente = PessoaFisica(cpf=cpf, nome=nome, data_nascimento=data_nasc, endereco=endereco)
    clientes.append(cliente)
    print("Usuário criado com sucesso.")


def op_nova_conta(clientes: list[PessoaFisica], contas: list[Conta]) -> None:
    cpf = input("CPF do titular: ").strip()
    cliente = localizar_cliente(cpf, clientes)
    if not cliente:
        print("Usuário não encontrado.")
        return
    numero = len(contas) + 1
    conta = ContaCorrente.nova_conta(cliente=cliente, numero=numero)  # usando ContaCorrente
    cliente.adicionar_conta(conta)
    contas.append(conta)
    print(f"Conta criada com sucesso. Agência {conta.agencia}  C/C {conta.numero}")


def op_listar_contas(contas: list[Conta]) -> None:
    if not contas:
        print("Nenhuma conta cadastrada.")
        return
    for c in contas:
        print("=" * 60)
        print(f"Agência: {c.agencia}")
        print(f"C/C:     {c.numero}")
        print(f"Titular: {c.cliente.nome}")
        print(f"Saldo:   R$ {c.saldo:.2f}")


def op_depositar(clientes: list[PessoaFisica]) -> None:
    cpf = input("CPF do titular: ").strip()
    cliente = localizar_cliente(cpf, clientes)
    if not cliente or not cliente.contas:
        print("Cliente não encontrado ou sem contas.")
        return
    numero = int(input("Número da conta: "))
    conta = next((c for c in cliente.contas if c.numero == numero), None)
    if not conta:
        print("Conta não encontrada para este cliente.")
        return
    valor = float(input("Valor do depósito: "))
    cliente.realizar_transacao(conta, Deposito(valor))


def op_sacar(clientes: list[PessoaFisica]) -> None:
    cpf = input("CPF do titular: ").strip()
    cliente = localizar_cliente(cpf, clientes)
    if not cliente or not cliente.contas:
        print("Cliente não encontrado ou sem contas.")
        return
    numero = int(input("Número da conta: "))
    conta = next((c for c in cliente.contas if c.numero == numero), None)
    if not conta:
        print("Conta não encontrada para este cliente.")
        return
    valor = float(input("Valor do saque: "))
    cliente.realizar_transacao(conta, Saque(valor))


def op_extrato(contas: list[Conta]) -> None:
    numero = int(input("Número da conta: "))
    conta = localizar_conta(numero, contas)
    if not conta:
        print("Conta não encontrada.")
        return
    print("\n================ EXTRATO ================")
    print(conta.historico.extrato_formatado())
    print(f"\nSaldo:\tR$ {conta.saldo:.2f}")
    print("=========================================")


def main() -> None:
    clientes: list[PessoaFisica] = []
    contas: list[Conta] = []

    while True:
        opcao = menu()

        if opcao == "nu":
            op_novo_usuario(clientes)

        elif opcao == "nc":
            op_nova_conta(clientes, contas)

        elif opcao == "lc":
            op_listar_contas(contas)

        elif opcao == "d":
            op_depositar(clientes)

        elif opcao == "s":
            op_sacar(clientes)

        elif opcao == "e":
            op_extrato(contas)

        elif opcao == "q":
            print("Sistema encerrado.")
            break

        else:
            print("Opção inválida. Tente novamente.")


if __name__ == "__main__":
    main()
