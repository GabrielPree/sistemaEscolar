import customtkinter as ctk
from pathlib import Path
from PIL import Image
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from exportar import exportar_excel, exportar_pdf
from matplotlib import style
import sys
import os
from banco_dados import (
    executar_bd,
    inserir_usuario,
    atualizar_notas,
    excluir_usuario,
    validar_usuario,
    listar_professores,
    listar_alunos,
    buscar_aluno,
    atualizar_aluno,
    atualizar_professor,
)
ctk.set_appearance_mode("light")
ctk.set_default_color_theme("blue")

# Função para obter o caminho do recurso (ícone e logo), funcionando tanto no ambiente de desenvolvimento quanto no executável criado pelo PyInstaller.
def caminho_recurso(arquivo):
    # Função para obter o caminho do recurso (ícone e logo), funcionando tanto no ambiente de desenvolvimento quanto no executável criado pelo PyInstaller.
    try:
        caminho = sys._MEIPASS  # quando vira .exe
    except Exception:
        caminho = os.path.abspath(".")  # quando roda normal

    return os.path.join(caminho, arquivo)

class LoginWindow(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.iconbitmap(caminho_recurso("icone.ico"))
        self.title("Sistema Escolar - Login")
        self.geometry("1050x800")
        self.configure(fg_color="#0f172a")

        executar_bd()  # Garantir que o banco de dados e tabelas existam
        
        # Container principal
        self.container = ctk.CTkFrame(self, corner_radius=20, fg_color="#f8fafc")
        self.container.pack(padx=20, pady=20, fill="both", expand=True)

        titulo_row = ctk.CTkFrame(self.container, fg_color="transparent")
        titulo_row.pack(pady=(35, 12))

        logo_path = caminho_recurso("logo.png")
        logo_base = Image.open(logo_path).convert("RGBA")
        alpha = logo_base.split()[3]
        logo_tint = Image.new("RGBA", logo_base.size, (30, 41, 59, 0))
        logo_tint.putalpha(alpha)
        self.logo_img = ctk.CTkImage(
            light_image=logo_tint,
            dark_image=logo_tint,
            size=(80, 80),
        )
        logo = ctk.CTkLabel(titulo_row, text="", image=self.logo_img, fg_color="transparent", text_color="#1e293b")
        logo.pack(side="left", padx=(0, 5), pady=(100, 0))

        # Título
        titulo = ctk.CTkLabel(titulo_row, text="Sistema Escolar",
                             font=("Arial", 80, "bold"), text_color="#1e293b")
        titulo.pack(side="left", padx=(0, 45), pady=(100, 0))

        # Subtítulo
        subtitulo = ctk.CTkLabel(self.container, text="Faça login para continuar",
                                font=("Arial", 28), text_color="#64748b")
        subtitulo.pack(pady=(0, 25))

        # Frame para inputs
        input_frame = ctk.CTkFrame(self.container, fg_color="transparent")
        input_frame.pack(padx=30, pady=0, expand=True)

        # Usuário
        ctk.CTkLabel(input_frame, text="Usuário:",
                    font=("Arial", 18, "bold"), text_color="#1e293b").pack(pady=(8, 6))
        
        self.usuario_entry = ctk.CTkEntry(input_frame,
                                         placeholder_text="Digite seu usuário",
                                         font=("Arial", 14),
                                         width=340,
                                         height=38)
        self.usuario_entry.pack(pady=(0, 14))

        # Senha
        ctk.CTkLabel(input_frame, text="Senha:",
                    font=("Arial", 18, "bold"), text_color="#1e293b").pack(pady=(8, 6))
        
        self.senha_entry = ctk.CTkEntry(input_frame,
                                       placeholder_text="Digite sua senha",
                                       show="*",
                                       font=("Arial", 14),
                                       width=340,
                                       height=38)
        self.senha_entry.pack(pady=(0, 14))

        # Botão Login
        btn_login = ctk.CTkButton(input_frame, text="Entrar",
                                 font=("Arial", 15, "bold"),
                                 fg_color="#0f172a",
                                 width=220,
                                 height=40,
                                 command=self.fazer_login)
        btn_login.pack(pady=(20, 10))

        # funcao para centralizar a janela na tela, mesmo em resolucoes diferentes
        def centralizar_janela(self):
            self.update_idletasks()
            largura = 1050
            altura = 800

            x = (self.winfo_screenwidth() // 2) - (largura // 2)
            y = (self.winfo_screenheight() // 2) - (altura // 2)

            self.geometry(f"{largura}x{altura}+{x}+{y}")
        centralizar_janela(self)

        # Mensagem de erro
        self.msg_erro = ctk.CTkLabel(input_frame, text="",
                                    font=("Arial", 16, "bold"), text_color="#b91c1c")
        self.msg_erro.pack(pady=(4, 0))

        # Atalhos de teclado para login
        self.bind("<Return>", self.atalho_login)
        self.bind("<KP_Enter>", self.atalho_login)

    def atalho_login(self, event=None):
        self.fazer_login()

    def fazer_login(self):
        usuario = self.usuario_entry.get().strip()
        senha = self.senha_entry.get().strip()

        if not usuario or not senha:
            self.msg_erro.configure(text="Preencha todos os campos!")
            return

        # Validar no banco de dados (retorna o tipo de usuário automaticamente)
        tipo_usuario = validar_usuario(usuario, senha)

        if tipo_usuario:
            # Captura a posicao atual para abrir a proxima janela no mesmo lugar.
            self.update_idletasks()
            pos_x = self.winfo_x()
            pos_y = self.winfo_y()
            # Login bem-sucedido
            self.destroy()
            app = SistemaEscolar(usuario, tipo_usuario, pos_x, pos_y)
            app.mainloop()
        else:
            self.msg_erro.configure(text="Usuário ou senha incorretos!")
            self.senha_entry.delete(0, "end")


class SistemaEscolar(ctk.CTk):
    def __init__(self, usuario_logado="", tipo_usuario="", pos_x=None, pos_y=None):
        super().__init__()
        self.iconbitmap(caminho_recurso("icone.ico"))

        self.usuario_logado = usuario_logado
        self.tipo_usuario = tipo_usuario
        self.visao_admin = "alunos"
        self.colunas_alunos = ("Nome", "Nota 1", "Nota 2", "Nota 3", "Nota 4", "Média", "Excluir")
        self.colunas_aluno = ("Nome", "Nota 1", "Nota 2", "Nota 3", "Nota 4", "Média")
        self.colunas_professores = ("Nome", "Disciplina", "Excluir")
        self.colunas_atuais = self.colunas_alunos
        self.alunos = []
        self.professores = []
        self.professores_disciplina = []
        self.alunos_notas = []
        self.ultima_pasta = None

        self.title(f"Sistema Escolar - {tipo_usuario.capitalize()}")
        if pos_x is not None and pos_y is not None:
            self.geometry(f"1050x800+{pos_x}+{pos_y}")
        else:
            self.geometry("1050x800")
        self.configure(fg_color="#0f172a")

        # Container principal
        self.container = ctk.CTkFrame(self, corner_radius=20, fg_color="#f8fafc")
        self.container.pack(padx=20, pady=20, fill="both", expand=True)

        self.configurar_estilo_treeview()
        self.carregar_dados()

        self.criar_header()
        self.criar_tabela()
        self.criar_footer()

#-------------------------- Funções auxiliares --------------------------

    def configurar_estilo_treeview(self):
        style = ttk.Style()

        style.configure(
            "Treeview",
            font=("Arial", 11),
            rowheight=34,
            background="#ffffff",
            fieldbackground="#ffffff",
            borderwidth=0
        )

        style.configure(
            "Treeview.Heading",
            font=("Arial", 12, "bold"),
            background="#f1f5f9",
            foreground="#1e293b",
            borderwidth=0
        )

        style.map(
            "Treeview",
            background=[("selected", "#36719F")],
            foreground=[("selected", "#ffffff")]
        )

    def carregar_dados(self):
        self.alunos_notas = listar_alunos() or []
        self.professores_com_disciplina = listar_professores() or []

    def formatar_nota(self, nota):
        if nota is None:
            return "-"
        try:
            return f"{float(nota):.1f}"
        except (TypeError, ValueError):
            return "-"

    def calcular_media(self, n1, n2, n3, n4):
        notas = []
        for nota in (n1, n2, n3, n4):
            if nota is not None:
                try:
                    notas.append(float(nota))
                except (TypeError, ValueError):
                    continue
        if not notas:
            return "-"
        return f"{(sum(notas) / len(notas)):.1f}"
    
    def abrir_cadastro(self, tipo):
        janela = ctk.CTkToplevel(self)
        janela.title(f"Cadastrar {tipo.capitalize()}")
        largura = 420
        altura = 400
        janela.geometry(f"{largura}x{altura}")
        janela.transient(self)
        janela.grab_set()

        # Centraliza a janela de cadastro em relacao ao app principal.
        self.update_idletasks()
        janela.update_idletasks()
        pos_x = self.winfo_x() + (self.winfo_width() // 2) - (largura // 2)
        pos_y = self.winfo_y() + (self.winfo_height() // 2) - (altura // 2)
        janela.geometry(f"{largura}x{altura}+{pos_x}+{pos_y}")

        frame = ctk.CTkFrame(janela, fg_color="transparent")
        frame.pack(fill="both", expand=True, padx=20, pady=20)

        ctk.CTkLabel(
            frame,
            text=f"Novo {tipo.capitalize()}",
            font=("Arial", 22, "bold"),
            text_color="#1e293b",
        ).pack(pady=(0, 18))

        ctk.CTkLabel(frame, text="Nome", font=("Arial", 14, "bold")).pack(anchor="w")
        entrada_nome = ctk.CTkEntry(frame, width=360, height=36)
        entrada_nome.pack(pady=(6, 12))

        ctk.CTkLabel(frame, text="Senha", font=("Arial", 14, "bold")).pack(anchor="w")
        entrada_senha = ctk.CTkEntry(frame, width=360, height=36, show="*")
        entrada_senha.pack(pady=(6, 12))

        entrada_disciplina = None
        if tipo == "professor":
            ctk.CTkLabel(frame, text="Disciplina", font=("Arial", 14, "bold")).pack(anchor="w")
            entrada_disciplina = ctk.CTkEntry(frame, width=360, height=36)
            entrada_disciplina.pack(pady=(6, 12))

        entradas_notas = []
        if tipo == "aluno":
            notas_frame = ctk.CTkFrame(frame, fg_color="transparent")
            notas_frame.pack(fill="x", pady=(4, 10))

            for indice in range(1, 5):
                ctk.CTkLabel(
                    notas_frame,
                    text=f"Nota {indice}",
                    font=("Arial", 12, "bold"),
                ).grid(row=0, column=indice - 1, padx=5, pady=(0, 5))

                entrada_nota = ctk.CTkEntry(notas_frame, width=80, height=32, placeholder_text="0-10")
                entrada_nota.grid(row=1, column=indice - 1, padx=5)
                entradas_notas.append(entrada_nota)

        msg = ctk.CTkLabel(frame, text="", font=("Arial", 12, "bold"), text_color="#b91c1c")
        msg.pack(pady=(5, 0))

        def salvar_cadastro():
            nome = entrada_nome.get().strip()
            senha = entrada_senha.get().strip()

            if not nome or not senha:
                msg.configure(text="Preencha nome e senha.")
                return

            disciplina = ""
            if tipo == "professor":
                disciplina = entrada_disciplina.get().strip() if entrada_disciplina else ""
                if not disciplina:
                    msg.configure(text="Informe a disciplina do professor.")
                    return

            if tipo == "aluno":
                notas = []
                for entrada_nota in entradas_notas:
                    valor = entrada_nota.get().strip()
                    if not valor:
                        notas.append(None)
                        continue
                    try:
                        nota_float = float(valor)
                    except ValueError:
                        msg.configure(text="Notas devem ser numéricas.")
                        return

                    if nota_float < 0 or nota_float > 10:
                        msg.configure(text="Notas devem estar entre 0 e 10.")
                        return
                    notas.append(round(nota_float, 1))

            sucesso = inserir_usuario(nome, disciplina, senha, tipo)
            if not sucesso:
                msg.configure(text="Não foi possível cadastrar (nome já existe?).")
                return

            if tipo == "aluno":
                atualizar_notas(sucesso, notas[0], notas[1], notas[2], notas[3])

            self.carregar_dados()
            self.atualizar_treeview()
            janela.destroy()

        botoes = ctk.CTkFrame(frame, fg_color="transparent")
        botoes.pack(pady=(0, 0))

        btn_salvar = ctk.CTkButton(botoes, text="Salvar", fg_color="#0f172a", command=salvar_cadastro)
        btn_salvar.pack(side="left", padx=(0, 8))

        btn_cancelar = ctk.CTkButton(
            botoes,
            text="Cancelar",
            fg_color="#991b1b",
            command=janela.destroy,
        )
        btn_cancelar.pack(side="left")

#-------------------------- Header e funções de cadastro/logout --------------------------

    def criar_header(self):
        header = ctk.CTkFrame(self.container, fg_color="transparent")
        header.pack(fill="x", padx=20, pady=(20, 10))

        # Título e informações do usuário
        titulo_frame = ctk.CTkFrame(header, fg_color="transparent")
        titulo_frame.pack(anchor="w", fill="x")

        titulo_row = ctk.CTkFrame(titulo_frame, fg_color="transparent")
        titulo_row.pack(anchor="w", fill="x")

        logo_path = caminho_recurso("logo.png")
        logo_base = Image.open(logo_path).convert("RGBA")
        alpha = logo_base.split()[3]
        logo_tint = Image.new("RGBA", logo_base.size, (30, 41, 59, 0))
        logo_tint.putalpha(alpha)
        self.logo_header_img = ctk.CTkImage(
            light_image=logo_tint,
            dark_image=logo_tint,
            size=(34, 34),
        )

        logo = ctk.CTkLabel(titulo_row, text="", image=self.logo_header_img, fg_color="transparent")
        logo.pack(side="left", padx=(0, 8))

        titulo = ctk.CTkLabel(titulo_row, text="Sistema Escolar",
                             font=("Arial", 30, "bold"), text_color="#1e293b")
        titulo.pack(side="left")

        subtitulo = ctk.CTkLabel(titulo_frame, text="Gerenciamento de Alunos e Notas",
                                font=("Arial", 16), text_color="#64748b")
        subtitulo.pack(anchor="w")

        # Info do usuário logado
        usuario_info = ctk.CTkLabel(titulo_row, 
                                   text=f"Logado como: {self.usuario_logado} ({self.tipo_usuario})",
                                   font=("Arial", 14), text_color="#64748b")
        usuario_info.pack(side="right", anchor="w")

        # linha de topo separa o header da tabela e dos botoes
        linha_topo = ctk.CTkFrame(header, fg_color="transparent")
        linha_topo.pack(fill="x", pady=10)

        # lado esquerdo (busca)
        busca_frame = ctk.CTkFrame(linha_topo, fg_color="transparent")
        busca_frame.pack(side="left")

        self.busca_entry = ctk.CTkEntry(
            busca_frame,
            placeholder_text="Buscar...",
            width=250,
            height=36
        )
        self.busca_entry.pack(side="left", padx=(0, 10))

        btn_buscar = ctk.CTkButton(
            busca_frame,
            text="Buscar",
            width=90,
            fg_color="#0f172a",
            command=self.filtrar_busca
        )
        btn_buscar.pack(side="left")


        # lado direito (botões)
        btn_frame = ctk.CTkFrame(linha_topo, fg_color="transparent")
        btn_frame.pack(side="right")

        # Botão cadastrar professor (apenas para admin)
        if self.tipo_usuario == "admin":
            btn_professor = ctk.CTkButton(btn_frame, text="Cadastrar Professor",
                                         corner_radius=10, fg_color="#0f172a",
                                         width=170, height=36,
                                         font=("Arial", 13, "bold"),
                                         command=lambda: self.abrir_cadastro("professor"))
            btn_professor.pack(side="left", padx=5)

        # Botão cadastrar aluno
        if self.tipo_usuario in ("admin", "professor"):
            btn_aluno = ctk.CTkButton(btn_frame, text="Cadastrar Aluno",
                                corner_radius=10, fg_color="#0f172a",
                                width=150, height=36,
                                font=("Arial", 13, "bold"),
                                command=lambda: self.abrir_cadastro("aluno"))
            btn_aluno.pack(side="left", padx=5)

        # Botão logout
        btn_logout = ctk.CTkButton(btn_frame, text="Logout",
                                  corner_radius=10, fg_color="#991b1b",
                                  width=100, height=36,
                                  font=("Arial", 13, "bold"),
                                  command=self.fazer_logout)
        btn_logout.pack(side="left", padx=5)

    def fazer_logout(self):
        self.update_idletasks()
        pos_x = self.winfo_x()
        pos_y = self.winfo_y()
        self.destroy()
        login_window = LoginWindow()
        login_window.geometry(f"1050x800+{pos_x}+{pos_y}")
        login_window.mainloop()

#-------------------------- Tabela de alunos (ou professores) --------------------------        

    def criar_tabela(self):
        tabela_frame = ctk.CTkFrame(self.container, corner_radius=10, fg_color="#ffffff")
        tabela_frame.pack(fill="both", expand=True, padx=20, pady=10)

        topo_tabela = ctk.CTkFrame(tabela_frame, fg_color="transparent")
        topo_tabela.pack(fill="x", padx=10, pady=(10, 8))

        self.titulo_tabela = ctk.CTkLabel(
            topo_tabela,
            text="",
            font=("Arial", 14, "bold"),
            text_color="#1e293b"
        )
        self.titulo_tabela.pack(side="left")

        if self.tipo_usuario == "admin":
            btn_visao = ctk.CTkButton(
                topo_tabela,
                text="Ver Professores",
                width=150,
                fg_color="#0f172a",
                command=self.alternar_visao_admin,
            )
            btn_visao.pack(side="left", padx=(12, 0))
            self.btn_visao = btn_visao

        if self.tipo_usuario in ("admin", "professor"):
            btn_editar = ctk.CTkButton(
                topo_tabela,
                text="Editar",
                width=150,
                fg_color="#0f172a",
                command=self.editar_registro
            )
            btn_editar.pack(side="right", padx=(0, 5))

        # Frame da tabela
        tree_frame = ctk.CTkFrame(tabela_frame, fg_color="transparent")
        tree_frame.pack(fill="both", expand=True, padx=10, pady=(0, 10))

        # Configura o grid
        tree_frame.grid_rowconfigure(0, weight=1)
        tree_frame.grid_columnconfigure(0, weight=1)

        # treeview
        self.tree = ttk.Treeview(
            tree_frame,
            columns=self.colunas_atuais,
            show="headings"
        )
        self.tree.grid(row=0, column=0, sticky="nsew")

        # scrollbar vertical
        self.scrollbar_y = ctk.CTkScrollbar(
            tree_frame,
            orientation="vertical",
            command=self.tree.yview
        )
        self.scrollbar_y.grid(row=0, column=1, sticky="ns", padx=(5, 0))

        self.tree.configure(yscrollcommand=self.scrollbar_y.set)

        # colunas
        self.configurar_colunas_treeview()

        # Permitir que as colunas se ajustem automaticamente ao redimensionar a janela
        for col in self.colunas_atuais:
            self.tree.column(col, stretch=True)

        self.tree.bind("<Button-1>", self.clique_treeview)

        # ajuste dinamicamente as colunas quando a janela for redimensionada
        self.tree.bind("<Configure>", self.ajustar_colunas_treeview)

        self.tree.bind("<Motion>", self.hover_linha)

        self.busca_entry.bind("<KeyRelease>", lambda e: self.filtrar_busca())

        self.tree.tag_configure("hover", background="#dbeafe")
        self.tree.tag_configure("selected", background="#489afd")
        
        self.atualizar_treeview()

    def configurar_colunas_treeview(self):
        # Configuração das colunas do treeview de acordo com o tipo de usuário e visão atual do admin (alunos ou professores)
        if self.tipo_usuario == "aluno":
            self.colunas_atuais = ("Nome", "Nota 1", "Nota 2", "Nota 3", "Nota 4", "Média")
        elif self.tipo_usuario == "admin" and self.visao_admin == "professores":
            self.colunas_atuais = ("Nome", "Disciplina", "Excluir")
        else:
            self.colunas_atuais = ("Nome", "Nota 1", "Nota 2", "Nota 3", "Nota 4", "Média", "Excluir")

        self.tree["columns"] = self.colunas_atuais

        for coluna in self.colunas_atuais:
            if coluna == "Excluir":
                self.tree.heading(coluna, text=coluna, anchor="center")
            else:
                self.tree.heading(
                    coluna,
                    text=coluna,
                    anchor="center",
                    command=lambda c=coluna: self.ordenar_treeview(c, False),
                )
            self.tree.column(coluna, anchor="center", stretch=False)

    def ajustar_colunas_treeview(self, event=None):
        # Ajuste dinamicamente as colunas quando a janela for redimensionada
        largura_total = self.tree.winfo_width()
        if largura_total <= 1:
            return

        pesos = {
            "Nome": 4,
            "Nota 1": 1,
            "Nota 2": 1,
            "Nota 3": 1,
            "Nota 4": 1,
            "Média": 1,
            "Excluir": 0.8,
            "Disciplina": 3
        }

        total_peso = sum(pesos.get(col, 1) for col in self.colunas_atuais)

        for col in self.colunas_atuais:
            proporcao = pesos.get(col, 1) / total_peso
            largura = int(largura_total * proporcao)

            if col == "Excluir":
                largura = 80

            self.tree.column(col, width=largura, stretch=False)

    def hover_linha(self, event):
        # obtem item hover
        item = self.tree.identify_row(event.y)

        # remove hover antigo
        if hasattr(self, "_hover_item") and self._hover_item:
            tags = list(self.tree.item(self._hover_item, "tags"))
            if "hover" in tags:
                tags.remove("hover")
            self.tree.item(self._hover_item, tags=tags)

        # aplica hover novo
        if item:
            tags = list(self.tree.item(item, "tags"))
            if "hover" not in tags:
                tags.append("hover")
            self.tree.item(item, tags=tags)

        self._hover_item = item

    def alternar_visao_admin(self):
        # Alterna a visão do admin entre alunos e professores
        if self.visao_admin == "alunos":
            self.visao_admin = "professores"
            self.btn_visao.configure(text="Ver Alunos")
        else:
            self.visao_admin = "alunos"
            self.btn_visao.configure(text="Ver Professores")
        self.configurar_colunas_treeview()
        self.ajustar_colunas_treeview()
        self.atualizar_treeview()

    def obter_registros_visiveis(self):
        # Obtem os registros visiveis do treeview
        registros = []

        if self.tipo_usuario == "admin":
            if self.visao_admin == "alunos":
                lista = self.alunos_notas
                tipo = "aluno"
            else:
                lista = self.professores_com_disciplina
                tipo = "professor"
        elif self.tipo_usuario == "professor":
            lista = self.alunos_notas
            tipo = "aluno"
        else:
            lista = [a for a in self.alunos_notas if a[1] == self.usuario_logado]
            tipo = "aluno"

        for registro in lista:
            if tipo == "aluno":
                id_, nome, n1, n2, n3, n4 = registro

                media = self.calcular_media(n1, n2, n3, n4)

                registros.append((
                    id_,
                    nome,
                    self.formatar_nota(n1),
                    self.formatar_nota(n2),
                    self.formatar_nota(n3),
                    self.formatar_nota(n4),
                    media,
                    "🗑" if self.tipo_usuario in ("admin", "professor") else ""
                ))

            else:
                id_, nome, disciplina = registro

                registros.append((
                    id_,
                    nome,
                    disciplina,
                    "🗑" if self.tipo_usuario == "admin" else ""
                ))

        return registros

    def atualizar_treeview(self):
        # Limpa e preenche o treeview
        for item in self.tree.get_children():
            self.tree.delete(item)

        if self.tipo_usuario == "admin":
            titulo = "Lista de Alunos" if self.visao_admin == "alunos" else "Lista de Professores"
        elif self.tipo_usuario == "professor":
            titulo = "Lista de Alunos"
        else:
            titulo = "Minhas Notas"

        self.titulo_tabela.configure(text=titulo)

        for registro in self.obter_registros_visiveis():
            id_registro = registro[0]
            valores_visuais = registro[1:] 

            self.tree.insert("", "end", iid=id_registro, values=valores_visuais)

        self.atualizar_total()

    def ordenar_treeview(self, coluna, crescente=True):
        # Ordena o treeview de acordo com a coluna escolhida
        if coluna == "Excluir":
            return

        dados = [(self.tree.set(k, coluna), k) for k in self.tree.get_children("")]

        # Detecta número
        if "Nota" in coluna or coluna == "Média":
            def chave(valor):
                try:
                    return float(valor[0])
                except:
                    return -1
        else:
            def chave(valor):
                return valor[0].lower()

        dados.sort(key=chave, reverse=not crescente)

        for index, (_, item) in enumerate(dados):
            self.tree.move(item, "", index)

        # reset headers
        for col in self.colunas_atuais:
            if col == "Excluir":
                self.tree.heading(col, text=col, anchor="center")
            else:
                self.tree.heading(
                    col,
                    text=col,
                    anchor="center",
                    command=lambda c=col: self.ordenar_treeview(c, False)
                )

        # seta de ordem
        seta = " ▼" if crescente else " ▲"

        self.tree.heading(
            coluna,
            text=coluna + seta,
            anchor="center",
            command=lambda: self.ordenar_treeview(coluna, not crescente)
        )

    def clique_treeview(self, event):
        regiao = self.tree.identify("region", event.x, event.y)

        # impede redimensionamento das colunas ao clicar no separador entre elas
        if regiao == "separator":
            return "break"

        item_id = self.tree.identify_row(event.y)
        coluna = self.tree.identify_column(event.x)

        if not item_id:
            return

        valores = self.tree.item(item_id, "values")

        if coluna != f"#{len(self.colunas_atuais)}":
            return

        if valores[-1] != "🗑":
            return

        id_registro = int(item_id)
        nome = valores[0]

        self.excluir_registro(id_registro, nome)

    def excluir_registro(self, id_registro, nome):
        tipo = "aluno"

        if self.tipo_usuario == "admin" and self.visao_admin == "professores":
            tipo = "professor"

        confirmar = messagebox.askyesno(
            "Confirmar",
            f"Deseja excluir {nome}?",
            parent=self
        )

        if not confirmar:
            return

        excluir_usuario(id_registro, tipo)

        self.carregar_dados()
        self.atualizar_treeview()

    def filtrar_busca(self):
        termo = self.busca_entry.get().lower().strip()

        self.configurar_colunas_treeview()
        self.ajustar_colunas_treeview()

        for item in self.tree.get_children():
            self.tree.delete(item)

        for registro in self.obter_registros_visiveis():
            if any(termo in str(valor).lower() for valor in registro):

                id_registro = registro[0]
                valores_visuais = registro[1:]

                self.tree.insert("", "end", iid=id_registro, values=valores_visuais)

        self.atualizar_total()

    def editar_registro(self):
        item = self.tree.focus()

        if not item:
            messagebox.showwarning("Aviso", "Selecione um registro")
            return

        id_ = int(item)

        if self.tipo_usuario == "admin" and self.visao_admin == "professores":
            self.abrir_edicao_professor(id_)
        else:
            self.abrir_edicao_aluno(id_)

    def abrir_edicao_aluno(self, id_aluno):
        aluno = next((a for a in self.alunos_notas if a[0] == id_aluno), None)

        if not aluno:
            return

        id_, nome, n1, n2, n3, n4 = aluno

        janela = ctk.CTkToplevel(self)
        janela.title("Editar Aluno")
        largura = 420
        altura = 300
        janela.geometry(f"{largura}x{altura}")
        janela.transient(self)
        janela.grab_set()

        self.update_idletasks()
        janela.update_idletasks()
        pos_x = self.winfo_x() + (self.winfo_width() // 2) - (largura // 2)
        pos_y = self.winfo_y() + (self.winfo_height() // 2) - (altura // 2)
        janela.geometry(f"{largura}x{altura}+{pos_x}+{pos_y}")

        frame = ctk.CTkFrame(janela, fg_color="transparent")
        frame.pack(fill="both", expand=True, padx=20, pady=20)

        ctk.CTkLabel(
            frame,
            text="Editar Aluno",
            font=("Arial", 22, "bold"),
            text_color="#1e293b",
        ).pack(pady=(0, 18))

        ctk.CTkLabel(frame, text="Nome", font=("Arial", 14, "bold")).pack(anchor="w")
        entry_nome = ctk.CTkEntry(frame, width=360, height=36)
        entry_nome.insert(0, nome)
        entry_nome.pack(pady=(6, 12))

        entradas = []

        notas_frame = ctk.CTkFrame(frame, fg_color="transparent")
        notas_frame.pack(fill="x", pady=(4, 10))

        for indice, nota in enumerate([n1, n2, n3, n4], start=1):
            ctk.CTkLabel(
                notas_frame,
                text=f"Nota {indice}",
                font=("Arial", 12, "bold"),
            ).grid(row=0, column=indice - 1, padx=5, pady=(0, 5))

            e = ctk.CTkEntry(notas_frame, width=80, height=32, placeholder_text="0-10")
            e.insert(0, "" if nota is None else str(nota))
            e.grid(row=1, column=indice - 1, padx=5)
            entradas.append(e)

        def salvar():
            novo_nome = entry_nome.get().strip()

            if not novo_nome:
                messagebox.showerror("Erro", "Nome vazio")
                return

            notas = []

            for e in entradas:
                valor = e.get().strip()

                if valor == "":
                    notas.append(None)
                    continue

                try:
                    n = float(valor)
                except:
                    messagebox.showerror("Erro", "Notas inválidas")
                    return

                if n < 0 or n > 10:
                    messagebox.showerror("Erro", "Notas entre 0 e 10")
                    return

                notas.append(n)

            atualizar_aluno(id_aluno, novo_nome, notas[0], notas[1], notas[2], notas[3])

            self.carregar_dados()
            self.atualizar_treeview()
            janela.destroy()

        botoes = ctk.CTkFrame(frame, fg_color="transparent")
        botoes.pack(pady=(10, 0))

        btn_salvar = ctk.CTkButton(botoes, text="Salvar", fg_color="#0f172a", command=salvar)
        btn_salvar.pack(side="left", padx=(0, 8), pady=(10, 0))
        btn_cancelar = ctk.CTkButton(
            botoes,
            text="Cancelar",
            fg_color="#991b1b",
            command=janela.destroy,
        )
        btn_cancelar.pack(side="left", pady=(10, 0))

    def abrir_edicao_professor(self, id_prof):
        prof = next((p for p in self.professores_com_disciplina if p[0] == id_prof), None)

        if not prof:
            return

        id_, nome, disciplina = prof

        janela = ctk.CTkToplevel(self)
        janela.title("Editar Professor")
        largura = 420
        altura = 300
        janela.geometry(f"{largura}x{altura}")
        janela.transient(self)
        janela.grab_set()

        self.update_idletasks()
        janela.update_idletasks()
        pos_x = self.winfo_x() + (self.winfo_width() // 2) - (largura // 2)
        pos_y = self.winfo_y() + (self.winfo_height() // 2) - (altura // 2)
        janela.geometry(f"{largura}x{altura}+{pos_x}+{pos_y}")

        frame = ctk.CTkFrame(janela, fg_color="transparent")
        frame.pack(fill="both", expand=True, padx=20, pady=20)

        ctk.CTkLabel(
            frame,
            text="Editar Professor",
            font=("Arial", 22, "bold"),
            text_color="#1e293b",
        ).pack(pady=(0, 18))

        ctk.CTkLabel(frame, text="Nome", font=("Arial", 14, "bold")).pack(anchor="w")
        entry_nome = ctk.CTkEntry(frame, width=360, height=36)
        entry_nome.insert(0, nome)
        entry_nome.pack(pady=(6, 12))

        ctk.CTkLabel(frame, text="Disciplina", font=("Arial", 14, "bold")).pack(anchor="w")
        entry_disciplina = ctk.CTkEntry(frame, width=360, height=36)
        entry_disciplina.insert(0, disciplina)
        entry_disciplina.pack(pady=(6, 12))

        def salvar():
            novo_nome = entry_nome.get().strip()
            nova_disciplina = entry_disciplina.get().strip()

            if not novo_nome or not nova_disciplina:
                messagebox.showerror("Erro", "Preencha tudo")
                return

            atualizar_professor(id_prof, novo_nome, nova_disciplina)

            self.carregar_dados()
            self.atualizar_treeview()
            janela.destroy()

        botoes = ctk.CTkFrame(frame, fg_color="transparent")
        botoes.pack(pady=(10, 0))

        btn_salvar = ctk.CTkButton(botoes, text="Salvar", fg_color="#0f172a", command=salvar)
        btn_salvar.pack(side="left", padx=(0, 8), pady=(10, 0))
        btn_cancelar = ctk.CTkButton(
            botoes,
            text="Cancelar",
            fg_color="#991b1b",
            command=janela.destroy,
        )
        btn_cancelar.pack(side="left", pady=(10, 0))

#-------------------------- Footer e Funções de exportação --------------------------

    def criar_footer(self):
        footer = ctk.CTkFrame(self.container, fg_color="transparent")
        footer.pack(fill="x", padx=20, pady=10)

        # linha de topo do footer para total e legenda
        linha_top = ctk.CTkFrame(footer, fg_color="transparent")
        linha_top.pack(fill="x")

        badge_total = ctk.CTkFrame(
            linha_top,
            corner_radius=14,
            fg_color="#e2e8f0",
            border_width=1,
            border_color="#cbd5e1"
        )
        badge_total.pack(side="left")

        self.total_label = ctk.CTkLabel(
            badge_total,
            text="Total: 0",
            font=("Arial", 14),
            text_color="#334155"
        )
        self.total_label.pack(padx=10, pady=4)

        # linha de botoes do footer
        linha_botoes = ctk.CTkFrame(footer, fg_color="transparent")
        linha_botoes.pack(fill="x", pady=(10, 0))

        botoes_container = ctk.CTkFrame(linha_botoes, fg_color="transparent")
        botoes_container.pack(anchor="e")

        btn_excel = ctk.CTkButton(
            botoes_container,
            text="Exportar Excel",
            width=140,
            fg_color="#0f172a",
            text_color="#ffffff",
            command=self.exportar_excel
        )
        btn_excel.pack(side="left", padx=5)

        btn_pdf = ctk.CTkButton(
            botoes_container,
            text="Exportar PDF",
            width=140,
            fg_color="#0f172a",
            text_color="#ffffff",
            command=self.exportar_pdf
        )
        btn_pdf.pack(side="left", padx=5)

        self.atualizar_total()

    def exportar_excel(self):
        dados = self.obter_registros_visiveis()
        colunas = self.colunas_atuais

        caminho = filedialog.asksaveasfilename(
            initialfile="SistemaEscolarExcel.xlsx",
            defaultextension=".xlsx",
            filetypes=[("Arquivo Excel", "*.xlsx")],
            initialdir=self.ultima_pasta or "",
            title="Salvar Excel"
        )

        if not caminho:
            return

        self.ultima_pasta = Path(caminho).parent

        exportar_excel(dados, colunas, caminho)
        
    def exportar_pdf(self):
        dados = self.obter_registros_visiveis()
        colunas = list(self.colunas_atuais)

        caminho = filedialog.asksaveasfilename(
            initialfile="SistemaEscolarPDF.pdf",
            defaultextension=".pdf",
            filetypes=[("Arquivo PDF", "*.pdf")],
            initialdir=self.ultima_pasta or "",
            title="Salvar PDF"
        )

        if not caminho:
            return

        self.ultima_pasta = Path(caminho).parent

        exportar_pdf(dados, colunas, caminho)

    def atualizar_total(self):
        if not hasattr(self, "total_label"):
            return

        total = len(self.tree.get_children()) if hasattr(self, "tree") else 0
        self.total_label.configure(text=f"Total de registros: {total}")

if __name__ == "__main__":
    login = LoginWindow()
    login.mainloop()