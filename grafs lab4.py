import networkx as nx
import matplotlib.pyplot as plt

def hungarian_min(cost):
    n = len(cost)
    if n == 0:
        return 0, []

    INF = 10**18

    u = [0] * (n + 1)
    v = [0] * (n + 1)
    p = [0] * (n + 1)
    way = [0] * (n + 1)

    for i in range(1, n + 1):
        p[0] = i
        j0 = 0

        minv = [INF] * (n + 1)
        used = [False] * (n + 1)

        while True:
            used[j0] = True
            i0 = p[j0]

            delta = INF
            j1 = 0

            for j in range(1, n + 1):
                if not used[j]:
                    cur = cost[i0 - 1][j - 1] - u[i0] - v[j]
                    if cur < minv[j]:
                        minv[j] = cur
                        way[j] = j0
                    if minv[j] < delta:
                        delta = minv[j]
                        j1 = j

            for j in range(0, n + 1):
                if used[j]:
                    u[p[j]] += delta
                    v[j] -= delta
                else:
                    minv[j] -= delta

            j0 = j1
            if p[j0] == 0:
                break

        while True:
            j1 = way[j0]
            p[j0] = p[j1]
            j0 = j1
            if j0 == 0:
                break

    assignment = [-1] * n
    for j in range(1, n + 1):
        if p[j] != 0:
            assignment[p[j] - 1] = j - 1

    min_cost = sum(cost[i][assignment[i]] for i in range(n))
    return min_cost, assignment


def hungarian(cost, maximize=False):
    n = len(cost)
    if n == 0:
        return 0, []

    if maximize:
        max_val = max(max(row) for row in cost)
        work = [[max_val - x for x in row] for row in cost]
    else:
        work = [row[:] for row in cost]

    min_val = min(min(row) for row in work)
    if min_val < 0:
        work = [[x - min_val for x in row] for row in work]

    _, assignment = hungarian_min(work)

    total = sum(cost[i][assignment[i]] for i in range(n))
    return total, assignment


def visualize_matching(cost, assignment, maximize=False, title=None):
    n = len(cost)

    G = nx.Graph()
    left_nodes = [f"L{i}" for i in range(n)]
    right_nodes = [f"R{j}" for j in range(n)]

    G.add_nodes_from(left_nodes, bipartite=0)
    G.add_nodes_from(right_nodes, bipartite=1)

    for i in range(n):
        for j in range(n):
            G.add_edge(f"L{i}", f"R{j}", weight=cost[i][j])

    pos = {}
    for i in range(n):
        pos[f"L{i}"] = (0, -i)
        pos[f"R{i}"] = (1, -i)

    edges_all = list(G.edges())
    nx.draw_networkx_nodes(G, pos, node_color='lightblue', node_size=500)
    nx.draw_networkx_labels(G, pos)
    nx.draw_networkx_edges(G, pos, edgelist=edges_all,
                           edge_color='lightgray', width=1, alpha=0.6)

    matching_edges = [(f"L{i}", f"R{assignment[i]}") for i in range(n)]
    nx.draw_networkx_edges(G, pos, edgelist=matching_edges,
                           edge_color='red', width=3)

    labels = { (f"L{i}", f"R{assignment[i]}"): cost[i][assignment[i]]
               for i in range(n) }
    nx.draw_networkx_edge_labels(G, pos, edge_labels=labels, font_color='red')

    total = sum(cost[i][assignment[i]] for i in range(n))
    if title is None:
        if maximize:
            title = f"Максимальное паросочетание, сумма = {total}"
        else:
            title = f"Минимальное паросочетание, сумма = {total}"

    plt.title(title)
    plt.axis('off')
    plt.show()

if __name__ == "__main__":
    cost = [
        [10, 20, 30],
        [30, 30, 30],
        [30, 30, 20],
    ]


    total_min, assign_min = hungarian(cost, maximize=False)
    print("Минимум:", total_min, assign_min)
    visualize_matching(cost, assign_min, maximize=False)

    total_max, assign_max = hungarian(cost, maximize=True)
    print("Максимум:", total_max, assign_max)
    visualize_matching(cost, assign_max, maximize=True)