"""
Este archivo proporciona la función `simplex` que permite aplicar el algoritmo para un problema de Programación
Lineal estandarizado. Además de resolver el problema, la función tiene la opción de imprimir en pantalla los cálculos
matriciales o los diccionarios correspondientes a cada iteración del algoritmo.
Lo he implementado principalmente para armar ejercicios en la segunda parte de la materia: con esta función puedo ver
qué tan largo es un ejercicio clásico (o que tan "feos" son los cálculos) al aplicar SIMPLEX haciendo las cuentas.
"""

import numpy as np
from sympy import nsimplify


class NoFeasibleSolution(Exception):
    pass


class UnoundedProblem(Exception):
    pass


def trivial_feasible_basic_sol(A):
    """
    Chequea si se puede obtener una solución básica facible inicial de manera sencilla. En caso afirmativo,
    devuelve los índices de sus variables básicas.
    :param A: matriz del problema
    :type A: numpy.array
    :return: None si no se puede obtener una solución básica factible inicial trivial o los índices de las variables
    básicas.
    :rtype: None | list[int]
    """
    n, m = A.shape
    if np.all(A[:, m-n:] == np.eye(n)):
        return list(range(m-n, m))
    return None


def phase1(A, b):
    """
    Lleva a cabo la Fase I de SIMPLEX para buscar una solución básica factible inicial.
    :param A: matriz del problema
    :type A: np.array
    :param b: vector con los valores del lado derecho de las restricciones
    :type b: np.array
    :return: índice de las variables básicas en la solución básica factible inicial hallada
    :rtype: list[int]
    :raises: NoFeasibleSolution si el problema original es infactible.
    """
    n, m = A.shape

    # Ampliamos la matriz A para incluir a las variables auxiliares de la Fase I. Se incluye una variable auxiliar
    # por cada restricción.
    A = np.concatenate((A, np.eye(n)), axis=1)

    # El vector de coeficientes de la función objetivo en la Fase I está compuesto por 0's para las variables del
    # problema original y -1's para las variables auxiliares.
    c = np.array([0]*m + [-1]*n)

    # La solución básica factible inicial viene dada por aquella donde las variables básicas son las variables
    # auxiliares
    basic_vars = list(range(m, m+n))

    # Iteramos hasta alcanzar el óptimo
    opt_achieved = False
    while not opt_achieved:
        opt_bvar_values, opt_achieved = simplex_iteration(c, A, b, basic_vars)

    # Si en el óptimo alguna de las variables auxiliares es básica con valor distinto de 0, el problema original es
    # infactible
    if any(k >= m and not np.isclose(v, 0) for k, v in opt_bvar_values.items()):
        raise NoFeasibleSolution('Problema sin solución factible!')

    # Se elimina la eventual aparición de una variable auxiliar en las variables básicas de la solución óptima
    # hallada y se devuelven las variables básicas de la solución básica factible inicial
    basic_vars = [v for v in basic_vars if v <= m-1]

    return basic_vars


