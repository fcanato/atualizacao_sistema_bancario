import streamlit as st
import pandas as pd
import sqlite3
import io

# Função para criar a conexão com o banco de dados
def criar_conexao():
    conn = sqlite3.connect("pendencias.db")
    return conn

# Função para criar a tabela no banco de dados
def criar_tabelas():
    conn = criar_conexao()
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS pendencias (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            codigo TEXT,
            codigo_origem TEXT,
            estoque_fisico_origem INTEGER,
            codigo_destino TEXT,
            estoque_fisico_destino INTEGER,
            cidade_origem TEXT,
            cidade_destino TEXT,
            sigla_origem TEXT,
            sigla_destino TEXT,
            codigo_produto TEXT,
            descricao_produto TEXT,
            qtde_produto INTEGER,
            status TEXT,
            dia DATE,
            size INTEGER,
            situacao TEXT
        )
    ''')
    conn.commit()
    conn.close()

# Função para atualizar o banco de dados com os dados da planilha
def atualizar_banco_de_dados(df):
    conn = criar_conexao()
    c = conn.cursor()
    for _, row in df.iterrows():
        c.execute('''
            INSERT INTO pendencias (
                codigo, codigo_origem, estoque_fisico_origem, codigo_destino, estoque_fisico_destino,
                cidade_origem, cidade_destino, sigla_origem, sigla_destino, codigo_produto,
                descricao_produto, qtde_produto, status, dia, size, situacao
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            row['codigo'], row['codigo_origem'], row['estoque_fisico_origem'], row['codigo_destino'],
            row['estoque_fisico_destino'], row['cidade_origem'], row['cidade_destino'],
            row['sigla_origem'], row['sigla_destino'], row['codigo_produto'],
            row['descricao_produto'], row['qtde_produto'], row['status'], row['dia'],
            row['size'], row.get('situacao', '')
        ))
    conn.commit()
    conn.close()

# Função para exibir os dados com edição de situação
def exibir_dados(df):
    st.markdown("### Situação dos Documentos")

    # Filtros
    col1, col2 = st.columns(2)
    with col1:
        cidade_origem = st.selectbox("Filtrar por Cidade de Origem", options=['Todos'] + sorted(df['cidade_origem'].dropna().unique().tolist()))
    with col2:
        cidade_destino = st.selectbox("Filtrar por Cidade de Destino", options=['Todos'] + sorted(df['cidade_destino'].dropna().unique().tolist()))

    df_filtrado = df.copy()
    if cidade_origem != 'Todos':
        df_filtrado = df_filtrado[df_filtrado['cidade_origem'] == cidade_origem]
    if cidade_destino != 'Todos':
        df_filtrado = df_filtrado[df_filtrado['cidade_destino'] == cidade_destino]

    # Edição de dados
    colunas_editar = ['id', 'codigo', 'descricao_produto', 'situacao']
    conn = criar_conexao()
    df_banco = pd.read_sql_query("SELECT * FROM pendencias", conn)
    conn.close()

    df_merge = pd.merge(df_filtrado, df_banco[['id', 'codigo', 'situacao']], on='codigo', how='left')
    df_merge['situacao'] = df_merge['situacao'].fillna('')

    st.markdown("**Edite diretamente a situação dos documentos na tabela abaixo:**")

    for index, row in df_merge.iterrows():
        situacao = st.selectbox(f"Situação para {row['descricao_produto']}", options=["", "Pendente", "Concluído", "Em Progresso"], index=["", "Pendente", "Concluído", "Em Progresso"].index(row['situacao']) if row['situacao'] in ["", "Pendente", "Concluído", "Em Progresso"] else 0, key=row['codigo'])
        df_merge.at[index, 'situacao'] = situacao

    if st.button("💾 Salvar Situações Atualizadas"):
        conn = criar_conexao()
        c = conn.cursor()
        for _, row in df_merge.iterrows():
            c.execute("UPDATE pendencias SET situacao = ? WHERE codigo = ?", (row['situacao'], row['codigo']))
        conn.commit()
        conn.close()
        st.success("Situações atualizadas com sucesso!")

    return df_merge

# Função para exportar os dados em Excel
def exportar_planilha(df):
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        df.to_excel(writer, index=False)
    processed_data = output.getvalue()

    st.download_button(
        label="📥 Baixar planilha com Status Atualizados",
        data=processed_data,
        file_name="pendencias_atualizadas.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )

# Função principal
def main():
    st.title("📌 Gerenciamento de Pendências Diárias")

    criar_tabelas()

    uploaded_file = st.file_uploader("📤 Carregue a planilha Excel", type=["xlsx"])

    if uploaded_file:
        try:
            df = pd.read_excel(uploaded_file)

            # Padroniza nomes de colunas
            df.columns = [col.strip().lower().replace(" ", "_") for col in df.columns]

            if 'situacao' not in df.columns:
                df['situacao'] = ''

            atualizar_banco_de_dados(df)
            st.success("Dados carregados e banco de dados atualizado!")

            # Exibir e editar os dados
            df_editado = exibir_dados(df)

            # Exportar
            exportar_planilha(df_editado)

        except Exception as e:
            st.error(f"Erro ao processar o arquivo: {e}")

# Executar
if __name__ == "__main__":
    main()
