import streamlit as st
import pandas as pd
import plotly.express as px
from pathlib import Path

FILE_PATH = Path().cwd() / "data" / "BASE_TESTE_HUGO1.csv"

def alunos_por_disciplina(df: pd.DataFrame, sit_disciplina: str) -> pd.DataFrame:
    df_alunos = df[df["SIT_DISCIPLINA"] == sit_disciplina.upper()]
    cols = ["CODIGO_DISCIPLINA", "DISCIPLINA", "NOME_ABREV_ALUNO"]
    return df_matriculados[cols].sort_values(by="DISCIPLINA")

if __name__ == "__main__":
    st.header("📊 Dados dos alunos da EC5MA")
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
    
    st.markdown("### Lista de alunos por disciplina")
    matriculados, em_ajuste = st.tabs(["Matriculados", "Em ajuste"])
    
    with matriculados:
        st.markdown("#### Alunos matriculados por disciplina")

        df_filtrado = alunos_por_disciplina(df_alunos, sit_disciplina="cursando")
        df_filtrado = filtrar_df(df_filtrado, "CODIGO_DISCIPLINA", filtro_codigo)
        df_filtrado = filtrar_df(df_filtrado, "DISCIPLINA", filtro_disciplina)
        
        st.dataframe(df_filtrado)
    with em_ajuste:
        st.markdown("#### Alunos em situação de ajuste por disciplina")

        df_filtrado = alunos_por_disciplina(df_alunos, sit_disciplina="ajuste")
        df_filtrado = filtrar_df(df_filtrado, "CODIGO_DISCIPLINA", filtro_codigo)
        df_filtrado = filtrar_df(df_filtrado, "DISCIPLINA", filtro_disciplina)
        
        st.dataframe(df_filtrado)