def print_dictionary(basic_vars, var_names, A, b, c):
    """
    Imprime el diccionario correspondiente a la solucion básica que tiene a basic_vars como variables básicas.
    :param basic_vars: índices de las variables básicas en la solución básica factible actual
    :type basic_vars: list[int]
    :param var_names: diccionario que mapea el indice de una variable a su nombre
    :type var_names: dict[int,str]
    :param A: matriz del problema
    :type A: np.array
    :param b: vector con los valores del lado derecho de las restricciones
    :type b: np.array
    :param c: vector con los coeficientes de las variables en la función objetivo
    :type c: np.array
    :return: diccionario con el valor de las variables básicas en el óptimo y un indicador de si se alcanzó el óptimo.
    :rtype: tuple[None | dict, bool]
    :raises: UnboundedProblem si detecta que el problema es no acotado.
    """
    non_basic_vars = [var for var in range(A.shape[1]) if var not in basic_vars]

    B = A[:, basic_vars]
    basic_vars_values = np.linalg.solve(B, b)

    R = A[:, non_basic_vars]
    pi = np.linalg.solve(B.T, c[basic_vars])
    reduced_costs = c[non_basic_vars] - pi @ R

    dict_matrix = np.zeros((A.shape[0]+1, A.shape[1] - len(basic_vars) + 1))

    # Primera columna del diccionario
    dict_matrix[:A.shape[0], 0] = basic_vars_values
    dict_matrix[-1, 0] = basic_vars_values @ c[basic_vars]

    # Columna de cada variable no básica
    for idx, var in enumerate(non_basic_vars, start=1):
        dict_matrix[:A.shape[0], idx] = - np.linalg.solve(B, A[:, var])
        dict_matrix[-1, idx] = reduced_costs[idx-1]

    # Armamos cada fila del diccionario
    str_dict = []
    ls_vars = basic_vars + [-1]
    for idx, var in enumerate(ls_vars):
        try:
            row = [var_names[var], ' = ']
        except KeyError:
            row = ['z', '=']

        for col, value in enumerate(dict_matrix[idx, :]):
            if value > 0 and col > 0:
                if value == 1:
                    row.append(f'+{var_names[non_basic_vars[col-1]]}')
                else:
                    row.append(f'+{nsimplify(value)}{var_names[non_basic_vars[col-1]]}')
            elif value > 0 and col == 0:
                row.append(f'{nsimplify(value)}')
            elif value < 0 and col > 0:
                if value == -1:
                    row.append(f'-{var_names[non_basic_vars[col-1]]}')
                else:
                    row.append(f'{nsimplify(value)}{var_names[non_basic_vars[col-1]]}')
            elif value < 0 and col == 0:
                row.append(f'{nsimplify(value)}')
            elif np.isclose(value, 0):
                row.append(' ')
        row_str = ' &'.join(row) + '\\\\'
        str_dict.append(row_str)

    str_dict[-2] += '\\hline'
    align = '{rc' + 'l'*(len(non_basic_vars)+1) + '}'
    print('\\[')
    print(f'\\begin{{array}}{align}')
    for line in str_dict:
        print(line)
    print('\\end{array}')
    print('\\]')
    print('\\vspace{1cm}')


def simplex_iteration(c, A, b, basic_vars, silent=True):
    """
    Realiza una iteración del método SIMPLEX.
    :param c: vector con los coeficientes de las variables en la función objetivo
    :type c: np.array
    :param A: matriz del problema
    :type A: np.array
    :param b: vector con los valores del lado derecho de las restricciones
    :type b: np.array
    :param basic_vars: índices de las variables básicas en la solución básica factible actual
    :type basic_vars: list[int]
    :return: diccionario con el valor de las variables básicas en el óptimo y un indicador de si se alcanzó el óptimo.
    :rtype: tuple[None | dict, bool]
    :raises: UnboundedProblem si detecta que el problema es no acotado.
    """
    non_basic_vars = [i for i in range(A.shape[1]) if i not in basic_vars]
    basic_vars.sort()

    # Submatriz de A correspondiente a las variables básicas
    B = A[:, basic_vars]

    # Submatriz de A correspondiente a las variables no básicas
    R = A[:, non_basic_vars]

    # Valores de las variables básicas
    bvar_vals = np.linalg.solve(B, b)

    # Vectores de coeficientes de las variables básicas y de las no básicas
    cB = c[basic_vars]
    cR = c[non_basic_vars]

    # Cálculo de costo reducido de las variables no básicas
    # cr = cR - cB @ (np.linalg.inv(B) @ R)
    pi = np.linalg.solve(B.T, cB)
    cr = cR - pi @ R

    if not silent:
        print('B: \n', B)
        print('B-1: \n', np.linalg.inv(B))
        print('R: \n', R)
        print('bvar: \n', bvar_vals)
        print('cB: \n', cB)
        print('cR: \n', cR)
        print('cr: \n', cr)


    # Si los costos reducidos son todos no positivos, se alcanzó un óptimo
    if np.all(cr <= 0):
        bvars_values = {i: bvar_vals[j] for j, i in enumerate(basic_vars)}
        return bvars_values, True

    # Obtenemos la variable que entrará a la base: la que tenga el máximo costo reducido
    nbvar_to_enter = non_basic_vars[np.argmax(cr)]

    # Calculamos qué variable sale de la base: la que imponga la cota más ajustada para el crecimiento de la variable
    # que entrará a la base:
    nbA = np.linalg.solve(B, A[:, nbvar_to_enter])

    # Si los valores de ese vector son todos no pistivos, se trata de un problema no acotado:
    if np.all(nbA <= 0):
        raise UnoundedProblem('Problema no acotado!')

    with np.errstate(divide='ignore'):
        # Si se divide por 0, numpy retorna inf, y como busco el mínimo, no me interesa.
        idx_bvar_exit = min((i for i in range(len(bvar_vals)) if nbA[i] > 0), key=lambda s: bvar_vals[s] / nbA[s])
        # idx_bvar_exit = np.argmin(bvar_vals / nbA)

    if not silent:
        print('A_i: ', nbA)
        print('\n\n')

    # Eliminamos de la base a la variable saliente y agregamos a la entrante
    del basic_vars[idx_bvar_exit]
    basic_vars.append(nbvar_to_enter)

    return None, False


