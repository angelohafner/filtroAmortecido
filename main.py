import streamlit as st
import numpy as np
import pandas as pd
import json
import os
from matplotlib.ticker import EngFormatter
import chardet


# Arquivo base para download
PARAMETERS_FILE = "parameters.txt"

# Função para criar o arquivo de parâmetros padrão
def create_default_parameters():
    with open(PARAMETERS_FILE, "w") as file:
        file.write(
            """# Frequência fundamental em Hz
f1 = 60

# Resistência em ohms do resistor principal
R = 222

# Resistência em ohms do indutor
r = 0.792

# Indutância do indutor em miliHenries (mH)
L_mH = 34.303

# Capacitância do capacitor em microFarads (uF)
C_uF = 8.543

# Tensão de linha em kV (quilovolts)
V_line_kV = 34.5

# Sobretensão permitida nos capacitores (fator de multiplicação)
capacitor_overvoltage = 1.3

# Sobrecorrente permitida no indutor (fator de multiplicação)
inductor_overcurrent = 1.66

# Sobrecorrente permitida no resistor (fator de multiplicação)
resistor_overcurrent = 1.66

# Número de capacitores em série
series_cap_count = 2

# Número de capacitores em paralelo
parallel_cap_count = 2
"""
        )

# Função para carregar os parâmetros de um arquivo texto ou binário
def load_parameters(uploaded_file):
    parameters = {}

    # Detectar a codificação do arquivo
    raw_data = uploaded_file.read()
    result = chardet.detect(raw_data)
    encoding = result['encoding']

    # Ler o arquivo usando a codificação detectada
    file_content = raw_data.decode(encoding).splitlines()

    for line in file_content:
        if line.strip() and not line.startswith("#"):
            key, value = line.split("=")
            key = key.strip()
            value = value.strip()
            parameters[key] = float(value) if '.' in value else int(value)
    return parameters

# Função para salvar os resultados em TXT, JSON e XLSX
def save_results_as_files(results, folder_name="results"):
    os.makedirs(folder_name, exist_ok=True)
    txt_file = f"{folder_name}/results.txt"
    json_file = f"{folder_name}/results.json"
    xlsx_file = f"{folder_name}/results.xlsx"

    # Salvar em TXT
    with open(txt_file, "w", encoding="utf-8") as file:
        for section, data in results.items():
            file.write(f"==== {section} ====\n")
            for parameter, value in data.items():
                file.write(f"{parameter}: {value}\n")
            file.write("\n")

    # Salvar em JSON
    with open(json_file, "w") as file:
        json.dump(results, file, indent=4)

    # Salvar em XLSX
    with pd.ExcelWriter(xlsx_file) as writer:
        for section, data in results.items():
            df = pd.DataFrame(data.items(), columns=["Parameter", "Value"])
            df.to_excel(writer, sheet_name=section, index=False)

    return txt_file, json_file, xlsx_file

