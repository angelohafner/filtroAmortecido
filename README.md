
# Simulação de Filtro Amortecido

Este projeto implementa uma aplicação web interativa para simulação de filtro amortecido usando **Streamlit**. O usuário pode baixar um arquivo de parâmetros padrão, ajustá-lo, fazer o upload de volta e visualizar os resultados calculados diretamente na interface. Além disso, os resultados da simulação podem ser baixados nos formatos TXT, JSON e XLSX.

## Índice
- [Instalação](#instalação)
- [Executando o Aplicativo](#executando-o-aplicativo)
- [Como Funciona](#como-funciona)
- [Parâmetros e Resultados](#parâmetros-e-resultados)
- [Exemplo de Uso](#exemplo-de-uso)

## Instalação

Primeiro, clone o repositório e navegue até o diretório do projeto:

```bash
git clone https://github.com/seu-usuario/simulacao-filtro-amortecido.git
cd simulacao-filtro-amortecido
```

Instale as dependências usando o `requirements.txt`:

```bash
pip install -r requirements.txt
```

### Dependências

As principais bibliotecas utilizadas neste projeto incluem:
- `streamlit` - Para criar a interface web interativa.
- `numpy` - Para cálculos numéricos.
- `pandas` e `openpyxl` - Para manipulação de dados e exportação dos resultados em XLSX.
- `matplotlib` - Para formatação de valores com `EngFormatter`.

## Executando o Aplicativo

Para iniciar a aplicação Streamlit, execute o seguinte comando:

```bash
streamlit run app.py
```

Isso abrirá o aplicativo no navegador. 

## Como Funciona

1. **Download do Arquivo de Parâmetros**: O aplicativo gera um arquivo padrão `parameters.txt` com parâmetros de entrada como resistência, capacitância, indutância, etc.
2. **Upload do Arquivo**: Após editar os parâmetros, faça o upload do `parameters.txt`.
3. **Simulação e Resultados**: O aplicativo exibe os valores calculados de impedância, corrente, tensão e potência. Além disso, inclui detalhes das células capacitivas, indutor e resistor.
4. **Download dos Resultados**: Os resultados da simulação podem ser baixados nos formatos **TXT**, **JSON** e **XLSX**.

## Parâmetros e Resultados

O arquivo `parameters.txt` contém os seguintes parâmetros padrão:

```text
f1 = 60                      # Frequência fundamental em Hz
R = 222                      # Resistência do resistor principal em ohms
r = 0.792                    # Resistência do indutor em ohms
L_mH = 34.303                # Indutância do indutor em mH
C_uF = 8.543                 # Capacitância do capacitor em uF
V_line_kV = 34.5             # Tensão de linha em kV
capacitor_overvoltage = 1.3  # Sobretensão permitida nos capacitores
inductor_overcurrent = 1.66  # Sobrecorrente permitida no indutor
resistor_overcurrent = 1.66  # Sobrecorrente permitida no resistor
series_cap_count = 2         # Número de capacitores em série
parallel_cap_count = 2       # Número de capacitores em paralelo
```

O resultado inclui cálculos de:
- **Impedância** (Resistor, Indutor, Capacitor, Filtro completo)
- **Corrente** em cada elemento
- **Tensão** em cada elemento
- **Potência** em cada elemento
- **Células Capacitivas**, **Banco de Capacitores**
- **Detalhes do Indutor** e **Resistor**

Cada valor é exibido com unidades apropriadas e, onde aplicável, no formato polar (magnitude ∠ ângulo).

## Exemplo de Uso

1. **Baixe o `parameters.txt`** no aplicativo e edite os valores conforme desejado.
2. **Faça o upload do `parameters.txt` editado**.
3. Visualize os **resultados da simulação** diretamente no aplicativo.
4. **Baixe os arquivos de resultados** nos formatos TXT, JSON e XLSX para análise ou integração com outros sistemas.

## Licença

Este projeto é distribuído sob a licença MIT. Consulte o arquivo [LICENSE](LICENSE) para mais informações.

---

Este projeto foi desenvolvido para auxiliar na simulação e análise de filtros amortecidos de forma prática e intuitiva. Aproveite e contribua!
