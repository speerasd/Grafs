import math
import sys
from collections import deque
import matplotlib.pyplot as plt

class Graph:
    def __init__(self):
        self.adj = {}
        self.order = []

    def add_vertex(self, v):
        if v not in self.adj:
            self.adj[v] = set()
            self.order.append(v)

    def add_edge(self, u, v):
        if u == v:
            return
        self.add_vertex(u)
        self.add_vertex(v)
        self.adj[u].add(v)
        self.adj[v].add(u)

    def vertices(self):
        return list(self.order)

    def neighbors(self, v):
        return self.adj[v]

    def edge_count(self):
        return sum(len(s) for s in self.adj.values()) // 2

    def __len__(self):
        return len(self.adj)

    def __iter__(self):
        return iter(self.order)


def load(path):
    g = Graph()
    with open(path, encoding="utf-8") as fh:
        for raw in fh:
            line = raw.strip()
            if not line or line.startswith("#"):
                continue
            parts = line.split()
            if len(parts) < 2:
                continue
            g.add_edge(parts[0], parts[1])
    return g


def articulation_points(g):
    tin = {}
    low = {}
    cuts = set()
    timer = [0]

    def dfs(v, parent):
        tin[v] = low[v] = timer[0]
        timer[0] += 1
        children = 0
        for u in g.neighbors(v):
            if u == parent:
                continue
            if u in tin:
                low[v] = min(low[v], tin[u])
            else:
                dfs(u, v)
                low[v] = min(low[v], low[u])
                children += 1
                if parent is not None and low[u] >= tin[v]:
                    cuts.add(v)
        if parent is None and children > 1:
            cuts.add(v)

    for v in g:
        if v not in tin:
            dfs(v, None)
    return cuts


def is_biconnected(g):
    if len(g) < 3:
        return False
    return len(articulation_points(g)) == 0


def make_edge(u, v):
    return (u, v) if u < v else (v, u)


class Segment:
    def __init__(self, contacts, body):
        self.contacts = contacts
        self.body = body

    def is_chord(self):
        return len(self.body) == 0


class PlanarityChecker:
    def __init__(self, g):
        self.g = g
        self.faces = []
        self.embedded_edges = set()

    def run(self):
        start = self._initial_cycle()
        if start is None:
            return None

        self.faces = [list(start), list(start)]
        for i in range(len(start)):
            self.embedded_edges.add(make_edge(start[i - 1], start[i]))

        target = self.g.edge_count()
        while len(self.embedded_edges) < target:
            seg = self._pick_next_segment()
            if seg is None:
                return None
            face = self._pick_face(seg)
            if face is None:
                return None
            path = self._path_through(seg)
            if path is None:
                return None
            self._insert_path(path, face)

        return self.faces


    def _initial_cycle(self):
        used = {}

        def dfs(v, parent):
            used[v] = parent
            for u in sorted(self.g.neighbors(v)):
                if u == parent:
                    continue
                if u in used:
                    cycle = [v]
                    while cycle[-1] != u:
                        cycle.append(used[cycle[-1]])
                    return cycle
                res = dfs(u, v)
                if res:
                    return res
            return None

        return dfs(min(self.g.vertices()), None)

    def _placed(self):
        placed = set()
        for u, v in self.embedded_edges:
            placed.add(u)
            placed.add(v)
        return placed

    def _all_segments(self):
        placed = self._placed()
        segments = []

        for u in sorted(placed):
            for v in sorted(self.g.neighbors(u)):
                if v in placed and u < v and make_edge(u, v) not in self.embedded_edges:
                    segments.append(Segment({u, v}, set()))

        seen = set()
        for start in sorted(self.g.vertices()):
            if start in placed or start in seen:
                continue
            comp = self._component(start, placed)
            seen |= comp
            contacts = set()
            for v in comp:
                contacts |= {u for u in self.g.neighbors(v) if u in placed}
            segments.append(Segment(contacts, comp))

        return segments

    def _component(self, start, placed):
        comp = {start}
        stack = [start]
        while stack:
            v = stack.pop()
            for u in self.g.neighbors(v):
                if u not in placed and u not in comp:
                    comp.add(u)
                    stack.append(u)
        return comp

    def _pick_next_segment(self):
        segments = self._all_segments()
        if not segments:
            return None
        best = None
        best_count = math.inf
        for seg in segments:
            cnt = sum(1 for f in self.faces if seg.contacts <= set(f))
            if cnt < best_count:
                best, best_count = seg, cnt
                if cnt == 0:
                    break
        return best

    def _pick_face(self, seg):
        candidates = [f for f in self.faces if seg.contacts <= set(f)]
        if not candidates:
            return None
        return min(candidates, key=len)

    def _path_through(self, seg):
        if seg.is_chord():
            return sorted(seg.contacts)
        start = min(seg.contacts)
        prev = {start: None}
        queue = deque([start])
        while queue:
            v = queue.popleft()
            for u in sorted(self.g.neighbors(v)):
                if u in prev:
                    continue
                if u in seg.body:
                    prev[u] = v
                    queue.append(u)
                elif u in seg.contacts and v != start:
                    path = [u, v]
                    while path[-1] != start:
                        path.append(prev[path[-1]])
                    return path
        return None

    def _insert_path(self, path, face):
        a, b = path[0], path[-1]
        inner = path[1:-1]
        i, j = face.index(a), face.index(b)
        if i < j:
            left = face[i:j + 1]
            right = face[j:] + face[:i + 1]
        else:
            left = face[i:] + face[:j + 1]
            right = face[j:i + 1]

        self.faces.remove(face)
        self.faces.append(left + inner[::-1])
        self.faces.append(right + inner)

        for k in range(len(path) - 1):
            self.embedded_edges.add(make_edge(path[k], path[k + 1]))