# Função principal para calcular o filtro amortecido
def damped_filter_calculation(
        f1, R, r, L_mH, C_uF, V_line_kV,
        capacitor_overvoltage, inductor_overcurrent,
        resistor_overcurrent, series_cap_count, parallel_cap_count
):
    # Frequência angular
    w1 = 2 * np.pi * f1

    # Função para calcular a frequência de ressonância
    def resonance_frequency(L_mH, C_uF):
        L_h = L_mH * 1e-3
        C_f = C_uF * 1e-6
        return 1 / (2 * np.pi * np.sqrt(L_h * C_f))

    # Função para calcular a impedância amortecida
    def calculate_impedance_damped(R, r, L_mH, C_uF, w):
        Z_R = complex(R, 0)
        Z_L = complex(r, w * L_mH * 1e-3)
        Z_C = complex(0, -1 / (w * C_uF * 1e-6))
        Z_RL = 1 / (1 / Z_R + 1 / Z_L)
        Z_F = Z_RL + Z_C
        return Z_R, Z_L, Z_C, Z_RL, Z_F

    # Função para calcular corrente e tensão em cada elemento
    def calculate_current_voltage(V_line_kV, Z_R, Z_L, Z_C, Z_RL, Z_F):
        V_phase = V_line_kV * 1e3 / np.sqrt(3)
        I_F = V_phase / Z_F
        V_R, V_L, V_C = I_F * Z_RL, I_F * Z_RL, I_F * Z_C
        I_R, I_L, I_C = V_R / Z_R, V_L / Z_L, V_C / Z_C
        return I_R, I_L, I_C, I_F, V_R, V_L, V_C

    # Função para calcular a potência
    def calculate_power(I_R, I_L, I_C, I_F, V_R, V_L, V_C):
        P_R = V_R * np.conj(I_R)
        P_L = V_L * np.conj(I_L)
        P_C = V_C * np.conj(I_C)
        P_F = (V_R + V_C) * np.conj(I_F)
        return P_R, P_L, P_C, P_F

    # Função para calcular detalhes das células capacitivas
    def capacitor_cells(series_cap_count, parallel_cap_count, V_C, P_C, capacitor_overvoltage):
        total_cap_count = 3 * series_cap_count * parallel_cap_count
        nominal_cell_voltage = np.abs(V_C) * capacitor_overvoltage / series_cap_count
        nominal_cell_power = 3 * np.abs(P_C) * capacitor_overvoltage ** 2 / total_cap_count
        nominal_cell_capacitance = 1 / (w1 * nominal_cell_voltage ** 2 / nominal_cell_power)
        association_capacitance = nominal_cell_capacitance * parallel_cap_count / series_cap_count
        return total_cap_count, nominal_cell_voltage, nominal_cell_power, nominal_cell_capacitance, association_capacitance

    # Calcular corrente de curto-circuito para o indutor
    def short_circuit_current(V_line_kV, L_mH, f1):
        inductance = L_mH * 1e-3
        line_voltage = V_line_kV * 1e3
        X_L = 2 * np.pi * f1 * inductance
        return (line_voltage / np.sqrt(3)) / X_L

    # Formatador de resultados
    formatter = EngFormatter(unit='')
    def format_with_unit(value, unit):
        return f"{formatter.format_eng(value)}{unit}"

    # Executar cálculos principais
    Z_R, Z_L, Z_C, Z_RL, Z_F = calculate_impedance_damped(R, r, L_mH, C_uF, w1)
    I_R, I_L, I_C, I_F, V_R, V_L, V_C = calculate_current_voltage(V_line_kV, Z_R, Z_L, Z_C, Z_RL, Z_F)
    P_R, P_L, P_C, P_F = calculate_power(I_R, I_L, I_C, I_F, V_R, V_L, V_C)
    total_cap_count, nominal_cell_voltage, nominal_cell_power, nominal_cell_capacitance, association_capacitance = capacitor_cells(
        series_cap_count, parallel_cap_count, V_C, P_C, capacitor_overvoltage)
    short_circuit_inductor_current = short_circuit_current(V_line_kV, L_mH, f1)

    # Dicionário de resultados com detalhes das células capacitivas, indutor e resistor
    results = {
        "Impedance (ohm)": {
            "Resistor": f"({np.abs(Z_R):.2f} ∠ {np.angle(Z_R, deg=True):.2f}°) Ω",
            "Inductor": f"({np.abs(Z_L):.2f} ∠ {np.angle(Z_L, deg=True):.2f}°) Ω",
            "Capacitor": f"({np.abs(Z_C):.2f} ∠ {np.angle(Z_C, deg=True):.2f}°) Ω",
            "Filter": f"({np.abs(Z_F):.2f} ∠ {np.angle(Z_F, deg=True):.2f}°) Ω",
            "Resonance Frequency (Hz)": format_with_unit(resonance_frequency(L_mH, C_uF), "Hz")
        },
        "Current (A)": {
            "Resistor": f"({np.abs(I_R):.2f} ∠ {np.angle(I_R, deg=True):.2f}°) A",
            "Inductor": f"({np.abs(I_L):.2f} ∠ {np.angle(I_L, deg=True):.2f}°) A",
            "Capacitor": f"({np.abs(I_C):.2f} ∠ {np.angle(I_C, deg=True):.2f}°) A",
            "Filter": f"({np.abs(I_F):.2f} ∠ {np.angle(I_F, deg=True):.2f}°) A"
        },
        "Voltage (V)": {
            "Resistor": f"({np.abs(V_R):.2f} ∠ {np.angle(V_R, deg=True):.2f}°) V",
            "Inductor": f"({np.abs(V_L):.2f} ∠ {np.angle(V_L, deg=True):.2f}°) V",
            "Capacitor": f"({np.abs(V_C):.2f} ∠ {np.angle(V_C, deg=True):.2f}°) V",
            "Filter": f"({np.abs(V_R + V_C):.2f} ∠ {np.angle(V_R + V_C, deg=True):.2f}°) V"
        },
        "Power": {
            "R (W)": format_with_unit(np.real(3 * P_R), "W"),
            "L (VA)": f"{format_with_unit(np.real(3 * P_L), 'VA')} + j{format_with_unit(np.imag(3 * P_L), 'VA')}",
            "C (VAR)": format_with_unit(np.imag(3 * P_C), "VAR"),
            "Filter (VA)": f"{format_with_unit(np.real(3 * P_F), 'VA')} + j{format_with_unit(np.imag(3 * P_F), 'VA')}"
        },
        "Capacitor Cells": {
            "Total Number of Cells": f"{total_cap_count:.0f}",
            "Series Cell Count": f"{series_cap_count:.0f}",
            "Parallel Cell Count": f"{parallel_cap_count:.0f}",
            "Cell Voltage": format_with_unit(nominal_cell_voltage, "V"),
            "Cell Power": format_with_unit(nominal_cell_power, "VAR"),
            "Cell Capacitance": format_with_unit(nominal_cell_capacitance, "F")
        },
        "Bank": {
            "Bank Voltage": format_with_unit(np.sqrt(3) * capacitor_overvoltage * np.abs(V_C), "V"),
            "Considered Overvoltage": f"{capacitor_overvoltage:.4f}",
            "Bank Power": format_with_unit(total_cap_count * nominal_cell_power, "VAR"),
            "Bank Capacitance": format_with_unit(association_capacitance, "F")
        },
        "Inductor": {
            "Nominal Current": format_with_unit(inductor_overcurrent * np.abs(I_L), "A"),
            "Considered Overcurrent": f"{inductor_overcurrent:.4f}",
            "Short-Circuit Current": format_with_unit(short_circuit_inductor_current, "A"),
            "Inductance": format_with_unit(L_mH / 1000, "H"),
            "Inductor Resistance": format_with_unit(r, "Ω")
        },
        "Resistor": {
            "Nominal Current": format_with_unit(resistor_overcurrent * np.abs(I_R), "A"),
            "Considered Overcurrent": f"{resistor_overcurrent:.4f}",
            "Short-Circuit Current": format_with_unit((V_line_kV * 1e3 / np.sqrt(3)) / R, "A"),
            "Resistance": format_with_unit(R, "Ω")
        }
    }

    return results


