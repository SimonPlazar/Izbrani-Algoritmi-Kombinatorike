import argparse
import matplotlib.pyplot as plt
import networkx as nx
import time


class KeywordTreeNode:
    def __init__(self):
        self.children = {}
        self.is_end = False
        self.word = None


class KeywordTree:
    def __init__(self):
        self.root = KeywordTreeNode()

    def insert(self, word):
        node = self.root
        for char in word:
            if char not in node.children:
                node.children[char] = KeywordTreeNode()
            node = node.children[char]
        node.is_end = True
        node.word = word

    def build_tree(self, keywords):
        for word in keywords:
            self.insert(word)

    def search_all(self, text, max_k=0):
        grouped_results = {}
        for i in range(len(text)):
            self._search_from(text, i, self.root, i, max_k, grouped_results)
        return grouped_results

    def _search_from(self, text, text_pos, node, start_index, remaining_k, grouped_results):
        if node.is_end:
            grouped_results.setdefault(node.word, []).append(start_index)

        if text_pos >= len(text):
            return

        current_char = text[text_pos]

        for char, child in node.children.items():
            if char == current_char:
                self._search_from(text, text_pos + 1, child, start_index, remaining_k, grouped_results)
            elif remaining_k > 0:
                self._search_from(text, text_pos + 1, child, start_index, remaining_k - 1, grouped_results)


class SuffixTreeNode:
    def __init__(self):
        self.children = {}          # label -> SuffixTreeNode
        self.indexes = []           # začetni indeksi (listi)

class SuffixTree:
    def __init__(self, text):
        self.text = text + "$"
        # self.text = text
        self.root = SuffixTreeNode()
        self._build_suffix_tree()
        self._compress_tree(self.root)

    def _build_suffix_tree(self):
        for i in range(len(self.text)):
            node = self.root
            for char in self.text[i:]:
                if char not in node.children:
                    node.children[char] = SuffixTreeNode()
                node = node.children[char]
            node.indexes.append(i)

    def _compress_tree(self, node):
        for char in list(node.children.keys()):
            child = node.children[char]
            label = char
            while len(child.children) == 1 and not child.indexes:
                next_char, next_child = next(iter(child.children.items()))
                label += next_char
                child = next_child
            if label != char:
                del node.children[char]
                node.children[label] = child
            self._compress_tree(child)


    # Collect all matches
    def _collect_indexes(self, node):
        result = list(node.indexes)
        for child in node.children.values():
            result.extend(self._collect_indexes(child))
        return result

    def search_approx(self, pattern, max_errors):
        results = set()
        for label, child in self.root.children.items():
            self._search_approx_recursive(child, label, pattern, 0, max_errors, results)
        return sorted(results)

    def _search_approx_recursive(self, node, label, pattern, pat_idx, remaining_k, results):
        i = 0
        while i < len(label) and pat_idx < len(pattern):
            if label[i] == pattern[pat_idx]:
                i += 1
                pat_idx += 1
            elif remaining_k > 0:
                # 3 možnosti: zamenjava, preskok v labelu, preskok v vzorcu
                # 1. zamenjava (label[i] ≠ pattern[pat_idx])
                self._search_approx_recursive(node, label[i+1:], pattern, pat_idx+1, remaining_k - 1, results)
                # 2. preskok v labelu (vstavitev znaka v pattern)
                self._search_approx_recursive(node, label[i+1:], pattern, pat_idx, remaining_k - 1, results)
                # 3. preskok v vzorcu (izbris znaka v pattern)
                self._search_approx_recursive(node, label[i:], pattern, pat_idx+1, remaining_k - 1, results)
                return  # enkrat poskusi vse poti in zaključi
            else:
                return

        if pat_idx == len(pattern):
            results.update(self._collect_indexes(node))
        else:
            # naprej na otroke
            for next_label, child in node.children.items():
                self._search_approx_recursive(child, next_label, pattern, pat_idx, remaining_k, results)


