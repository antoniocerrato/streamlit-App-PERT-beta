# Formulación matemática

## 1. Estimación de tres valores

Para una actividad se definen:

- `a`: duración optimista;
- `m`: duración más probable;
- `b`: duración pesimista.

Debe cumplirse:

\[
a \leq m \leq b, \qquad a<b.
\]

## 2. PERT clásico

La duración esperada se aproxima mediante:

\[
t_e=\frac{a+4m+b}{6}.
\]

La desviación típica tradicional de PERT es:

\[
\sigma_{PERT}=\frac{b-a}{6},
\]

por lo que la varianza es:

\[
\operatorname{Var}_{PERT}(T)=\left(\frac{b-a}{6}\right)^2.
\]

Estas expresiones para la dispersión son aproximaciones del método clásico.

## 3. Distribución Beta-PERT

Sea una variable aleatoria:

\[
X\sim \operatorname{Beta}(\alpha,\beta),
\]

definida en `[0,1]`. La duración se obtiene transformándola al intervalo `[a,b]`:

\[
T=a+(b-a)X.
\]

Los parámetros de forma se definen mediante un parámetro de concentración `λ > 0`:

\[
\alpha=1+\lambda\frac{m-a}{b-a},
\]

\[
\beta=1+\lambda\frac{b-m}{b-a}.
\]

Cuando la moda es interior al intervalo, esta parametrización garantiza:

\[
\operatorname{Moda}(T)=m.
\]

## 4. Esperanza matemática

La esperanza de una beta es:

\[
\operatorname{E}[X]=\frac{\alpha}{\alpha+\beta}.
\]

Por tanto:

\[
\operatorname{E}[T]
=a+(b-a)\frac{\alpha}{\alpha+\beta}.
\]

Sustituyendo `α` y `β`:

\[
\operatorname{E}[T]=\frac{a+\lambda m+b}{\lambda+2}.
\]

Para `λ=4`:

\[
\operatorname{E}[T]=\frac{a+4m+b}{6},
\]

que coincide con la fórmula clásica de PERT.

## 5. Varianza exacta de Beta-PERT

La varianza de una beta es:

\[
\operatorname{Var}(X)
=\frac{\alpha\beta}
{(\alpha+\beta)^2(\alpha+\beta+1)}.
\]

Después de transformar al intervalo `[a,b]`:

\[
\operatorname{Var}(T)
=(b-a)^2
\frac{\alpha\beta}
{(\alpha+\beta)^2(\alpha+\beta+1)}.
\]

Esta varianza depende también de la posición de `m`, mientras que la aproximación clásica de PERT depende únicamente del rango `b-a`. Por ello ambas varianzas no coinciden en general.

## 6. Probabilidades y cuantiles

Para un plazo `d`, la probabilidad de terminar antes de ese plazo es:

\[
P(T\leq d)=F_T(d),
\]

donde `F_T` es la función de distribución acumulada de Beta-PERT.

El cuantil de nivel `p` satisface:

\[
P(T\leq t_p)=p.
\]

## 7. Simulación de Monte Carlo

La simulación genera valores independientes:

\[
T_1,T_2,\ldots,T_n\sim\operatorname{BetaPERT}(a,m,b,\lambda).
\]

La media muestral:

\[
\overline{T}_n=\frac{1}{n}\sum_{i=1}^n T_i
\]

converge hacia la esperanza teórica al aumentar `n`.
