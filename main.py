import streamlit as st
import pandas as pd
import plotly.express as px
from pathlib import Path
from fpdf import FPDF
import io

st.set_page_config(
    page_title="Desafio do CTIC Sistemas",
    page_icon="📊",
    layout="wide"
)

FILE_PATH = Path().cwd() / "data" / "BASE_TESTE_HUGO1.csv"

def alunos_por_disciplina(df: pd.DataFrame, sit_disciplina: str) -> pd.DataFrame:
    df_alunos = df[df["SIT_DISCIPLINA"] == sit_disciplina.upper()]
    cols = ["CODIGO_DISCIPLINA", "DISCIPLINA", "NOME_ABREV_ALUNO"]
    return df_alunos[cols].sort_values(by=["DISCIPLINA", "NOME_ABREV_ALUNO"])

def filtrar_df(df: pd.DataFrame, coluna: str, valores: list) -> pd.DataFrame:
    if not valores:
        return df
    return df[df[coluna].isin(valores)]

def exportar_excel(df: pd.DataFrame) -> bytes:
    buffer = io.BytesIO()
    with pd.ExcelWriter(buffer, engine="openpyxl") as writer:
        df.to_excel(writer, index=False, sheet_name="EC5MA")
    return buffer.getvalue()

def exportar_pdf(df: pd.DataFrame) -> bytes:
    pdf = FPDF()
    pdf.add_page()
    pdf.set_auto_page_break(auto=True, margin=10)

    col_widths = {
        "CODIGO_DISCIPLINA": 30,
        "DISCIPLINA": 120,
        "NOME_ABREV_ALUNO": 40,
    }
    # Fallback: divide igualmente para colunas não mapeadas
    default_width = pdf.epw / len(df.columns)
    widths = [col_widths.get(col, default_width) for col in df.columns]

    # Cabeçalho
    pdf.set_font("Helvetica", style="B", size=8)
    for col, width in zip(df.columns, widths):
        pdf.cell(width, 6, str(col), border=1)
    pdf.ln()

    # Linhas
    pdf.set_font("Helvetica", size=8)
    for _, row in df.iterrows():
        for val, width in zip(row, widths):
            pdf.cell(width, 6, str(val), border=1)
        pdf.ln()

    return bytes(pdf.output())

def lista_alunos(df: pd.DataFrame, sit_disciplina: str):
    df_filtrado = alunos_por_disciplina(df, sit_disciplina=sit_disciplina)
    
    st.dataframe(df_filtrado)
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.download_button(
            label="⬇️ Exportar Excel",
            data=exportar_excel(df_filtrado),
            file_name=f"{sit_disciplina}.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            key=f"excel_{sit_disciplina}"
        )
    with col2:
        st.download_button(
            label="⬇️ Exportar PDF",
            data=exportar_pdf(df_filtrado),
            file_name=f"{sit_disciplina}.pdf",
            mime="application/pdf",
            key=f"pdf_{sit_disciplina}"
        )
    
if __name__ == "__main__":
    st.title("📊 Dados dos alunos da EC5MA")
    df_alunos = pd.read_csv(Path(FILE_PATH), encoding="latin1", sep="\t")
    
    disciplinas = {
        codigo: disciplina
        for codigo, disciplina in zip(
            df_alunos["CODIGO_DISCIPLINA"], df_alunos["DISCIPLINA"]
        )
    }
    
    filtro_codigo = st.sidebar.multiselect(
        "Filtrar por código da disciplina",
        disciplinas.keys()
    )
    
    filtro_disciplina = st.sidebar.multiselect(
        "Filtrar por nome da disciplina",
        disciplinas.values()
    )
    
    df_filtrado = filtrar_df(df_alunos, "CODIGO_DISCIPLINA", filtro_codigo)
    df_filtrado = filtrar_df(df_filtrado, "DISCIPLINA", filtro_disciplina)
    
    tab1, tab2 = st.tabs(["Tabelas", "Gráficos"])
    
    with tab1:
        st.header("Lista de alunos por disciplina")
        matriculados, em_ajuste = st.tabs(["Matriculados", "Em ajuste"])
        
        with matriculados:
            st.markdown("##### Alunos matriculados por disciplina")
            lista_alunos(
                df=df_filtrado,
                sit_disciplina="cursando"
            )
        with em_ajuste:
            st.markdown("##### Alunos em situação de ajuste por disciplina")
            lista_alunos(
                df=df_filtrado,
                sit_disciplina="ajuste"
            )
        st.divider()
        
        st.header("Grade curricular de cada aluno")
        
        cols_disciplinas = ["CODIGO_DISCIPLINA", "DISCIPLINA", "SIT_DISCIPLINA"]
        grade_aluno = st.selectbox(
            "Selecione o aluno:",
            df_filtrado["NOME_ABREV_ALUNO"].unique()
        )
        
        st.write(f"Exibindo a grade curricular do(a) aluno(a) {grade_aluno}:")
        st.dataframe(df_filtrado[df_filtrado["NOME_ABREV_ALUNO"] == grade_aluno][cols_disciplinas]
                    .sort_values(by="SIT_DISCIPLINA", ascending=False))
    
    with tab2:
        # TOTAL DE ALUNOS POR DISCIPLINA
        df_alunos_disciplina = (
            df_filtrado.groupby("DISCIPLINA")["NOME_ABREV_ALUNO"]
            .count()
            .reset_index()
            .rename(columns={"NOME_ABREV_ALUNO": "TOTAL"})
            .sort_values(by="TOTAL")
        )
        
        fig_alunos_disciplina = px.bar(
            df_alunos_disciplina, x="TOTAL", y="DISCIPLINA",
            orientation="h", text="TOTAL", title="Total de alunos por disciplina",
            labels={"TOTAL": "Quantidade de alunos", "DISCIPLINA": "Disciplina"}
        )
        st.plotly_chart(fig_alunos_disciplina, use_container_width=True)
        
        # DISCIPLINAS COM MAIS AJUSTES
        df_disciplinas_ajustes = (
            df_filtrado[df_filtrado["SIT_DISCIPLINA"] == "AJUSTE"]
            .groupby("DISCIPLINA")["NOME_ABREV_ALUNO"]
            .count()
            .reset_index()
            .rename(columns={"NOME_ABREV_ALUNO": "TOTAL"})
            .sort_values(by="TOTAL")
        )
        
        fig_disciplinas_ajustes = px.bar(
            df_disciplinas_ajustes, x="TOTAL", y="DISCIPLINA",
            orientation="h", text="TOTAL", title="Disciplinas com mais ajustes",
            labels={"TOTAL": "Quantidade de alunos", "DISCIPLINA": "Disciplina"}
        )
        st.plotly_chart(fig_disciplinas_ajustes, use_container_width=True)

        # % DE ALUNOS EM AJUSTE POR CURSO

        # RANKING DE DISCIPLINAS

        # PERCENTUAL DE AJUSTE