# Interface do Streamlit
st.title("Simulação de Filtro Amortecido")

# Download do arquivo parameters.txt
st.header("1. Baixe o arquivo de parâmetros")
create_default_parameters()
with open(PARAMETERS_FILE, "rb") as file:
    st.download_button(label="Baixar parameters.txt", data=file, file_name="parameters.txt")

# Upload do arquivo parameters.txt após edição
st.header("2. Faça o upload do arquivo parameters.txt editado")
# Upload de qualquer arquivo de texto com extensão .txt
uploaded_file = st.file_uploader("Carregue um arquivo de parâmetros (.txt)", type="txt")

if uploaded_file:
    # Carregar parâmetros e exibir valores
    params = load_parameters(uploaded_file)
    st.subheader("Parâmetros carregados:")
    st.json(params)

    # Executar cálculos e exibir resultados
    st.header("3. Resultados da Simulação")
    results = damped_filter_calculation(
        params["f1"], params["R"], params["r"], params["L_mH"], params["C_uF"],
        params["V_line_kV"], params["capacitor_overvoltage"],
        params["inductor_overcurrent"], params["resistor_overcurrent"],
        params["series_cap_count"], params["parallel_cap_count"]
    )
    st.subheader("Resultados:")
    st.json(results)

    # Salvar resultados e permitir download
    st.header("4. Baixe os arquivos de resultados")
    txt_file, json_file, xlsx_file = save_results_as_files(results)
    st.download_button(label="Baixar results.txt", data=open(txt_file, "rb"), file_name="results.txt")
    st.download_button(label="Baixar results.json", data=open(json_file, "rb"), file_name="results.json")
    st.download_button(label="Baixar results.xlsx", data=open(xlsx_file, "rb"), file_name="results.xlsx")