def simplex(c, A, b, silent=True, var_names=None, initial_basis=None):
    """
    Resuelve el problema de Programación Lineal (con objetivo de maximizar) utilizando SIMPLEX. Alerta si el problema
    es no acotado o infactible.
    Imprime en pantalla el valor de las variables básicas en la solución básica óptima hallada y su valor
    correspondiente en la función objetivo.
    :param c: vector con los coeficientes de las variables en la función objetivo
    :type c: np.array
    :param A: matriz del problema estandarizado
    :type A: np.array
    :param b: vector con los valores del lado derecho de las restricciones
    :type b: np.array
    :param silent: si toma el valor True, no se imprimen los resultados de los cálculos de cada iteración de SIMPLEX.
    :type silent: bool
    :param var_names: diccionario que mapea el índice de cada columna de A con el nombre de su correspondiente
    variable. Este argumento es opcional. Si es None, no se imprime el diccionario de cada iteración. Si es un
    diccionario, se setea a silent=True (independientemente del valor de silent introducido) y se imprime el
    diccionario de cada iteración.
    :type var_names: None | dict[int,str]
    :param initial_basis: lista de indices de las columnas de A correspondientes a las variables de una solucion básica
    factible inicial. Si es None, se intenta buscar la solucion basica factible trivial (variables slack) y si no se
    encuentra, se corre la Fase I de SIMPLEX.
    :type initial_basis: None | list[int]
    """
    # Chequeamos si el problema proviene de estandarizar un problema donde todas las restricciones venían dadas por
    # <= con b no negativo. Si es el caso, una solución básica factible inicial se puede obtener considerando como
    # variables básicas a las variables slack. Si no es el caso, se lleva adelante la Fase I de SIMPLEX para hallar una
    # solución básica factible inicial.
    if initial_basis is None:
        basic_vars = trivial_feasible_basic_sol(A)  # en basic_vars se guarda el índice de las variables básicas
        if basic_vars is None:
            basic_vars = phase1(A, b)
    else:
        basic_vars = initial_basis

    if var_names is not None:
        silent = True
        print_dictionary(basic_vars, var_names, A, b, c)

    # Iteramos hasta alcanzar el óptimo
    opt_achieved = False
    while not opt_achieved:
        opt_bvar_values, opt_achieved = simplex_iteration(c, A, b, basic_vars, silent)
        if var_names is not None:
            print_dictionary(basic_vars, var_names, A, b, c)

    # Imprimimos el valor de la función objetivo en el óptimo y el valor de las variables básicas de la solución óptima:
    xopt = np.zeros(A.shape[1])

    print('Valor óptimo de las variables básicas: ')
    for k, v in opt_bvar_values.items():
        xopt[k] = v
        if var_names is None:
            print(f'x_{k+1} = {v}')
        else:
            print(f'{var_names[k]} = {v}')
    print('Valor óptimo de la función objetivo: ', c @ xopt)


def ejemplo():
    A = np.array([
                  [1, 1, 1, -1, 0, 1, 0],
                  [1, 0, 2, 0, 1, 0, 0],
                  [-1, 1, 1, 0, 0, 0, 1]])
    b = np.array([4, 6, 2])
    c = np.array([2, 1, 1, 0, 0, -1000, -1000])
    var_names = {0: 'x_1',
                 1: 'x_2',
                 2: 'x_3',
                 3: 'w_1',
                 4: 'w_2',
                 5: 'a_1',
                 6: 'a_2',
                 }
    init_base = [4, 5, 6]
    simplex(c, A, b, var_names=var_names, initial_basis=init_base)
