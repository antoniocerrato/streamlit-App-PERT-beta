"""Aplicación didáctica sobre el método PERT de tres valores y Beta-PERT."""

from __future__ import annotations

import math

import numpy as np
import pandas as pd
import plotly.graph_objects as go
import streamlit as st

from pert_math import (
    beta_pert_cdf,
    beta_pert_pdf,
    beta_pert_ppf,
    calculate_pert_parameters,
    sample_beta_pert,
    validate_three_point_estimate,
)


st.set_page_config(
    page_title="PERT y distribución Beta",
    page_icon="📐",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.markdown(
    """
    <style>
    .main .block-container {max-width: 1250px; padding-top: 1.5rem;}
    .hero {
        padding: 1.3rem 1.5rem;
        border-radius: 1rem;
        background: linear-gradient(135deg, rgba(38,88,139,.13), rgba(52,152,219,.06));
        border: 1px solid rgba(38,88,139,.20);
        margin-bottom: 1rem;
    }
    .hero h1 {margin: 0 0 .3rem 0;}
    .concept-card {
        padding: 1rem 1.1rem;
        border-radius: .8rem;
        border: 1px solid rgba(120,120,120,.22);
        min-height: 145px;
    }
    .small-note {font-size: .92rem; opacity: .84;}
    div[data-testid="stMetric"] {
        border: 1px solid rgba(120,120,120,.20);
        padding: .75rem;
        border-radius: .65rem;
    }
    </style>
    """,
    unsafe_allow_html=True,
)


PRESETS = {
    "Ejemplo asimétrico": (6.0, 10.0, 18.0),
    "Caso simétrico": (4.0, 8.0, 12.0),
    "Riesgo de retraso elevado": (5.0, 7.0, 20.0),
    "Moda próxima al pesimista": (2.0, 9.0, 11.0),
}


def format_number(value: float, digits: int = 3) -> str:
    """Formatea números para la interfaz en español."""

    if math.isclose(value, round(value), abs_tol=10 ** (-digits)):
        return f"{value:,.0f}".replace(",", "X").replace(".", ",").replace("X", ".")
    return f"{value:,.{digits}f}".replace(",", "X").replace(".", ",").replace("X", ".")


def distribution_figure(a: float, m: float, b: float, concentration: float) -> go.Figure:
    x = np.linspace(a, b, 700)
    y = beta_pert_pdf(x, a, m, b, concentration)
    stats = calculate_pert_parameters(a, m, b, concentration)

    fig = go.Figure()
    fig.add_trace(
        go.Scatter(
            x=x,
            y=y,
            mode="lines",
            name="Densidad Beta-PERT",
            fill="tozeroy",
            hovertemplate="Duración: %{x:.3f}<br>Densidad: %{y:.4f}<extra></extra>",
        )
    )
    markers = [
        (a, "Optimista, a", "dash"),
        (m, "Más probable, m", "dot"),
        (stats.beta_mean, "Media", "solid"),
        (b, "Pesimista, b", "dash"),
    ]
    for value, label, dash in markers:
        fig.add_vline(x=value, line_dash=dash, annotation_text=label, annotation_position="top")

    fig.update_layout(
        title="Distribución de la duración de la actividad",
        xaxis_title="Duración",
        yaxis_title="Densidad de probabilidad",
        hovermode="x unified",
        legend_orientation="h",
        margin=dict(l=30, r=20, t=65, b=30),
    )
    return fig


def probability_figure(
    a: float,
    m: float,
    b: float,
    concentration: float,
    threshold: float,
) -> go.Figure:
    x = np.linspace(a, b, 700)
    y = beta_pert_pdf(x, a, m, b, concentration)
    mask = x <= threshold

    fig = go.Figure()
    fig.add_trace(go.Scatter(x=x, y=y, mode="lines", name="Densidad"))
    fig.add_trace(
        go.Scatter(
            x=x[mask],
            y=y[mask],
            mode="lines",
            fill="tozeroy",
            name=f"P(T ≤ {threshold:.2f})",
            hovertemplate="Duración: %{x:.3f}<br>Densidad: %{y:.4f}<extra></extra>",
        )
    )
    fig.add_vline(x=threshold, line_dash="dash", annotation_text="Plazo objetivo")
    fig.update_layout(
        title="Área acumulada hasta el plazo objetivo",
        xaxis_title="Duración",
        yaxis_title="Densidad",
        margin=dict(l=30, r=20, t=65, b=30),
    )
    return fig


def influence_figure(a: float, b: float, concentration: float) -> go.Figure:
    modes = np.linspace(a, b, 160)
    means = [calculate_pert_parameters(a, mode, b, concentration).beta_mean for mode in modes]
    midpoint = (a + b) / 2

    fig = go.Figure()
    fig.add_trace(go.Scatter(x=modes, y=means, mode="lines", name="Media Beta-PERT"))
    fig.add_trace(
        go.Scatter(
            x=modes,
            y=modes,
            mode="lines",
            name="Referencia: media = moda",
            line=dict(dash="dot"),
        )
    )
    fig.add_vline(x=midpoint, line_dash="dash", annotation_text="Punto medio")
    fig.update_layout(
        title="Cómo desplaza la moda a la duración esperada",
        xaxis_title="Valor más probable, m",
        yaxis_title="Duración esperada",
        margin=dict(l=30, r=20, t=65, b=30),
    )
    return fig


st.markdown(
    """
    <section class="hero">
      <h1>PERT de tres valores y distribución Beta</h1>
      <p>De la intuición de tres estimaciones a un modelo probabilístico completo.</p>
    </section>
    """,
    unsafe_allow_html=True,
)

def apply_preset() -> None:
    preset_a, preset_m, preset_b = PRESETS[st.session_state.preset_name]
    st.session_state.a_input = preset_a
    st.session_state.m_input = preset_m
    st.session_state.b_input = preset_b


if "preset_name" not in st.session_state:
    st.session_state.preset_name = next(iter(PRESETS))
if "a_input" not in st.session_state:
    st.session_state.a_input, st.session_state.m_input, st.session_state.b_input = PRESETS[
        st.session_state.preset_name
    ]

with st.sidebar:
    st.header("Parámetros de la actividad")
    st.selectbox(
        "Ejemplo",
        list(PRESETS),
        key="preset_name",
        on_change=apply_preset,
    )

    a = st.number_input("Optimista, a", step=0.5, format="%.2f", key="a_input")
    m = st.number_input("Más probable, m", step=0.5, format="%.2f", key="m_input")
    b = st.number_input("Pesimista, b", step=0.5, format="%.2f", key="b_input")
    concentration = st.slider(
        "Concentración, λ",
        min_value=0.5,
        max_value=12.0,
        value=4.0,
        step=0.5,
        help="λ=4 reproduce la media clásica de PERT. Valores mayores concentran más probabilidad alrededor de m.",
    )
    unit = st.text_input("Unidad", value="días")

    st.divider()
    st.caption("Condición necesaria: a ≤ m ≤ b, con a < b.")

try:
    validate_three_point_estimate(a, m, b)
    stats = calculate_pert_parameters(a, m, b, concentration)
except ValueError as exc:
    st.error(str(exc))
    st.stop()

if not unit.strip():
    unit = "unidades de tiempo"

main_tabs = st.tabs(
    [
        "1. Fundamentos",
        "2. Explorar la distribución",
        "3. Probabilidades",
        "4. Simulación",
        "5. Varias actividades",
        "6. Autoevaluación",
    ]
)

with main_tabs[0]:
    st.header("¿Por qué se usan tres valores?")
    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown(
            """
            <div class="concept-card">
            <h3>Optimista, a</h3>
            <p>Duración mínima razonable si las condiciones son especialmente favorables.</p>
            </div>
            """,
            unsafe_allow_html=True,
        )
    with col2:
        st.markdown(
            """
            <div class="concept-card">
            <h3>Más probable, m</h3>
            <p>Duración que se considera más plausible en condiciones normales.</p>
            </div>
            """,
            unsafe_allow_html=True,
        )
    with col3:
        st.markdown(
            """
            <div class="concept-card">
            <h3>Pesimista, b</h3>
            <p>Duración máxima razonable cuando aparecen dificultades importantes.</p>
            </div>
            """,
            unsafe_allow_html=True,
        )

    st.subheader("La estimación clásica de PERT")
    st.latex(r"t_e=\frac{a+4m+b}{6}")
    st.write(
        "La duración más probable recibe un peso cuatro veces mayor que cada extremo. "
        "No es una media aritmética simple: pretende reducir la influencia de escenarios extremos sin ignorarlos."
    )

    formula_cols = st.columns(3)
    formula_cols[0].metric("Duración esperada PERT", f"{format_number(stats.pert_mean)} {unit}")
    formula_cols[1].metric("Desviación típica aproximada", f"{format_number(stats.pert_standard_deviation)} {unit}")
    formula_cols[2].metric("Varianza aproximada", f"{format_number(stats.pert_variance)} {unit}²")

    st.latex(r"\sigma_{PERT}=\frac{b-a}{6}")
    st.latex(r"\operatorname{Var}_{PERT}(T)=\left(\frac{b-a}{6}\right)^2")

    st.info(
        "La desviación típica y la varianza anteriores son aproximaciones tradicionales de PERT. "
        "No coinciden necesariamente con la varianza exacta de una distribución Beta-PERT."
    )

    st.subheader("De tres valores a una distribución Beta-PERT")
    st.write(
        "La distribución beta ordinaria vive en el intervalo [0, 1]. Para representar duraciones, "
        "se transforma al intervalo [a, b]. Sus parámetros de forma se eligen de modo que m actúe como moda."
    )
    st.latex(r"\alpha=1+\lambda\frac{m-a}{b-a}")
    st.latex(r"\beta=1+\lambda\frac{b-m}{b-a}")
    st.latex(r"T=a+(b-a)X,\qquad X\sim\operatorname{Beta}(\alpha,\beta)")

    st.subheader("La conexión matemática con PERT")
    st.latex(r"\operatorname{E}[T]=\frac{a+\lambda m+b}{\lambda+2}")
    st.write("Al tomar λ = 4 se obtiene exactamente:")
    st.latex(r"\operatorname{E}[T]=\frac{a+4m+b}{6}")
    st.success(
        "Esta igualdad es el vínculo central: la fórmula clásica de PERT coincide con la media de "
        "una Beta-PERT cuando λ = 4."
    )

with main_tabs[1]:
    st.header("Explorador de la distribución")
    metric_cols = st.columns(5)
    metric_cols[0].metric("α", format_number(stats.alpha))
    metric_cols[1].metric("β", format_number(stats.beta))
    metric_cols[2].metric("Media Beta-PERT", f"{format_number(stats.beta_mean)} {unit}")
    metric_cols[3].metric("Moda", f"{format_number(m)} {unit}")
    metric_cols[4].metric("Punto medio", f"{format_number((a+b)/2)} {unit}")

    st.plotly_chart(distribution_figure(a, m, b, concentration), width="stretch")

    interpretation_cols = st.columns(2)
    with interpretation_cols[0]:
        st.subheader("Lectura de la forma")
        midpoint = (a + b) / 2
        if math.isclose(m, midpoint, rel_tol=1e-9, abs_tol=1e-9):
            st.write("La moda está en el centro: la distribución es simétrica.")
        elif m < midpoint:
            st.write(
                "La moda está a la izquierda del centro. La distribución presenta una cola más larga hacia "
                "duraciones elevadas: existe riesgo de retrasos importantes."
            )
        else:
            st.write(
                "La moda está a la derecha del centro. La cola más larga queda hacia duraciones reducidas."
            )

        if concentration < 4:
            st.write("Como λ < 4, la distribución es relativamente dispersa.")
        elif concentration > 4:
            st.write("Como λ > 4, la distribución se concentra más alrededor de m.")
        else:
            st.write("λ = 4 corresponde a la parametrización Beta-PERT clásica.")

    with interpretation_cols[1]:
        st.subheader("PERT clásico frente a Beta-PERT")
        comparison = pd.DataFrame(
            {
                "Magnitud": ["Media", "Varianza"],
                "PERT clásico": [stats.pert_mean, stats.pert_variance],
                "Beta-PERT": [stats.beta_mean, stats.beta_variance],
                "Diferencia": [
                    stats.beta_mean - stats.pert_mean,
                    stats.beta_variance - stats.pert_variance,
                ],
            }
        )
        st.dataframe(
            comparison.style.format(
                {
                    "PERT clásico": "{:.4f}",
                    "Beta-PERT": "{:.4f}",
                    "Diferencia": "{:+.4f}",
                }
            ),
            width="stretch",
            hide_index=True,
        )
        if math.isclose(concentration, 4.0):
            st.caption("Con λ = 4, las medias coinciden; las varianzas no tienen por qué coincidir.")
        else:
            st.caption("Con λ ≠ 4, incluso la media Beta-PERT se separa de la fórmula clásica de PERT.")

    st.plotly_chart(influence_figure(a, b, concentration), width="stretch")

with main_tabs[2]:
    st.header("Probabilidades y plazos")
    prob_col1, prob_col2 = st.columns([1, 2])
    with prob_col1:
        threshold = st.slider(
            "Plazo objetivo",
            min_value=float(a),
            max_value=float(b),
            value=float(stats.beta_mean),
            step=max((b - a) / 200, 0.01),
        )
        probability = beta_pert_cdf(threshold, a, m, b, concentration)
        st.metric(
            "Probabilidad de terminar a tiempo",
            f"{100 * probability:.2f} %",
            help="P(T ≤ plazo objetivo)",
        )
        st.latex(rf"P(T\leq {threshold:.3f})={probability:.4f}")
        st.write(
            f"Según el modelo, aproximadamente {100 * probability:.1f} de cada 100 actividades "
            f"terminarían antes de {format_number(threshold)} {unit}."
        )

    with prob_col2:
        st.plotly_chart(
            probability_figure(a, m, b, concentration, threshold),
            width="stretch",
        )

    st.divider()
    st.subheader("Cálculo inverso: duración asociada a un nivel de confianza")
    confidence = st.slider("Nivel de confianza", 1, 99, 90, 1) / 100
    quantile = beta_pert_ppf(confidence, a, m, b, concentration)
    st.metric(
        f"Duración que no se supera con un {confidence:.0%} de probabilidad",
        f"{format_number(quantile)} {unit}",
    )
    st.latex(rf"P(T\leq t_{{{confidence:.2f}}})={confidence:.2f}")
    st.caption(
        "El cuantil no asegura que la actividad termine en ese plazo; expresa una probabilidad según el modelo elegido."
    )

with main_tabs[3]:
    st.header("Simulación de Monte Carlo")
    controls, results = st.columns([1, 2])
    with controls:
        simulation_size = st.select_slider(
            "Número de simulaciones",
            options=[500, 1_000, 2_000, 5_000, 10_000, 25_000, 50_000],
            value=10_000,
        )
        seed = st.number_input("Semilla aleatoria", min_value=0, value=42, step=1)
        st.write(
            "Cada simulación representa una posible duración de la actividad. Al repetir el experimento, "
            "el histograma se aproxima a la densidad teórica."
        )

    samples = sample_beta_pert(
        simulation_size,
        a,
        m,
        b,
        concentration=concentration,
        seed=int(seed),
    )

    with results:
        sim_metrics = st.columns(4)
        sim_metrics[0].metric("Media simulada", f"{format_number(samples.mean())} {unit}")
        sim_metrics[1].metric("Media teórica", f"{format_number(stats.beta_mean)} {unit}")
        sim_metrics[2].metric("Desv. típica simulada", f"{format_number(samples.std(ddof=1))} {unit}")
        sim_metrics[3].metric("Desv. típica teórica", f"{format_number(math.sqrt(stats.beta_variance))} {unit}")

    x = np.linspace(a, b, 500)
    theoretical_pdf = beta_pert_pdf(x, a, m, b, concentration)
    hist = go.Figure()
    hist.add_trace(
        go.Histogram(
            x=samples,
            histnorm="probability density",
            nbinsx=45,
            name="Simulaciones",
            opacity=0.65,
        )
    )
    hist.add_trace(go.Scatter(x=x, y=theoretical_pdf, mode="lines", name="Densidad teórica"))
    hist.update_layout(
        title="Histograma simulado y distribución teórica",
        xaxis_title="Duración",
        yaxis_title="Densidad",
        barmode="overlay",
        margin=dict(l=30, r=20, t=65, b=30),
    )
    st.plotly_chart(hist, width="stretch")

    running_mean = np.cumsum(samples) / np.arange(1, len(samples) + 1)
    convergence = go.Figure()
    convergence.add_trace(
        go.Scatter(
            x=np.arange(1, len(samples) + 1),
            y=running_mean,
            mode="lines",
            name="Media acumulada",
        )
    )
    convergence.add_hline(
        y=stats.beta_mean,
        line_dash="dash",
        annotation_text="Media teórica",
    )
    convergence.update_layout(
        title="Convergencia de la media simulada",
        xaxis_title="Número de simulaciones",
        yaxis_title="Media acumulada",
        margin=dict(l=30, r=20, t=65, b=30),
    )
    st.plotly_chart(convergence, width="stretch")

with main_tabs[4]:
    st.header("Aplicación práctica a varias actividades")
    st.write(
        "Edita la tabla. La app calcula la media PERT, los parámetros Beta-PERT y las dos varianzas. "
        "Esta sección analiza actividades por separado; todavía no construye una red de precedencias."
    )

    default_activities = pd.DataFrame(
        {
            "Actividad": ["A", "B", "C", "D"],
            "Optimista a": [3.0, 2.0, 5.0, 4.0],
            "Más probable m": [5.0, 4.0, 8.0, 6.0],
            "Pesimista b": [9.0, 10.0, 14.0, 11.0],
        }
    )
    edited = st.data_editor(
        default_activities,
        num_rows="dynamic",
        width="stretch",
        hide_index=True,
        column_config={
            "Actividad": st.column_config.TextColumn(required=True),
            "Optimista a": st.column_config.NumberColumn(format="%.2f", required=True),
            "Más probable m": st.column_config.NumberColumn(format="%.2f", required=True),
            "Pesimista b": st.column_config.NumberColumn(format="%.2f", required=True),
        },
    )

    rows: list[dict[str, float | str]] = []
    errors: list[str] = []
    for index, row in edited.iterrows():
        try:
            activity_a = float(row["Optimista a"])
            activity_m = float(row["Más probable m"])
            activity_b = float(row["Pesimista b"])
            activity_stats = calculate_pert_parameters(
                activity_a,
                activity_m,
                activity_b,
                concentration,
            )
            rows.append(
                {
                    "Actividad": str(row["Actividad"]),
                    "Media PERT": activity_stats.pert_mean,
                    "Media Beta-PERT": activity_stats.beta_mean,
                    "α": activity_stats.alpha,
                    "β": activity_stats.beta,
                    "Varianza PERT": activity_stats.pert_variance,
                    "Varianza Beta-PERT": activity_stats.beta_variance,
                }
            )
        except (TypeError, ValueError):
            errors.append(f"Fila {index + 1}: debe cumplirse a ≤ m ≤ b y a < b.")

    if errors:
        for error in errors:
            st.warning(error)

    if rows:
        results_df = pd.DataFrame(rows)
        st.dataframe(
            results_df.style.format(
                {
                    "Media PERT": "{:.3f}",
                    "Media Beta-PERT": "{:.3f}",
                    "α": "{:.3f}",
                    "β": "{:.3f}",
                    "Varianza PERT": "{:.3f}",
                    "Varianza Beta-PERT": "{:.3f}",
                }
            ),
            width="stretch",
            hide_index=True,
        )

        chart = go.Figure()
        chart.add_trace(
            go.Bar(
                x=results_df["Actividad"],
                y=results_df["Media PERT"],
                name="Media PERT",
            )
        )
        chart.add_trace(
            go.Bar(
                x=results_df["Actividad"],
                y=results_df["Media Beta-PERT"],
                name="Media Beta-PERT",
            )
        )
        chart.update_layout(
            title="Comparación de duraciones esperadas",
            xaxis_title="Actividad",
            yaxis_title=f"Duración ({unit})",
            barmode="group",
            margin=dict(l=30, r=20, t=65, b=30),
        )
        st.plotly_chart(chart, width="stretch")

        csv_data = results_df.to_csv(index=False).encode("utf-8-sig")
        st.download_button(
            "Descargar resultados en CSV",
            data=csv_data,
            file_name="resultados_pert_beta.csv",
            mime="text/csv",
        )

with main_tabs[5]:
    st.header("Autoevaluación")
    st.write("Responde y abre después la explicación.")

    q1 = st.radio(
        "1. ¿Qué valor recibe mayor peso en la fórmula clásica de PERT?",
        ["El optimista", "El más probable", "El pesimista", "Los tres por igual"],
        index=None,
    )
    with st.expander("Ver respuesta 1"):
        if q1 is None:
            st.write("Selecciona primero una respuesta.")
        elif q1 == "El más probable":
            st.success("Correcto. m tiene peso 4, mientras que a y b tienen peso 1.")
        else:
            st.error("No es correcto. La fórmula es (a + 4m + b) / 6.")

    q2 = st.radio(
        "2. ¿Qué sucede con la media Beta-PERT cuando λ = 4?",
        [
            "Coincide con la moda",
            "Coincide con la media clásica de PERT",
            "Coincide siempre con el punto medio",
            "La distribución se vuelve uniforme",
        ],
        index=None,
    )
    with st.expander("Ver respuesta 2"):
        if q2 is None:
            st.write("Selecciona primero una respuesta.")
        elif q2 == "Coincide con la media clásica de PERT":
            st.success("Correcto. E[T] = (a + 4m + b) / 6 cuando λ = 4.")
        else:
            st.error("No es correcto. λ = 4 enlaza la media Beta-PERT con la fórmula clásica.")

    q3 = st.radio(
        "3. Si m está muy próximo a a, ¿qué interpretación es más adecuada?",
        [
            "No hay incertidumbre",
            "La distribución es necesariamente simétrica",
            "Existe una cola hacia duraciones altas",
            "La duración pesimista deja de influir",
        ],
        index=None,
    )
    with st.expander("Ver respuesta 3"):
        if q3 is None:
            st.write("Selecciona primero una respuesta.")
        elif q3 == "Existe una cola hacia duraciones altas":
            st.success("Correcto. La mayor parte de la masa queda cerca de a y aparece una cola hacia b.")
        else:
            st.error("No es correcto. La asimetría expresa riesgo de duraciones superiores poco frecuentes.")

    st.subheader("Pregunta de reflexión")
    st.write(
        "Dos actividades pueden tener la misma media PERT pero distribuciones diferentes. "
        "Busca dos ternas (a, m, b) con igual valor de (a + 4m + b) / 6 y compara sus curvas."
    )

st.divider()
st.caption(
    "Aplicación docente. Los resultados dependen de que las estimaciones a, m y b sean razonables "
    "y de que la distribución Beta-PERT sea adecuada para representar la incertidumbre."
)
