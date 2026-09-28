import random
import networkx as nx
import matplotlib.pyplot as plt

def generate_planar_graph(n, seed=None):
    try:
        from scipy.spatial import Delaunay
        import numpy as np

        rng = np.random.default_rng(seed)
        points = rng.random((n, 2))
        tri = Delaunay(points)

        G = nx.Graph()
        G.add_nodes_from(range(n))
        for simplex in tri.simplices:
            for i in range(3):
                u, v = simplex[i], simplex[(i + 1) % 3]
                if not G.has_edge(u, v):
                    G.add_edge(u, v)

        if seed is not None:
            random.seed(seed)
        edges = list(G.edges())
        for e in edges:
            if random.random() < 0.3:
                G.remove_edge(*e)

        return G

    except ImportError:
        for attempt in range(1000):
            max_edges = min(3 * n - 6, n * (n - 1) // 2)
            m = random.randint(n - 1, max_edges)
            G = nx.gnm_random_graph(n, m, seed=seed)
            is_planar, _ = nx.check_planarity(G)
            if is_planar:
                return G
        raise RuntimeError("Не удалось сгенерировать планарный граф за 1000 попыток")


def check_and_draw(G, title_prefix=""):
    is_planar, embedding = nx.check_planarity(G)

    print(f"{title_prefix}Вершин: {G.number_of_nodes()}, рёбер: {G.number_of_edges()}")
    print(f"{title_prefix}Граф планарен: {is_planar}")

    plt.figure(figsize=(9, 7))

    if is_planar:
        print(f"{title_prefix}Комбинаторное вложение:")
        for v in G.nodes():
            print(f"   {v}: {list(embedding.neighbors_cw_order(v))}")

        pos = nx.planar_layout(G)
        nx.draw(
            G,
            pos=pos,
            with_labels=True,
            node_color='lightblue',
            edge_color='gray',
            node_size=500,
            font_size=10
        )
        plt.title(f"{title_prefix}Планарная укладка графа")
    else:
        nx.draw(
            G,
            with_labels=True,
            node_color='salmon',
            edge_color='gray',
            node_size=500,
            font_size=10
        )
        plt.title(f"{title_prefix}Граф непланарен")

    plt.show()

if __name__ == "__main__":
    n = 12
    seed = None

    # Генерируем случайный планарный граф
    G = generate_planar_graph(n, seed)

    # Проверяем и рисуем
    check_and_draw(G, title_prefix="Сгенерированный граф. ")