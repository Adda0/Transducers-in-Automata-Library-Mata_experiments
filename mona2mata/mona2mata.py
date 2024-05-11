import sys
from collections import defaultdict
from queue import Queue


EPSILON = "4294967295"
DCARE = "4294967294"


class Mona:
    def __init__(self) -> None:
        self.states = set()
        self.trans = defaultdict(lambda: defaultdict(set))
        self.initial = set()
        self.final = set()

    def add_transition(self, src, label, dst):
        self.states.add(src)
        self.states.add(dst)
        self.trans[src][label].add(dst)

    def add_state(self, state):
        new_state = list(set(range(len(state) + 1)).difference(state))[0]
        self.states.add(new_state)
        return new_state

    def add_initial(self, state):
        self.states.add(state)
        self.initial.add(state)

    def add_final(self, state):
        self.states.add(state)
        self.final.add(state)

    def remove_states(self, states_to_remove: set):
        self.states = self.states.difference(states_to_remove)
        self.initial = self.initial.difference(states_to_remove)
        self.final = self.final.difference(states_to_remove)

        new_trans = defaultdict(lambda: defaultdict(set))
        for src, state_post in self.trans.items():
            if src in states_to_remove:
                continue
            for label, targets in state_post.items():
                new_targets = targets.difference(states_to_remove)
                if not new_targets:
                    continue
                new_trans[src][label] = new_targets
        self.trans = new_trans

    def trim(self):
        def dfs(state, trans: dict, visited: set):
            visited.add(state)
            for _, targets in trans[state].items():
                for target in targets:
                    if target not in visited:
                        dfs(target, trans,  visited)

        accessible = set()
        for init_state in self.initial:
            dfs(init_state, self.trans, accessible)

        rev_trans = defaultdict(lambda: defaultdict(set))
        for src, state_post in self.trans.items():
            for label, targets in state_post.items():
                for target in targets:
                    rev_trans[target][label].add(src)
        finishable = set()
        for final_state in self.final:
            dfs(final_state, rev_trans, finishable)

        self.remove_states(self.states.difference(accessible.intersection(finishable)))

    def get_alphabet(self):
        alphabet = set()
        for state_post in self.trans.values():
            alphabet = alphabet.union(state_post.keys())
        return alphabet

    def expand_transitions(self):
        def expand_label(label: str) -> set:
            if set(label) == {"X"}:
                return {label}
            if "X" in label:
                idx = label.index("X")
                return expand_label(label[:idx] + "0" + label[idx + 1:]).union(expand_label(label[:idx] + "1" + label[idx + 1:]))
            return {label}

        new_trans = defaultdict(lambda: defaultdict(set))
        for src, state_post in self.trans.items():
            for label, targets in state_post.items():
                for expanded_label in expand_label(label):
                    new_trans[src][expanded_label].update(targets)
        self.trans = new_trans

    def load_from_file(self, file_name: str, vector_len: int, trim=False):
        assert vector_len % 2 == 0

        with open(file_name, "r") as fh:
            for line in fh:
                if line.startswith("Initial"):
                    for state in line.split()[2:]:
                        self.add_initial(state)
                elif line.startswith("Accepting"):
                    for state in line.split()[2:]:
                        self.add_final(state)
                elif line.startswith("State"):
                    src = line.split()[1][:-1]
                    dst = line.split()[-1]
                    label = "X" * vector_len
                    for at in line.split()[2:-3]:
                        at_idx = int(at[1:].split("=")[0])
                        at_val = at.split("=")[-1].rstrip(",")
                        label = label[:at_idx] + at_val + label[at_idx + 1:]
                    label_first_half = label[:int(vector_len/2)]
                    label_second_half = label[int(vector_len/2):]
                    self.add_transition(src, label_first_half, (src, label_first_half))
                    self.add_transition((src, label_first_half), label_second_half, dst)

        self.rename_states()
        self.rename_alphabet()
        if trim:
            self.trim()

    def get_all_distances_from_init(self):
        distance = dict()
        queue = Queue()
        for init_state in self.initial:
            queue.put(init_state)
            distance[init_state] = 0

        while not queue.empty():
            src = queue.get()
            if src not in self.trans:
                continue
            for _, targets in self.trans[src].items():
                for target in targets:
                    if target not in distance:
                        distance[target] = distance[src] + 1
                        queue.put(target)

        return distance

    def rename_states(self):
        rename = {old: f"s{i}" for i, old in enumerate(self.states)}

        self.initial = {rename[state] for state in self.initial}
        self.final = {rename[state] for state in self.final}
        self.states = {rename[state] for state in self.states}

        new_trans = defaultdict(lambda: defaultdict(set))
        for src, state_post in self.trans.items():
            for label, targets in state_post.items():
                new_trans[rename[src]][label] = {rename[target] for target in targets}
        self.trans = new_trans

    def rename_alphabet(self):
        self.expand_transitions()
        rename = dict()
        for old in sorted(self.get_alphabet()):
            if set(old) == {"X"}:
                rename[old] = DCARE
            elif set(old) == {"0"}:
                rename[old] = EPSILON
            else:
                i = int(old, 2)
                rename[old] = f"a{i}"

        new_trans = defaultdict(lambda: defaultdict(set))
        for src, state_post in self.trans.items():
            for label, targets in state_post.items():
                new_trans[src][rename[label]] = targets

        self.trans = new_trans

    def print_DOT(self, fh=sys.stdout):
        output = "digraph finiteAutomaton {\n"
        output += "node [shape=circle];\n"

        distance = self.get_all_distances_from_init()
        for state in self.states:
            output += f"{state} [label=\"{state}:{distance[state]%2}\"];\n"

        for final_state in self.final:
            output += f"{final_state} [shape=doublecircle];\n"

        for src, state_post in self.trans.items():
            for label, targets in state_post.items():
                for target in targets:
                    if label == EPSILON:
                        label_txt = "ε"
                    elif label == DCARE:
                        label_txt = "?"
                    else:
                        label_txt = label
                    output += f"{src} -> {target} [label=\"{label_txt}\"];\n"

        output += "node [shape=none, label=\"\"];\n"
        output += "forcelabels=true;\n"
        for init_state in self.initial:
            output += f"i{init_state} -> {init_state};\n"

        output += "}\n"

        fh.write(output)

    def print_Mata(self, fh=sys.stdout):
        output = "@NFA-explicit\n"
        output += "%Alphabet-auto\n"
        output += f"%Initial {' '.join(self.initial)}\n"
        output += f"%Final {' '.join(self.final)}\n"

        distance = self.get_all_distances_from_init()
        output += f"%LevelsCnt 2\n"
        output += "%Levels " + " ".join(f"{state}:{distance[state]%2}" for state in self.states) + "\n"

        for source, symbol_post in self.trans.items():
            for symbol, targets in symbol_post.items():
                for target in targets:
                    output += f"{source} {symbol} {target}\n"

        fh.write(output)


def main():
    if len(sys.argv) < 3:
        print("Usage: python3 mona2mata.py <input_file> <vector_len> [--dot] [--trim]")
        sys.exit(1)
    if {"-h", "--help"}.intersection(sys.argv):
        print("Usage: python3 mona2mata.py <input_file> <vector_len> [--dot] [--trim]")
        sys.exit(0)

    trim = "--trim" in sys.argv
    mona = Mona()
    mona.load_from_file(sys.argv[1], int(sys.argv[2]), trim)
    if "--dot" in sys.argv:
        mona.print_DOT()
    else:
        mona.print_Mata()


if __name__ == "__main__":
    main()
