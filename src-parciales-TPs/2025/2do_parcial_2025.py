from IO.docencia import simplex
from IO.model_to_latex import branch_and_bound
import numpy as np
from docplex.mp.model import Model


def ejercicio_1():
    # Fase I
    print('------------------------ FASE I ---------------------------------------------')
    A = np.array([[1, 0, 1, 1, 0, 0],
                  [2, -1, 1, 0, 0, 1],
                  [1, -1, 0, 0, 1, 0]])
    b = np.array([3, 2, 2])
    # c = np.array([4, 2, 1, 0, 0, 0])
    var_names = {0: 'y_1',
                 1: 'y_2',
                 2: 'y_3',
                 3: 'w_1',
                 4: 'w_2',
                 5: 'a_1',
                 }
    c = np.array([0, 0, 0, 0, 0, -1])
    init_base = [3, 4, 5]
    # init_base = [0, 3, 4]
    simplex(c, A, b, var_names=var_names, initial_basis=init_base)

    # Fase II
    print('------------------------ FASE II ---------------------------------------------')
    A = np.array([[1, 0, 1, 1, 0],
                  [2, -1, 1, 0, 0],
                  [1, -1, 0, 0, 1]])
    b = np.array([3, 2, 2])
    c = np.array([4, 2, 1, 0, 0])
    var_names = {0: 'y_1',
                 1: 'y_2',
                 2: 'y_3',
                 3: 'w_1',
                 4: 'w_2',
                 }
    init_base = [0, 3, 4]
    simplex(c, A, b, var_names=var_names, initial_basis=init_base)


def corroboro_ej_1():
    # Planteo y resuelvo el primal
    primal = Model('Primal')
    x = primal.continuous_var_dict([1, 2, 3], lb=-primal.infinity, ub=[0, primal.infinity, 0], name='X')
    primal.add_constraint(x[1] + 2*x[2] + x[3] <= -4)
    primal.add_constraint(-x[2] - x[3] <= -2)
    primal.add_constraint(x[1] + x[2] <= -1)
    primal.maximize(3*x[1] + 2*x[2] + 2*x[3])
    primal_sol = primal.solve()
    print(primal_sol)

    # Planteo y resuelvo el dual
    dual = Model('Dual')
    y = dual.continuous_var_dict([1, 2, 3], name='Y')
    dual.add_constraint(y[1]+y[3] <=3)
    dual.add_constraint(2*y[1]-y[2]+y[3] == 2)
    dual.add_constraint(y[1]-y[2] <=2)
    dual.minimize(-4*y[1]-2*y[2]-y[3])
    dual_sol = dual.solve()
    print(dual_sol)


def ejercicio_3():
    A = np.array([[2, 1],
                  [4, 9],
                  [4, -5],
                  ])
    b = np.array([8, 24, -4])
    c = np.array([1, 3])
    ineq = 'llg'
    for i in (0, 1):
        branch_and_bound(A, b, c, ineq, 'max', i)


if __name__ == '__main__':
    ejercicio_3()