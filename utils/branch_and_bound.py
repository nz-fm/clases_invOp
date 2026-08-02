"""
Dado un problema de Programación Lineal Entera en dos variables, la fución `branch_and_bound` genera el árbol de Branch
and Bound. El propósito de esta función es ver rápidamente si un ejercicio de Branch and Bound requiere la resolución
de muchos subproblemas (es decir, si el ejercicio resultaría ser muy largo).
Requiere tener instalado GraphViz : https://graphviz.org/
"""

import matplotlib.pyplot as plt
import networkx as nx
import numpy as np
from docplex.mp.model import Model
from networkx.drawing.nx_pydot import graphviz_layout

# Full path a dot.exe de Graphviz\bin. Por ejemplo `Z:\Programs\Graphviz\bin\dot.exe` (depende de donde lo hayas
# instalado)
GRAPHVIZ_PATH = r''

def solve_model(A, b, c, ineq, obj):
    """
    Resuelve el problma correspondiente a la relajación lineal.
    A: matriz del problema (tiene que incluir si las variables son >= 0)
    b: vector de términos independientes
    c: coeficientes de la f.o.
    ineq: lista con desigualdades: {'g': >=, 'l': <=, 'e': =}
    obj: objetivo: {'max', 'min'}
    force_branch: None por defecto, se puede poner 1 o 2 si quiero forzar a que el primer branch sea en x1 o en x2,
    respectivamente.
    """

    model = Model()
    nvars = A.shape[1]
    xidx = range(1, nvars+1)
    x = model.continuous_var_dict(xidx, lb=-model.infinity, ub=model.infinity, name='X')

    # Se agregan las restricciones
    for row in range(A.shape[0]):
        if ineq[row] == 'e':
            model.add_constraint(model.scal_prod_f(x, lambda key: A[row, key-1]) == b[row])
        elif ineq[row] == 'g':
            model.add_constraint(model.scal_prod_f(x, lambda key: A[row, key-1]) >= b[row])
        elif ineq[row] == 'l':
            model.add_constraint(model.scal_prod_f(x, lambda key: A[row, key-1]) <= b[row])
        else:
            raise ValueError('Simbolo de desigualdad invalido')

    # Se agrega la funcion objetivo:
    model.set_objective(obj, model.scal_prod_f(x, lambda key: c[key-1]))

    # Se optimiza
    sol = model.solve()

    if sol is None:
        return None, None
    else:
        xsol = sol.get_value_dict(x, True)
        xsol = np.array([xsol[i] for i in range(1, nvars + 1)])
        zopt = sol.get_objective_value()
        return xsol, zopt


def non_int_indices(x):
    return np.flatnonzero(np.logical_not(np.isclose(x, np.round(x, 0))))


def add_branch_problem(problem_params, branch_on, problem_stack, newineq, newb, father):
    """ Apila el nuevo subproblema a resolver """
    A, b, c, ineq, obj, _ = problem_params
    newrow = np.array([[1, 0]])*(1-branch_on) + np.array([[0, 1]])*branch_on
    newA = np.concatenate((A, newrow), axis=0)
    newb = np.append(b, newb)
    newineq_ = ineq + newineq
    problem_stack.append((newA, newb, c, newineq_, obj, father))


def better_than_incumbent(zopt, obj, zinc):
    return (obj == 'min' and zopt <= zinc) or (obj == 'max' and zopt >= zinc)


def branch_and_bound(A, b, c, ineq, obj, force_branch=None):
    """
    A: matriz del problema (tiene que incluir si las variables son >= 0)
    b: vector de términos independientes
    c: coeficientes de la f.o.
    ineq: lista con desigualdades: {g: >=, l: <=, e: =}
    obj: objetivo: {max, min}
    force_branch: None por defecto, se puede poner 1 o 2 si quiero forzar a que el primer branch sea en x1 o en x2
    """
    bb_tree = nx.DiGraph()
    nlabels = []

    problem_stack = [(A, b, c, ineq, obj, None)]

    pcounter = 0
    z_inc = np.inf if obj == 'min' else -np.inf      # Valor incumbente
    while problem_stack:
        problem_params = problem_stack.pop()
        pcounter += 1
        if problem_params[-1] is None:
            bb_tree.add_node(1)
        else:
            bb_tree.add_edge(problem_params[-1], pcounter)
        xopt, zopt = solve_model(*problem_params[:-1])
        if xopt is not None:
            label = '\n'.join([f'S{pcounter}', f'x* = {xopt}', f'z* = {zopt}'])
            nint_indices = non_int_indices(xopt)
            if len(nint_indices) > 0 and better_than_incumbent(zopt, obj, z_inc):
                if pcounter == 1 and force_branch is not None:
                    branch_on = force_branch if force_branch in nint_indices else nint_indices[0]
                else:
                    branch_on = np.random.choice(nint_indices)
                add_branch_problem(problem_params, branch_on, problem_stack, 'g', np.ceil(xopt[branch_on]), pcounter)
                add_branch_problem(problem_params, branch_on, problem_stack, 'l', np.floor(xopt[branch_on]), pcounter)
            elif not len(nint_indices) and better_than_incumbent(zopt, obj, z_inc):
                z_inc = zopt
        else:
            label = '\n'.join([f'S{pcounter}', 'INFACTIBLE'])
        nlabels.append(label)

    # Grafica el árbol de B&B
    try:
        pos = graphviz_layout(bb_tree, prog=GRAPHVIZ_PATH)
    except FileNotFoundError:
        pos = graphviz_layout(bb_tree)
    nx.draw_networkx(bb_tree, pos=pos, with_labels=False, node_shape='s', node_size=3000, node_color='white')
    nodenames = {n: nlabels[n-1] for n in bb_tree.nodes()}
    nx.draw_networkx_labels(bb_tree, pos=pos, labels=nodenames)
    plt.show()
