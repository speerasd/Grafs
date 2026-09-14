import os
import sys

BASE_DIR = os.path.dirname(os.path.abspath(__file__))


class TreeNode:
    _counter = 0

    def __init__(self, label=None):
        if label is None:
            TreeNode._counter += 1
            label = TreeNode._counter
        self.label = label
        self.children = []
        self.parent = None

def restore_tree(code: str) -> TreeNode:
    TreeNode._counter = 0
    root = TreeNode()
    current = root

    for i, ch in enumerate(code, 1):
        if ch == "0":
            child = TreeNode()
            child.parent = current
            current.children.append(child)
            current = child
        elif ch == "1":
            if current.parent is None:
                pointer = " " * (i - 1) + "^"
                raise ValueError(
                    f"попытка выйти вверх из корня\n"
                    f"    код: {code}\n"
                    f"          {pointer}\n"
                    f"    позиция: {i}"
                )
            current = current.parent
        else:
            pointer = " " * (i - 1) + "^"
            raise ValueError(
                f"недопустимый символ {ch!r}\n"
                f"    код: {code}\n"
                f"          {pointer}\n"
                f"    позиция: {i}"
            )

    if current is not root:
        depth = 0
        node = current
        while node.parent is not None:
            depth += 1
            node = node.parent
        raise ValueError(
            f"обход не вернулся в корень (остались на глубине {depth})\n"
            f"    код: {code}"
        )
    return root


def tree_edges(root: TreeNode):
    edges = []

    def dfs(node):
        for ch in node.children:
            edges.append((node.label, ch.label))
            dfs(ch)

    dfs(root)
    return edges

def tree_stats(root: TreeNode):
    count, leaves, depth = 0, 0, 0

    def dfs(node, d):
        nonlocal count, leaves, depth
        count += 1
        depth = max(depth, d)
        if not node.children:
            leaves += 1
        for ch in node.children:
            dfs(ch, d + 1)

    dfs(root, 0)
    return count, leaves, depth

def format_tree(root: TreeNode) -> str:
    lines = [f"[{root.label}]"]

    def walk(node, prefix=""):
        n = len(node.children)
        for i, ch in enumerate(node.children):
            last = (i == n - 1)
            branch = "└── " if last else "├── "
            lines.append(f"{prefix}{branch}[{ch.label}]")
            extension = "    " if last else "│   "
            walk(ch, prefix + extension)

    walk(root)
    return "\n".join(lines)

def tree_to_dot(root: TreeNode, name: str = "Tree") -> str:
    lines = [
        f"digraph {name} {{",
        '    graph [charset="UTF-8"];',
        '    node [shape=circle, style=filled, fillcolor=lightyellow, fontname="Helvetica"];',
        '    edge [color="#555555"];',
        '    rankdir=TB;',
    ]

    def visit(node):
        lines.append(f'    "{node.label}";')
        for ch in node.children:
            lines.append(f'    "{node.label}" -> "{ch.label}";')
            visit(ch)

    visit(root)
    lines.append("}")
    return "\n".join(lines)

def save_dot(text: str, filename: str, outdir: str = None) -> str:
    outdir = outdir or BASE_DIR
    os.makedirs(outdir, exist_ok=True)
    path = os.path.abspath(os.path.join(outdir, filename))
    with open(path, "w", encoding="utf-8") as f:
        f.write(text)
    return path

def print_header(title: str):
    width = 60
    print("═" * width)
    print(title.center(width))
    print("═" * width)


def print_section(title: str):
    print()
    print("─" * 60)
    print(f"  {title}")
    print("─" * 60)

def main():

    code = input("Введите двоичный код: ").strip()
    if not code:
        print("\n⚠  Пустой ввод.")
        return
    try:
        root = restore_tree(code)
    except ValueError as e:
        print("Ошибка в коде:")
        print(f"    {e}")
        return

    print_section("ДЕРЕВО")
    print(format_tree(root))

    edges = tree_edges(root)
    print_section("РЁБРА")
    for i, (u, v) in enumerate(edges, 1):
        print(f"    {i:>2}. {u} → {v}")

    count, leaves, depth = tree_stats(root)
    print_section("СТАТИСТИКА")
    print(f"    Вершин:  {count}")
    print(f"    Листьев: {leaves}")
    print(f"    Глубина: {depth}")

    dot_tree = tree_to_dot(root, name="RestoredTree")
    save_dot(dot_tree, "tree.dot")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nПрервано пользователем.")
        sys.exit(1)