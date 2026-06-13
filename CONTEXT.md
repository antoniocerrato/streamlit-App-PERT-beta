# Contexto del proyecto

## Propósito

Crear un recurso docente muy didáctico para explicar el método PERT de tres valores y su relación con la distribución beta. La aplicación debe conectar la formulación matemática con la interpretación gráfica y la experimentación numérica.

## Público

Estudiantes de asignaturas de proyectos, planificación y gestión de proyectos. No debe suponerse una formación estadística avanzada.

## Principios didácticos

- Presentar primero la intuición y después la formulación.
- Mantener visibles los significados de `a`, `m` y `b`.
- Distinguir con claridad PERT clásico y Beta-PERT.
- Explicar que la varianza clásica de PERT es una aproximación.
- Utilizar gráficos, probabilidades y simulación para reforzar los conceptos.
- Evitar que la aplicación funcione como una caja negra.

## Convenciones

- `a`: duración optimista.
- `m`: duración más probable.
- `b`: duración pesimista.
- `λ`: parámetro de concentración de Beta-PERT.
- La parametrización clásica utiliza `λ = 4`.
- La interfaz está escrita en español de España.
- Se utiliza la palabra «duración», sin fijar una unidad concreta.

## Arquitectura

- `app.py`: interfaz y visualizaciones.
- `pert_math.py`: lógica matemática independiente de Streamlit.
- `tests/`: pruebas de las identidades matemáticas principales.
- `docs/MATEMATICA.md`: desarrollo teórico.

## Próximas ampliaciones posibles

- Importación de actividades desde CSV o Excel.
- Precedencias y construcción de una red AON.
- Fechas tempranas y tardías.
- Holguras y camino crítico.
- Simulación Monte Carlo de la duración total del proyecto.
- Correlación entre duraciones de actividades.
- Comparación con distribución triangular.