def build_graph_from_tree(tree_root):
    graph = nx.DiGraph()
    node_id_counter = [0]  # mutable counter
    node_to_id = {}

    def _add_edges(node, parent_id):
        for label, child in node.children.items():
            node_id_counter[0] += 1
            node_id = node_id_counter[0]

            edge_label = label
            # Optionally show index info for suffix trees
            if hasattr(child, "indexes") and child.indexes:
                edge_label += f" ({','.join(map(str, child.indexes))})"

            graph.add_node(node_id, label=edge_label)
            graph.add_edge(parent_id, node_id)

            node_to_id[child] = node_id
            _add_edges(child, node_id)

    graph.add_node(0, label="ROOT")
    node_to_id[tree_root] = 0
    _add_edges(tree_root, 0)

    return graph


def hierarchy_pos(G, root, width=1., vert_gap=0.2, vert_loc=0, xcenter=0.5, pos=None, parent=None):
    # Vir: networkx
    if pos is None:
        pos = {root: (xcenter, vert_loc)}
    else:
        pos[root] = (xcenter, vert_loc)
    children = list(G.successors(root))
    if len(children) != 0:
        dx = width / len(children)
        nextx = xcenter - width / 2 - dx / 2
        for child in children:
            nextx += dx
            pos = hierarchy_pos(G, child, width=dx, vert_gap=vert_gap,
                                vert_loc=vert_loc - vert_gap, xcenter=nextx, pos=pos, parent=root)
    return pos


def draw_tree_graph_manual_layout(graph, root_id=0):
    pos = hierarchy_pos(graph, root=root_id)
    labels = nx.get_node_attributes(graph, 'label')
    plt.figure(figsize=(12, 6))
    nx.draw(graph, pos, labels=labels, with_labels=True, arrows=True,
            node_size=2000, node_color='lightyellow', font_size=10, font_weight='bold')
    plt.title("Drevo ključnih besed (brez pydot)")
    plt.axis('off')
    plt.show()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Primerjava nizov z uporabo eksaktnega in približnega iskanja.")
    parser.add_argument("--file", type=str, required=True, help="Pot do datoteke z DNK zapisi")
    parser.add_argument("--keywords", type=str, required=True, help="Vnos ključnih besed, ločenih z vejico")
    parser.add_argument("--k", type=int, required=True, help="Parameter k (največje dovoljeno število napak)")

    args = parser.parse_args()
    with open(args.file, 'r') as f:
        content = f.read().replace("\n", "")

    keywords = args.keywords.split(',')
    k = args.k

    keywordtree = KeywordTree()
    start_time = time.time()
    keywordtree.build_tree(keywords)
    build_time = time.time() - start_time
    print(f"[KeywordTree] Čas za gradnjo drevesa: {build_time*1000:.4f} ms")
    # keyword_graph = build_graph_from_tree(keywordtree.root)
    # draw_tree_graph_manual_layout(keyword_graph)
    start_time = time.time()
    matches = keywordtree.search_all(content, max_k=k)
    search_time = time.time() - start_time
    print("[KeywordTree] Najdeni nizi:")
    for word, positions in matches.items():
    #     print(f"'{word}' najden na indeksih: {positions}")
        print(f"'{word}' najden {len(positions)} krat")
    print(f"[KeywordTree] Čas iskanja: {search_time*1000:.4f} ms")
    print(f"[KeywordTree] Skupni čas: {(build_time + search_time)*1000:.4f} ms\n")

    print("--------------------------------------------------\n")

    start_time = time.time()
    suffixtree = SuffixTree(content)
    build_time = time.time() - start_time
    print(f"[SuffixTree] Čas za gradnjo sufiksnega drevesa: {build_time*1000:.4f} ms")
    # suffix_graph = build_graph_from_tree(suffixtree.root)
    # draw_tree_graph_manual_layout(suffix_graph)
    search_time = 0
    print("[SuffixTree] Najdeni nizi:")
    keywords.sort()
    for pattern in keywords:
        start_time = time.time()
        result = suffixtree.search_approx(pattern, max_errors=k)
        search_time += time.time() - start_time
        # print(f"'{pattern}' najden na indeksih: {result}")
        print(f"'{pattern}' najden {len(result)} krat")
    print(f"[SuffixTree] Čas iskanja: {search_time*1000:.4f} ms")
    print(f"[SuffixTree] Skupni čas: {(build_time + search_time)*1000:.4f} ms")

