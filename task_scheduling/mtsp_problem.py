#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Copyright (c) 2015, lounick and decabyte
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:
#
# * Redistributions of source code must retain the above copyright notice, this
#   list of conditions and the following disclaimer.
#
# * Redistributions in binary form must reproduce the above copyright notice,
#   this list of conditions and the following disclaimer in the documentation
#   and/or other materials provided with the distribution.
#
# * Neither the name of task_scheduling nor the names of its
#   contributors may be used to endorse or promote products derived from
#   this software without specific prior written permission.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
# AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
# IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
# DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE
# FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL
# DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR
# SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER
# CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY,
# OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
# OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

"""
Multiple traveling salesmen (mTSP) problem solver.
"""

from __future__ import (absolute_import, division, print_function, unicode_literals)

import numpy as np
import gurobipy


def mtsp_solver(cost, salesmen=1, min_cities=None, max_cities=None, **kwargs):
    """
    Multiple traveling salesmen MILP solver using the Gurobi MILP optimiser.

    :rtype : Returns tuple with the routes for each salesman, the objective value, and a model object.
    :param cost: Cost matrix for travelling from point to point.
    :param salesmen: Number of salesmen taking part in the solution.
    :param min_cities: Optional parameter of minimum cities to be visited by each salesman.
    :param max_cities: Optional parameter of maximum cities to be visited by each salesman.
    """
    n = cost.shape[0]

    if min_cities is None:
        K = 2
    else:
        K = min_cities

    if max_cities is None:
        L = n
    else:
        L = max_cities

    m = gurobipy.Model()

    # Create variables
    e_vars = {}
    for i in range(n):
        for j in range(n):
            e_vars[i, j] = m.addVar(obj=cost[i, j], vtype=gurobipy.GRB.BINARY, name='e' + str(i) + '_' + str(j))
    m.update()

    for i in range(n):
        e_vars[i, i].ub = 0

    u_vars = {}
    for i in range(n):
        u_vars[i] = m.addVar(lb=0, ub=L, vtype=gurobipy.GRB.INTEGER, name='u' + str(i))
    m.update()

    # Add degree-2 constraint, and forbid loops
    m.addConstr(gurobipy.quicksum(e_vars[0, i] for i in range(1, n)) == salesmen)
    m.addConstr(gurobipy.quicksum(e_vars[i, 0] for i in range(1, n)) == salesmen)

    for i in range(1, n):
        m.addConstr(gurobipy.quicksum(e_vars[i, j] for j in range(n) if i != j) == 1)

    for i in range(1, n):
        m.addConstr(gurobipy.quicksum(e_vars[j, i] for j in range(n) if i != j) == 1)

    for i in range(1, n):
        m.addConstr(u_vars[i] + (L - 2) * e_vars[0, i] - e_vars[i, 0] <= L - 1)

    for i in range(1, n):
        m.addConstr(u_vars[i] + e_vars[0, i] + (2 - K) * e_vars[i, 0] >= 2)

    for i in range(1, n):
        m.addConstr(e_vars[0, i] + e_vars[i, 0] <= 1)

    for i in range(1, n):
        for j in range(1, n):
            if i != j:
                m.addConstr(u_vars[i] - u_vars[j] + L * e_vars[i, j] + (L - 2) * e_vars[j, i] <= L - 1)
    m.update()

    m._vars = e_vars
    m._uvars = u_vars
    m.params.OutputFlag = int(kwargs.get('output_flag', 0))
    m.params.TimeLimit = float(kwargs.get('time_limit', 60.0))
    m.optimize()

    solution = m.getAttr('X', e_vars)
    selected = [(i, j) for i in range(n) for j in range(n) if solution[i, j] > 0.5]
    routes = []

    for i in range(salesmen):
        routes.append([])
        next_city = 0
        finished = False

        while not finished:
            for j in range(len(selected)):
                if selected[j][0] == next_city:
                    routes[i].append(next_city)
                    next_city = selected[j][1]

                    selected.pop(j)
                    break

            if next_city == 0:
                finished = True

    return routes, m.objVal, m


def main():
    import matplotlib.pyplot as plt
    import task_scheduling.utils as tsu

    nodes = tsu.generate_nodes()
    cost = tsu.calculate_distances(nodes)
    salesmen = np.random.randint(2, 4)

    solution, objective, _ = tsu.solve_problem(mtsp_solver, cost, salesmen=salesmen)

    fig, ax = tsu.plot_problem(nodes, solution, objective)
    plt.show()


if __name__ == '__main__':
    main()