def tutte_embed(g, outer_face, radius=4.0, max_iter=100000, eps=1e-12):
    pos = {}
    n = len(outer_face)
    for i, v in enumerate(outer_face):
        angle = math.pi / 2 + 2 * math.pi * i / n
        pos[v] = (radius * math.cos(angle), radius * math.sin(angle))

    inner = [v for v in g.vertices() if v not in pos]
    for v in inner:
        pos[v] = (0.0, 0.0)

    for _ in range(max_iter):
        shift = 0.0
        for v in inner:
            nb = g.neighbors(v)
            x = sum(pos[u][0] for u in nb) / len(nb)
            y = sum(pos[u][1] for u in nb) / len(nb)
            shift = max(shift, abs(x - pos[v][0]) + abs(y - pos[v][1]))
            pos[v] = (x, y)
        if shift < eps:
            break

    return pos


def pick_outer_face(faces):
    return max(faces, key=len)


def fmt(x):
    return "%g" % (round(x, 3) + 0.0)


def write_dot(g, pos, path):
    lines = ["graph G {", "    layout=neato;", "    node [shape=circle];"]
    for v in sorted(g.vertices()):
        x, y = pos[v]
        lines.append('    "%s" [pos="%s,%s!"];' % (v, fmt(x), fmt(y)))
    for u in sorted(g.vertices()):
        for v in sorted(g.neighbors(u)):
            if u < v:
                lines.append('    "%s" -- "%s";' % (u, v))
    lines.append("}")
    with open(path, "w", encoding="utf-8") as fh:
        fh.write("\n".join(lines))


def show(g, pos):
    fig, ax = plt.subplots(figsize=(7, 7))
    for u in g.vertices():
        for v in g.neighbors(u):
            if u < v:
                ax.plot([pos[u][0], pos[v][0]],
                        [pos[u][1], pos[v][1]],
                        color="#555555", linewidth=1.2, zorder=1)
    for v in g.vertices():
        x, y = pos[v]
        ax.scatter(x, y, s=140, c="#9ecbff", edgecolors="#1f4e79",
                   linewidths=1.5, zorder=2)
        ax.text(x + 0.12, y + 0.12, v, fontsize=10, zorder=3)
    ax.set_aspect("equal")
    ax.axis("off")
    fig.tight_layout()
    plt.show()


def main(argv):
    src = argv[1] if len(argv) > 1 else "graph.txt"
    g = load(src)

    if not is_biconnected(g):
        print("Граф не двусвязный: укладка невозможна")
        return 1

    checker = PlanarityChecker(g)
    faces = checker.run()

    if faces is None:
        print("Граф не планарен")
        return 1

    print("Граф планарен")
    print("Граней: %d" % len(faces))
    for f in faces:
        print("  " + " ".join(f))

    outer = pick_outer_face(faces)
    print("\nВнешняя грань: " + " ".join(outer))

    pos = tutte_embed(g, outer)
    print("\nКоординаты вершин:")
    for v in sorted(g.vertices()):
        x, y = pos[v]
        print("  %s: (%s, %s)" % (v, fmt(x), fmt(y)))

    out = src.rsplit(".", 1)[0] + ".dot"
    write_dot(g, pos, out)
    print("\nDOT-файл сохранён: " + out)

    show(g, pos)
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))