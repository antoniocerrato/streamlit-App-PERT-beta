# PERT de tres valores y distribución Beta-PERT

Aplicación docente desarrollada con Streamlit para estudiar la relación entre:

- las estimaciones optimista, más probable y pesimista;
- la fórmula clásica de duración esperada de PERT;
- la distribución Beta-PERT;
- la varianza aproximada de PERT y la varianza exacta de Beta-PERT;
- el cálculo de probabilidades, cuantiles y simulaciones de Monte Carlo.

## Puesta en marcha

Se recomienda Python 3.11 o 3.12.

```bash
python -m venv .venv
```

En Windows:

```bash
.venv\Scripts\activate
```

En macOS o Linux:

```bash
source .venv/bin/activate
```

Instalación y ejecución:

```bash
pip install -r requirements.txt
streamlit run app.py
```

La aplicación se abrirá normalmente en `http://localhost:8501`.

## Contenido de la aplicación

1. Fundamentos del método de los tres valores.
2. Relación matemática entre PERT y Beta-PERT.
3. Explorador interactivo de la distribución.
4. Probabilidades de cumplimiento y cuantiles.
5. Simulación de Monte Carlo y convergencia.
6. Comparación de varias actividades.
7. Preguntas de autoevaluación.

## Estructura

```text
pert_beta_streamlit/
├── app.py
├── pert_math.py
├── requirements.txt
├── README.md
├── CONTEXT.md
├── docs/
│   └── MATEMATICA.md
├── tests/
│   └── test_pert_math.py
└── .streamlit/
    └── config.toml
```

## Despliegue en Streamlit Community Cloud

1. Subir esta carpeta a un repositorio de GitHub.
2. Crear una aplicación en Streamlit Community Cloud.
3. Seleccionar el repositorio, la rama y `app.py` como archivo principal.
4. Desplegar.

No se necesitan secretos ni servicios externos.

## Alcance actual

La versión actual explica y analiza actividades individuales y permite comparar varias actividades. No incluye todavía relaciones de precedencia, cálculo de fechas tempranas y tardías, holguras ni camino crítico.
