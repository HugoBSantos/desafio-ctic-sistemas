import streamlit as st
import pandas as pd
import plotly.express as px
from pathlib import Path

FILE_PATH = Path().cwd() / "data" / "BASE_TESTE_HUGO1.csv"

def matriculados_por_disciplina(df: pd.DataFrame) -> pd.DataFrame:
    df_matriculados = df[df["SIT_DISCIPLINA"] == "CURSANDO"]
    cols = ["CODIGO_DISCIPLINA", "DISCIPLINA", "NOME_ABREV_ALUNO"]
    return df_matriculados[cols].sort_values(by="DISCIPLINA")

if __name__ == "__main__":
    st.header("📊 Dados dos alunos da EC5MA")
    df_alunos = pd.read_csv(Path(FILE_PATH), encoding="latin1", sep="\t")
    
    st.markdown("### Alunos matriculados por disciplina")
    
    st.write(matriculados_por_disciplina(df_alunos))