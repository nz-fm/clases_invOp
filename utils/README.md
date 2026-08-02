# Utils

Esta carpeta contiene algunas funciones útiles, principalmente para ver si un ejercicio propuesto es demasiado largo 
de resolver. Por ejemplo, si uno plantea un ejercicio de Branch & Bound para un parcial, está bueno corroborar que 
no será demasiado largo de resolver para les alumnes. Corroborar esto a mano puede ser tedioso si uno debe iterar el 
ejercicio propuesto. Las funciones implementadas en los archivos de esta carpeta buscan simplificar el proceso.

## `branch_and_bound.py`

Dado un problema de Programación Lineal Entera en dos variables, la fución `branch_and_bound` genera el árbol de Branch
& Bound. El propósito de esta función es ver rápidamente si un ejercicio de Branch & Bound requiere la resolución
de muchos subproblemas (es decir, si el ejercicio resultaría ser muy largo).

La función `branch_and_bound` requiere como input `A` la matriz del problema, `b` el vector de términos 
independientes, `c` el vector de coeficientes, `ineq` una lista con las desigualdades correspondientes a cada fila 
de `A`, `obj` el objetivo de optimización (`max` o `min`) y un argumento opcional `force_branch` que indica en qué 
variable ramificar luego de resolver la primera relajación lineal.

Las (des)igualdades de `ineq` vienen dadas por strings: `g` representa `>=`, `l` representa `<=` y `e` representa 
`=`. Se debe cumplir que `len(ineq) == A.shape[0]`.

La implementación actual de la resolución de la relajación lineal requiere tener instalado CPLEX (la versión de 
prueba es suficiente).  En el futuro reemplazaré CPLEX por un solver más conveniente.
### Ejemplo de uso

Para resolver el siguiente problema de Programación Lineal Entera:
$$\begin{array}{rrrrrrrrc}
\max & 3x_1 & + & 4x_2 &  &   \\
\text{s.a:}	 & 2x_1 & + & x_2 & \leq & 14  \\
			 & 2x_1 & + & 3x_2 & \leq & 17 \\
			 &2x_1 & +  & 2x_2 & \leq & 15 \\
			 & x_1  & & & \geq & 0 \\
             &  &  & x_2 & \geq & 0 \\
			 & x_1, & x_2 & \in & \mathbb{Z}
\end{array}
$$
```python
from utils.branch_and_bound import branch_and_bound

A = np.array([[2 , 1],
              [2, 3],
              [2, 2],
              [1, 0],
              [0, 1]
              ])
b = np.array([14, 17, 15, 0, 0])
c = np.array([3, 4])
ineq = 'lllgg'

branch_and_bound(A, b, c, ineq, 'max')
```