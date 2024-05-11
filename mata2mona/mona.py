""" Do not attempt to understand, optimize, or fix this code. It's a mess.
    When I wrote this code, only God and I knew how it worked. Now, only God knows.
    You have been warned.
"""

from collections import defaultdict
from nfa import Nfa


class Mona:
    def __init__(self, nfa: Nfa=None) -> None:
        self.nfa = nfa
        self.vars_cnt = 0
        self.states = set()
        self.state_type = list()
        self.initial = None
        self.sink = None
        self.bdd_nodes_cnt = 0
        self.bdd_nodes = list()
        self.index_by_node = dict()
        self.leaf_by_root = dict()
        self.roots = dict()
        self.levels = dict()
        self.bdd_trans = defaultdict(lambda: defaultdict(int))
        if nfa is not None:
            self.create_bdd_nodes(nfa)
            self.set_sink()
            self.create_bdd_transition(nfa)

    def __str__(self) -> str:
        out = "MONA DFA\n"
        out += f"number of variables: {self.vars_cnt}\n"
        if self.vars_cnt > 0:
            out += f"variables: {' '.join([f'v{i}' for i in range(self.vars_cnt)])}\n"
            out += f"orders: {' '.join(['1'] * self.vars_cnt)}\n"
        else:
            out += "variables: 0\n"
            out += "orders:\n"
        out += f"states: {len(self.states)}\n"
        out += f"initial: {self.index_by_node[self.initial]}\n"
        out += f"bdd nodes: {len(self.bdd_nodes)}\n"
        out += f"final: {' '.join(map(str, self.state_type))}\n"
        out += f"behaviour: {' '.join(map(lambda x: str(self.roots[x]), sorted(self.states, key=lambda y: self.index_by_node[y])))}\n"

        out += "bdd:\n"
        for i, node in enumerate(self.bdd_nodes):
            if node in self.leaf_by_root and (i >= len(self.states) or self.roots[node] == self.roots["sink"]):
                out += f"-1 {self.index_by_node[node]} 0\n"
            else:
                low = self.bdd_trans[node][0] if 0 in self.bdd_trans[node] else self.sink
                high = self.bdd_trans[node][1] if 1 in self.bdd_trans[node] else self.sink
                low_index = self.index_by_node[low] if low not in self.roots or self.index_by_node[low] != self.roots[low] else self.leaf_by_root[low]
                high_index = self.index_by_node[high] if high not in self.roots or self.index_by_node[high] != self.roots[high] else self.leaf_by_root[high]
                out += f"{self.levels[node]} {low_index} {high_index}\n"
        out += "end\n"

        return out

    def set_node(self, node: str) -> None:
        if node not in self.index_by_node:
            new_index = len(self.bdd_nodes)
            self.index_by_node[node] = new_index
            self.bdd_nodes.append(node)

    def set_leaf(self, root) -> None:
        if root not in self.leaf_by_root:
            new_index = len(self.bdd_nodes)
            self.leaf_by_root[root] = new_index
            self.bdd_nodes.append(root)

    def set_root(self, root) -> None:
        if root not in self.roots:
            new_index = len(self.bdd_nodes)
            self.index_by_node[root] = new_index
            self.roots[root] = new_index
            self.bdd_nodes.append(root)


    def set_sink(self) -> int:
        self.sink = "sink"
        self.levels[self.sink] = 0
        self.states.add(self.sink)
        self.state_type.append(-1)
        new_index = len(self.bdd_nodes)
        self.roots[self.sink] = new_index
        self.leaf_by_root[self.sink] = new_index
        self.index_by_node[self.sink] = new_index
        self.bdd_nodes.append(self.sink)

    def create_bdd_nodes(self, nfa: Nfa) -> None:
        self.levels.update({s: 0 for s in nfa.states})
        self.states.update(nfa.states)
        self.state_type.extend([0] * len(nfa.states))
        for s in nfa.states:
            self.set_root(s)
        assert nfa.init_states.issubset(self.states)
        assert nfa.fin_states.issubset(self.states)
        assert len(nfa.init_states) == 1

        self.initial = list(nfa.init_states)[0]
        for s in nfa.fin_states:
            self.state_type[s] = 1

    def create_bdd_transition(self, nfa: Nfa) -> None:
        for src in nfa.states.difference(nfa.trans.keys()):
            self.roots[src] = self.leaf_by_root[self.sink]
            self.leaf_by_root[src] = self.index_by_node[src]

        for src in nfa.trans:
            assert(src in self.levels)
            for label in nfa.trans[src]:
                for trg in nfa.trans[src][label]:
                    self.set_leaf(trg)
                    assert(trg in self.levels)
                    source_state = src
                    inner_state = f"{src}:"
                    level = 1
                    for symbol in label[:-1]:
                        inner_state += symbol
                        self.set_node(inner_state)
                        self.levels[inner_state] = level
                        self.bdd_trans[source_state][int(symbol)] = inner_state
                        source_state = inner_state
                        level += 1
                    self.bdd_trans[inner_state][int(label[-1])] = trg

    def shift_levels(self, shift: int) -> None:
        self.vars_cnt += shift
        for node in self.levels:
            self.levels[node] += shift

    def print(self) -> None:
        print(self)

    def save(self, file_name: str) -> None:
        with open(file_name, "w") as fh:
            print(self, file=fh)

    def print_to_DOT(self, file_name: str) -> None:
        def translate_target(target):
            if target in self.leaf_by_root:
                return self.leaf_by_root[target]
            return self.index_by_node[target]

        template_nodes = "\n".join(f"template_node_{i} -> template_node_{i+1};" for i in range(0, self.vars_cnt-1))
        roots_initial = "\n".join(f"iroot_{s} -> root_{s};" for s in self.nfa.states if s in self.nfa.init_states)
        roots_final = "\n".join(f"root_{s} [label=\"{s}\"];" for s in self.nfa.states if s in self.nfa.fin_states)
        roots = "\n".join(f"root_{s} [label=\"{s}\"];" for s in self.nfa.states if s not in self.nfa.fin_states)
        leaves = "\n".join(f"{self.leaf_by_root[leaf]} [label=\"{leaf}\"];" for leaf in self.leaf_by_root if leaf != "sink")
        inner_nodes = "\n".join(f"{self.index_by_node[node]} [label=\"{str(node)[2:]}\"];" for node in self.index_by_node if node not in self.leaf_by_root and node != "sink")

        edges_from_roots = "\n".join(f"root_{root_state} -> {root_node}" for root_state, root_node in self.roots.items() if root_node != self.leaf_by_root["sink"])
        edges_0 = "\n".join(f"{self.index_by_node[src]} -> {translate_target(self.bdd_trans[src][0])};" for src in self.bdd_trans if 0 in self.bdd_trans[src])
        edges_1 = "\n".join(f"{self.index_by_node[src]} -> {translate_target(self.bdd_trans[src][1])};" for src in self.bdd_trans if 1 in self.bdd_trans[src])

        ranking_init = f"rank=min; template_init; {'; '.join(f'iroot_{s}' for s in self.nfa.init_states)}"
        ranking_roots = f"rank=same; template_root; {';'.join(f'root_{s}' for s in self.nfa.states)}"
        ranking_inner_nodes = "\n".join(f"{{ rank=same; template_node_{self.levels[node]}; {self.index_by_node[node]} }}" for node in self.index_by_node if node not in self.leaf_by_root and node not in self.roots)
        ranking_leaves = f"rank=max;template_leaf; {';'.join(f'{self.leaf_by_root[leaf]}' for leaf in self.leaf_by_root if leaf != 'sink')}"

        with open(file_name, "w") as fh:
            fh.write(f"""
            digraph BDD {{
                rankdir=TB;

                // Template
                node [shape=none, label=""];
                edge [style=invis];
                template_init -> template_root;
                template_root -> template_node_0;
                {template_nodes}
                template_node_{self.vars_cnt-1} -> template_leaf;

                // Roots
                node [shape=octagon];
                {roots}

                // Roots + Initial
                edge [style=solid];
                node [shape=none, label=""];
                {roots_initial}

                // Root + Final
                node [shape=doubleoctagon];
                {roots_final}

                // Leaves
                node [shape=rectangle];
                {leaves}

                // Inner Nodes
                node [shape=ellipse];
                {inner_nodes}

                 // Edges from Roots
                edge [style=dotted];
                {edges_from_roots}

                // Edges over 0 within BDD
                edge [style=dashed];
                {edges_0}

                // Edges over 1 within BDD
                edge [style=solid];
                {edges_1}

                // Setting the Ranking
                {{ {ranking_init} }}
                {{ {ranking_roots} }}
                {ranking_inner_nodes}
                {{ {ranking_leaves} }}

            }}
            """)


if __name__ == "__main__":
    import sys
    from nft import Parser
    from bitvector import Bitvector

    input_nft = Parser().parse(sys.argv[1])[0]
    bitvector = Bitvector(input_nft.get_alphabet(), input_nft.max_num_of_nondet())
    print(bitvector.mapping["a"])
    aux_nfa = input_nft.to_vector_transitions(bitvector)

    bdd = Mona(aux_nfa)
    print(bitvector.nondet_prefix_len, bitvector.vector_len, input_nft.levels_cnt)
    bdd.vars_cnt = (bitvector.nondet_prefix_len + bitvector.vector_len) * (input_nft.levels_cnt)
    print(bdd)
    bdd.print_to_DOT("bdd.dot")
