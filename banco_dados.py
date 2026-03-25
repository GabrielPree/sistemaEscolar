import sqlite3 as conector
import bcrypt

def executar_bd():
    try:
        # Abertura de conexão e aquisição de cursor
        caminho_banco = "escolaBD.db"
        conexao = conector.connect(caminho_banco)
        cursor = conexao.cursor()

        admin = '''CREATE TABLE IF NOT EXISTS admin (
                        id INTEGER PRIMARY KEY,      
                        nome TEXT NOT NULL,
                        senha TEXT NOT NULL
                        );'''
        cursor.execute(admin)
        cursor.execute("SELECT 1 FROM admin WHERE nome = 'admin' LIMIT 1")
        admin_existe = cursor.fetchone()
        if not admin_existe:
            # Hash da senha antes de armazenar e criação do admin padrão
            # troquei a senha para 'admin' para facilitar os testes, mas é recomendado usar uma senha mais forte
            senha_hash = bcrypt.hashpw('admin'.encode(), bcrypt.gensalt()).decode()
            criar_admin = '''INSERT INTO admin (nome, senha) VALUES ('admin', ?)'''
            cursor.execute(criar_admin, (senha_hash,))

        # Criação das tabelas
        comando = '''CREATE TABLE IF NOT EXISTS professor (
                        id INTEGER PRIMARY KEY,      
                        nome TEXT NOT NULL,
                        disciplina TEXT NOT NULL,
                        senha TEXT NOT NULL
                        );'''

        cursor.execute(comando)

        comando2 = '''CREATE TABLE IF NOT EXISTS aluno (
                        id INTEGER PRIMARY KEY,      
                        nome TEXT NOT NULL,
                        senha TEXT NOT NULL,
                        nota1 REAL,
                        nota2 REAL,
                        nota3 REAL,
                        nota4 REAL
                        );'''
        
        cursor.execute(comando2)
        conexao.commit()

    finally:
        if conexao:
            cursor.close()
            conexao.close()

def inserir_usuario(nome, disciplina, senha, tipo):
    try:
        caminho_banco = "escolaBD.db"
        conexao = conector.connect(caminho_banco)
        cursor = conexao.cursor()
        senha_hash = bcrypt.hashpw(senha.encode(), bcrypt.gensalt()).decode()

        if tipo == "professor":
            comando = '''INSERT INTO professor (nome, disciplina, senha) VALUES (?, ?, ?)'''
        else:
            comando = '''INSERT INTO aluno (nome, senha) VALUES (?, ?)'''

        cursor.execute(comando, (nome, disciplina, senha_hash) if tipo == "professor" else (nome, senha_hash))
        conexao.commit()
        novo_id = cursor.lastrowid
        return novo_id

    except conector.DatabaseError as err:
        print("Erro de banco de dados", err)
        return None

    finally:
        if conexao:
            cursor.close()
            conexao.close()

def atualizar_notas(id, nota1, nota2, nota3, nota4):
    try:
        caminho_banco = "escolaBD.db"
        conexao = conector.connect(caminho_banco)
        cursor = conexao.cursor()

        comando = '''
            UPDATE aluno
            SET nota1 = ?, nota2 = ?, nota3 = ?, nota4 = ?
            WHERE id = ?
        '''
        cursor.execute(comando, (nota1, nota2, nota3, nota4, id))
        conexao.commit()
        return cursor.rowcount > 0

    except conector.DatabaseError as err:
        print("Erro de banco de dados", err)
        return False

    finally:
        if conexao:
            cursor.close()
            conexao.close()

def excluir_usuario(id, tipo):
    try:
        caminho_banco = "escolaBD.db"
        conexao = conector.connect(caminho_banco)
        cursor = conexao.cursor()

        if tipo == "professor":
            comando = '''DELETE FROM professor WHERE id = ?'''
        else:
            comando = '''DELETE FROM aluno WHERE id = ?'''

        cursor.execute(comando, (id,))
        conexao.commit()

    except conector.DatabaseError as err:
        print("Erro de banco de dados", err)

    finally:
        if conexao:
            cursor.close()
            conexao.close()

def _verificar_senha(senha_digitada, senha_armazenada):
    if senha_armazenada is None:
        return False
    try:
        return bcrypt.checkpw(senha_digitada.encode(), senha_armazenada.encode())
    except ValueError:
        return False

def validar_usuario(nome, senha):
    try:
        caminho_banco = "escolaBD.db"
        conexao = conector.connect(caminho_banco)
        cursor = conexao.cursor()

        comando_admin = '''SELECT senha FROM admin WHERE nome = ?'''
        cursor.execute(comando_admin, (nome,))
        admins = cursor.fetchall()
        if any(_verificar_senha(senha, admin[0]) for admin in admins):
            return "admin"

        comando_professor = '''SELECT senha FROM professor WHERE nome = ?'''
        cursor.execute(comando_professor, (nome,))
        professores = cursor.fetchall()
        if any(_verificar_senha(senha, professor[0]) for professor in professores):
            return "professor"

        comando_aluno = '''SELECT senha FROM aluno WHERE nome = ?'''
        cursor.execute(comando_aluno, (nome,))
        alunos = cursor.fetchall()
        if any(_verificar_senha(senha, aluno[0]) for aluno in alunos):
            return "aluno"

        return None

    except conector.DatabaseError as err:
        print("Erro de banco de dados", err)

    finally:
        if conexao:
            cursor.close()
            conexao.close()

def listar_professores():
    try:
        caminho_banco = "escolaBD.db"
        conexao = conector.connect(caminho_banco)
        cursor = conexao.cursor()

        comando = '''SELECT id, nome, disciplina FROM professor'''
        cursor.execute(comando)
        return cursor.fetchall()

    except conector.DatabaseError as err:
        print("Erro de banco de dados", err)
        return []

    finally:
        if conexao:
            cursor.close()
            conexao.close()

def listar_alunos():
    try:
        caminho_banco = "escolaBD.db"
        conexao = conector.connect(caminho_banco)
        cursor = conexao.cursor()

        comando = '''SELECT id, nome, nota1, nota2, nota3, nota4 FROM aluno'''
        cursor.execute(comando)
        return cursor.fetchall()

    except conector.DatabaseError as err:
        print("Erro de banco de dados", err)
        return []

    finally:
        if conexao:
            cursor.close()
            conexao.close()

def buscar_aluno(id):
    try:
        caminho_banco = "escolaBD.db"
        conexao = conector.connect(caminho_banco)
        cursor = conexao.cursor()

        comando = '''SELECT id, nome, nota1, nota2, nota3, nota4 FROM aluno WHERE id = ?'''
        cursor.execute(comando, (id,))
        return cursor.fetchone()

    except conector.DatabaseError as err:
        print("Erro de banco de dados", err)
        return None

    finally:
        if conexao:
            cursor.close()
            conexao.close()

def atualizar_aluno(id, nome, n1, n2, n3, n4):
    conexao = conector.connect("escolaBD.db")
    cursor = conexao.cursor()

    cursor.execute("""
        UPDATE aluno
        SET nome=?, nota1=?, nota2=?, nota3=?, nota4=?
        WHERE id=?
    """, (nome, n1, n2, n3, n4, id))

    conexao.commit()
    cursor.close()
    conexao.close()

def atualizar_professor(id, nome, disciplina):
    conexao = conector.connect("escolaBD.db")
    cursor = conexao.cursor()

    cursor.execute("""
        UPDATE professor
        SET nome=?, disciplina=?
        WHERE id=?
    """, (nome, disciplina, id))

    conexao.commit()
    cursor.close()
    conexao.close()