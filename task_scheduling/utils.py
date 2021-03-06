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

"""Utility Module

This module provides helper functions to be used with task_scheduling problems.

Notes
-----
Documention of this project is following the Numpy guidelines. These can be seen in action in the example file from the
Napoleon project (`example_numpy.py`_).


.. _example_numpy.py:
    http://sphinxcontrib-napoleon.readthedocs.org/en/latest/example_numpy.html
"""

from __future__ import (absolute_import, division, print_function, unicode_literals)

import time
import numpy as np
import matplotlib as mpl
import matplotlib.pyplot as plt

from mpl_toolkits.mplot3d import Axes3D

np.set_printoptions(precision=3, suppress=True)
np.random.seed(int(time.time()))


def generate_nodes(n=20, lb=-50, ub=50, dims=2, **kwargs):
    """Generate a random set of `n` nodes of `dims` coordinates using a discrete uniform distribution (lb, ub].

    Parameters
    ----------
    n
    lb
    ub
    dims
    kwargs

    Returns
    -------
    nodes: ndarray (n, dims)
        List of randomly generates coordinates for problem nodes.

    Examples
    --------
    This function is used to generate a new random set of nodes to be used as input for a scheduling problem.

    >>> import numpy as np
    >>> np.random.seed(42)
    >>> nodes = generate_nodes(n=2, lb=-10, up=10, dims=2)
    >>> nodes.flatten()
    array([28, 41, 18,  4])

    """
    return np.random.randint(lb, ub, (n, dims))


def calculate_distances(nodes):
    n = np.atleast_2d(nodes).shape[0]
    distances = np.zeros((n, n))

    for k in xrange(n):
        for p in xrange(n):
            distances[k, p] = np.linalg.norm(nodes[k, :] - nodes[p, :])

    return distances


def solve_problem(solver, cost, **kwargs):
    """Generic wrapper for library solvers. Useful for command-line examples or tests.

    Parameters
    ----------
    solver
    cost
    kwargs

    Returns
    -------
    solution: list
        list of node indexes that form a solution

    solution: float
        value of the objective for the found solution

    model: object
        model object after running the solver
    """
    st = time.time()
    solution, objective, model = solver(cost, **kwargs)
    dt = time.time() - st

    print('Solving problem using [{}] solver\n'.format(solver.__name__))
    print('Time to Solve: %.2f secs' % dt)
    print('Objective: %.3f' % objective)
    print('Solution: %s\n' % solution)

    return solution, objective, model


def _set_plot_style():
    """Set the global matplotlib using the project's default style.

    Notes
    -----
    This configuration affects all the tests and the examples included in this package.
    """
    if 'bmh' in mpl.style.available:
        mpl.style.use('bmh')

    mpl.rcParams['figure.figsize'] = _get_figsize(scale=2.0)
    # mpl.rcParams[''] = 'tight'


def _get_figsize(scale=1.0):
    """Calculate figure size using aestetic ratio.

    Parameters
    ----------
    scale : float
        Scaling parameter from basic aspect (6.85:4.23).

    Returns
    -------
    figsize : tuple
        A 2-element tuple (w, h) defining the width and height of a figure.

    Examples
    --------
    This function is used to configure matplotlib.

    >>> import numpy as np
    >>> np.allclose(_get_figsize(1.0), (6.85, 4.23), atol=0.1)
    True
    """
    fig_width_pt = 495.0                              # Get this from LaTeX using \the\textwidth
    inches_per_pt = 1.0 / 72.27                       # Convert pt to inch

    golden_mean = (np.sqrt(5.0) - 1.0) / 2.0

    fig_width = fig_width_pt * inches_per_pt * scale  # width in inches
    fig_height = fig_width * golden_mean              # height in inches

    return (fig_width, fig_height)


