import re
import time

import pandas as pd
import streamlit as st

from cognitive import *

st.set_page_config(layout="wide")

hide_streamlit_style = """
            <style>
            #MainMenu {visibility: hidden;}
            footer {visibility: hidden;}
            </style>
            """
st.markdown(hide_streamlit_style, unsafe_allow_html=True)

hide_footer_style = """
    <style>
    .reportview-container .main footer {visibility: hidden;}    
    """
st.markdown(hide_footer_style, unsafe_allow_html=True)


def get_df(file):
    extension = file.name.split('.')[1]
    if extension.upper() == 'CSV':
        df = pd.read_csv(file)
    elif extension.upper() == 'XLSX':
        df = pd.read_excel(file, engine='openpyxl')
    elif extension.upper() == 'TXT':
        df = pd.read_csv(file, sep=" ", header=None)
    else:
        return pd.DataFrame([])
    return df


def run_iteration(df, q, t, i, to_header, to_columns, to_impulse):
    a = df.to_numpy()
    to_remove = '[]'
    to_header.subheader(f'Ітерація {i}')
    cognitive_model = CognitiveModel(a)
    calculate_eigenvalues = cognitive_model.calculate_eigenvalues()
    get_spectral_radius = cognitive_model.get_spectral_radius(cognitive_model.adjacency_matrix)
    check_perturbation_stability = cognitive_model.check_perturbation_stability()
    check_numerical_stability = cognitive_model.check_numerical_stability()
    check_structural_stability = cognitive_model.check_structural_stability()

    col1, col2, col3 = to_columns.columns(3)

    col1.subheader('Власні числа')
    for x in calculate_eigenvalues:
        col1.write(str(x))
    col1.write(f'**Максимум:** {get_spectral_radius}')

    col2.subheader('Властивості')
    col2.write(f'**Стійкість за збуренням:** {"Так" if check_perturbation_stability else "Ні"}')
    col2.write(f'**Стійкість за значенням:** {"Так" if check_numerical_stability else "Ні"}')
    col2.write(f'**Структурна стійкість:** {"Так" if not check_structural_stability else "Ні"}')

    col3.subheader('Отримані цикли')
    res = [f'[{cycle_str(x)}]' for x in check_structural_stability][::-1]
    col3.dataframe(res)
    if len(res):
        col3.write(f'**Рекомендовано для видалення:** {res[0]}')
        to_remove = res[0]  # to_select.selectbox("Виберіть для видалення", res, 0, key=i)
    else:
        col3.write(f'**Видаляти нічого**')

    fig_col1, fig_col2 = to_impulse.columns(2)

    fig1 = cognitive_model.impulse_model(t=t, q=q)
    fig_col1.pyplot(fig1)

    fig2 = cognitive_model.draw_graph()
    fig_col2.pyplot(fig2)

    return list(map(int, re.findall(r'\d+', to_remove))), fig1, fig2


def main():
    st.header('Налаштування')
    st.info("Завантажте матрицю")
    uploaded_file = st.file_uploader("Завантажити матрицю")
    if uploaded_file is not None:
        df = get_df(uploaded_file)
        q_input = st.text_input("Ввести вектор імпульсу (через пробіл)", ' '.join(['0'] * len(df)))
        if len(q_input.split()) == len(df):
            t = st.number_input("Ввести T", min_value=0, value=5)
            go = st.button('Виконати')
            if go:

                step = 0

                q = np.array(list(map(float, q_input.split())))
                df.columns = range(len(df))
                df.index = range(len(df))

                to_header = st.empty()
                to_table = st.empty()
                to_columns = st.empty()
                to_impulse = st.empty()

                to_table.table(df)
                st.subheader("Видалені зв'язки")

                while True:
                    to_remove, fig1, fig2 = run_iteration(df, q, t, step, to_header, to_columns,
                                              to_impulse)
                    for i in range(len(to_remove) - 1):
                        df.iloc[to_remove[i], to_remove[i + 1]] = 0

                    to_table.table(df)
                    st.write(f"**Ітерація** {step}: {' - '.join([str(x) for x in to_remove])}")
                    time.sleep(1.5)
                    step += 1

                    if not len(to_remove):
                        break

                time.sleep(5)
                plt.close(fig1)
                plt.close(fig2)
        else:
            st.error('Введено вектор неправильної розмірності')


if __name__ == "__main__":
    main()
