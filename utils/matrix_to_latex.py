"""
Se implementa la función `matrix_to_latex` para simplificar la escritura de los problemas de Programación Lineal para
ejercicios y parciales. La idea es ingresar la matriz. los vectores y desigualdades del problema y que se imprima
directamente el código de Latex con la formulación del problema.
"""


import numpy as np


def ineq_sign(s):
    if s == 'l':
        return '\leq'
    elif s == 'g':
        return '\geq'
    else:
        return '='


def objective(obj):
    if obj == 'max':
        return '\\max'
    else:
        return '\\min'


def inner_prod(v, nvars):
    s = []
    for i in range(nvars):
        if v[i] == 0:
            continue
        if not s:
            if v[i] != 1 and v[i] != -1:
                s.append(f'{v[i]}x_{i + 1}')
            elif v[i] == -1:
                s.append(f'-x_{i + 1}')
            else:
                s.append(f'x_{i + 1}')
        elif v[i] >= 0 and v[i] != 1:
            s.append(f'+{v[i]}x_{i + 1}')
        elif v[i] < 0 and v[i] != -1:
            s.append(f'{v[i]}x_{i + 1}')
        elif v[i] == 1:
            s.append(f'+x_{i + 1}')
        elif v[i] == -1:
            s.append(f'-x_{i + 1}')

    return ''.join(s)


def matrix_to_latex(A, b, c, ineq, obj):
    """ Para escribir modelos en Latex (útil para armar parciales y guías de ejercicios) """
    n_vars = A.shape[1]
    output = ['\\[', '\\begin{array}{rrcl}']
    output.append(f'{objective(obj)} & \\multicolumn{{3}}{{l}}{{z = {inner_prod(c, n_vars)}}} \\\\')
    output.append(f's.a: & {inner_prod(A[0, :], n_vars)} & {ineq_sign(ineq[0])} & {b[0]} \\\\')
    for i in range(1, A.shape[0]):
        output.append(f' & {inner_prod(A[i, :], n_vars)} & {ineq_sign(ineq[i])} & {b[i]} \\\\')
    output.extend(['\\end{array}', '\\]'])

    model = '\n'.join(output)
    print(model)


def translate_model_to_latex():
    """ Para usar model_to_latex """
    A = np.array([[2, 1, -2, 1],
                  [0, -1, 3, -2]])
    b = np.array([10, -8])
    c = np.array([3, 1, -4, 2])
    ineq = 'gl'
    obj = 'max'

    print(matrix_to_latex(A, b, c, ineq, obj))