def plot_problem(nodes, solution, objective):
    """Plot the results of a problem in 2D coordinates (X-Y).

    Parameters
    ----------
    nodes
    solution
    objective

    Returns
    -------
    fig: object
        figure object

    ax: object
        axes object
    """
    # init plot
    _set_plot_style()
    fig, ax = plt.subplots()

    # plot vertexes
    ax.plot(nodes[:, 1], nodes[:, 0], 'o', ms=8, label='nodes')
    # ax.plot(nodes[:, 0], nodes[:, 1], 'o', ms=8, label='nodes')

    # # add labels
    # for n in xrange(len(idx)):
    #     x, y = nodes[n, 1], nodes[n, 0]
    #     xt, yt = x - 0.10 * np.abs(x), y - 0.10 * np.abs(y)
    #
    #     ax.annotate('#%d' % n, xy=(x, y), xycoords='data', xytext=(xt,yt))

    # normalize solution(s)
    indexes = []

    if len(solution) > 0:
        if type(solution[0]) == list:
            indexes.extend(solution)
        else:
            indexes.append(solution)

    # plot solution(s)
    for n, idx in enumerate(indexes):
        # route plots
        route = nodes[idx, :]
        # ax.plot(route[:, 0], route[:, 1], '--', alpha=0.8, label='route #{}'.format(n))
        ax.plot(route[:, 1], route[:, 0], '--', alpha=0.8, label='route #{}'.format(n))

        # add route order
        for k, n in enumerate(idx):
            # x, y = nodes[n, 0], nodes[n, 1]
            x, y = nodes[n, 1], nodes[n, 0]
            xt, yt = x + 0.05 * np.abs(x), y + 0.05 * np.abs(y)
            xt, yt = x + 0.15, y + 0.15
            ax.annotate(str(k), xy=(x, y), xycoords='data', xytext=(xt, yt))

    # adjust plot features
    ax.axis('equal')
    xlim = ax.get_xlim()
    ylim = ax.get_ylim()
    xnew =  (xlim[0] - np.abs(xlim[0] * 0.05), xlim[1] + np.abs(xlim[1] * 0.05))
    ynew =  (ylim[0] - np.abs(ylim[0] * 0.05), ylim[1] + np.abs(ylim[1] * 0.05))
    # xnew =  (xlim[0] - 2, xlim[1] + 2)
    # ynew =  (ylim[0] - 1, ylim[1] + 1)
    ax.set_xlim(xnew)
    ax.set_ylim(ynew)

    ax.legend(loc='best')
    ax.xaxis.set_minor_locator(mpl.ticker.AutoMinorLocator(2))
    ax.yaxis.set_minor_locator(mpl.ticker.AutoMinorLocator(2))
    ax.grid(which='minor')

    ax.set_xlabel('X (m)')
    ax.set_ylabel('Y (m)')
    ax.set_title('Problem Solution')

    return fig, ax


def plot_problem_3d(nodes, solution, cost_total):
    """Plot the results of a problem in 3D coordinates.

    Parameters
    ----------
    nodes
    solution
    cost_total

    Returns
    -------
    fig: object
        figure object

    ax: object
        axes object
    """
    # init plot
    _set_plot_style()
    fig, ax = plt.subplots(subplot_kw=dict(projection='3d'))

    nodes = np.atleast_2d(nodes)

    # plot vertexes
    ax.scatter(nodes[:, 1], nodes[:, 0], nodes[:,2], label='nodes')

    # # add labels
    # for n in xrange(len(idx)):
    #     x, y = nodes[n, 1], nodes[n, 0]
    #     xt, yt = x - 0.10 * np.abs(x), y - 0.10 * np.abs(y)
    #
    #     ax.annotate('#%d' % n, xy=(x, y), xycoords='data', xytext=(xt,yt))

    # normalize solution(s)
    indexes = []

    if len(solution) > 0:
        if type(solution[0]) == list:
            indexes.extend(solution)
        else:
            indexes.append(solution)

    # plot solution(s)
    for n, idx in enumerate(indexes):
        # route plots
        route = nodes[idx, :]
        ax.plot(nodes[idx, 1], nodes[idx, 0], route[:, 2], '--', alpha=0.8, label='#{}'.format(n))

        # # add route order
        # for k, n in enumerate(idx):
        #     x, y, z = nodes[n, 1], nodes[n, 0], nodes[n, 2]
        #     xt, yt, zt = x + 0.05 * np.abs(x), y + 0.05 * np.abs(y), z + 0.05 * np.abs(z)
        #
        #     ax.annotate(str(k), xy=(x, y), xycoords='data', xytext=(xt, yt))

    # adjust plot features
    ax.legend(loc='best')
    ax.xaxis.set_minor_locator(mpl.ticker.AutoMinorLocator(2))
    ax.yaxis.set_minor_locator(mpl.ticker.AutoMinorLocator(2))
    ax.zaxis.set_minor_locator(mpl.ticker.AutoMinorLocator(2))
    ax.grid(which='minor')

    ax.set_xlabel('X (m)')
    ax.set_ylabel('Y (m)')
    ax.set_zlabel('Z (m)')
    ax.set_title('Problem Solution')

    return fig, ax

def plot_problem_correlation_circles(nodes, solution, objective, max_range=2.0):
    import matplotlib.patches as mpatches
    from matplotlib.collections import PatchCollection

    fig, ax = plot_problem(nodes, solution, objective)

    ax.hold(True)

    indexes = []

    if len(solution) > 0:
        if type(solution[0]) == list:
            indexes.extend(solution)
        else:
            indexes.append(solution)

    circles = []
    for n, idx in enumerate(indexes):
        # route plots
        route = nodes[idx, :]

        for node in route[9:10]:#len(route) - 1]:
            # print("Node: {0}".format(node))
            circle = mpatches.Circle((node[1],node[0]), radius=max_range, fill=False, edgecolor='blue', linestyle='dotted', lw=1.5, label='Max sensor range')
            circles.append(circle)

    # collection = PatchCollection(circles, cmap=plt.cm.hsv, alpha=0.3)
    # ax.add_collection(collection)
    for p in circles:
        ax.add_patch(p)
    return fig, ax

def plot_problem_correlation_gradient(nodes, solution, objective, max_range=2.0):
    def cor(x, y, centre, max_range):
        alpha = -np.log(0.01)/max_range
        val = np.exp(-alpha*np.sqrt((centre[1]-x)**2 + (centre[0]-y)**2))
        # for i in range(len(val)):
        #     for j in range(len(val[i])):
        #         if val[i][j] < 0.001:
        #             val[i][j] = 0
        return val

    fig, ax = plot_problem(nodes, solution, objective)

    ax.hold(True)

    (xmin, xmax) = ax.get_xlim()
    (ymin, ymax) = ax.get_ylim()
    extent = xmin, xmax, ymin, ymax
    dx, dy = 0.01, 0.01

    indexes = []

    if len(solution) > 0:
        if type(solution[0]) == list:
            indexes.extend(solution)
        else:
            indexes.append(solution)

    for n, idx in enumerate(indexes):
        # route plots
        route = nodes[idx, :]
        ims = []
        x = np.arange(xmin, xmax, dx)
        y = np.arange(ymax, ymin, -dy)
        X, Y = np.meshgrid(x, y)
        Z = cor(X, Y, route[1], max_range)
        for node in route[1:len(route)-1]:
            Z += cor(X, Y, node, max_range)
            # plt.cm.jet
        ax.imshow(Z, cmap="Blues", alpha=.9, interpolation='bilinear',extent=extent)
    # ax.legend(loc=(0.6,0.9))
    # fig.set_dpi(300)


    return fig, ax

def generate_grid(x_size, y_size=None, idx_start=[0,0]):
    import math
    if y_size is None:
        y_size = x_size

    nodes = []
    nodes.append(idx_start)
    idx_finish = [idx_start[0]+x_size+1, idx_start[1]]
    y_2_floor = int(math.floor(y_size/2.0))
    y_2_ceil = int(math.ceil(y_size/2.0))
    y_start_ceil = int(math.ceil(idx_start[1]))
    for i in range(int(idx_start[0]+1), int(idx_start[0]+x_size+1)):
        for j in range(-y_2_floor + y_start_ceil, y_2_ceil + y_start_ceil):
            nodes.append([i,j])
    nodes.append(idx_finish)
    return nodes

