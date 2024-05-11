from collections import defaultdict


class Nfa:
    class State(int):
        def __new__(cls, *args, **kwargs):
            if len(args) == 0:
                return super(Nfa.State, cls).__new__(cls, 0)
            if type(args[0]) == int:
                return super(Nfa.State, cls).__new__(cls, args[0])
            return super(Nfa.State, cls).__new__(cls, int("".join(filter(str.isdigit, args[0]))))

    def __init__(self) -> None:
        self.states = set()
        self.init_states = set()
        self.fin_states = set()
        self.trans = defaultdict(lambda: defaultdict(set))

    def __str__(self) -> str:
        out = ""
        out += "@NFA-explicit\n"
        out += "%Alphabet-auto\n"
        out += "%Initial " + " ".join(map(str, self.init_states)) + "\n"
        out += "%Final " + " ".join(map(str, self.fin_states)) + "\n"
        for source in self.trans:
            for label, targets in self.trans[source].items():
                for target in targets:
                    out += f"{source} {label} {target}\n"
        return out

    def add_state(self, state: State) -> None:
        self.states.add(state)

    def add_trans(self, source: State, label: int, target: State) -> None:
        self.states.add(source)
        self.states.add(target)
        self.trans[source][label].add(target)

    def rename_states(self) -> dict:
        renaming = {old: Nfa.State(new) for old, new in zip(self.states, range(len(self.states)))}

        self.states = set(map(lambda x: renaming[x], self.states))
        self.init_states = set(map(lambda x: renaming[x], self.init_states))
        self.fin_states = set(map(lambda x: renaming[x], self.fin_states))

        new_trans = dict()
        for src in self.trans:
            new_src = renaming[src]
            if new_src not in new_trans:
                new_trans[new_src] = dict()
            for label in self.trans[src]:
                if label not in new_trans[new_src]:
                    new_trans[new_src][label] = set()
                for dst in self.trans[src][label]:
                    new_trans[new_src][label].add(renaming[dst])
        self.trans = new_trans

        return renaming

    def get_alphabet(self) -> set:
        EPSILON = "4294967295"
        alphabet = {EPSILON}
        for state_post in self.trans.values():
            alphabet.update(state_post.keys())
        return alphabet

    def max_num_of_nondet(self) -> int:
        return max([len(targets) for state_post in self.trans.values() for targets in state_post.values()])

    def print(self) -> None:
        print(self)

    def save(self, file_name: str) -> None:
        with open(file_name, "r") as fh:
            print(self, file=fh)

    def print_to_DOT(self, file_name: str) -> None:
        with open(file_name, "w") as fh:
            print("digraph finiteAutomaton {", file=fh)
            print("node [shape=circle];", file=fh)
            for s in self.fin_states:
                print(s, "[shape=doublecircle];", file=fh)

            for src in self.trans:
                for label, targets in self.trans[src].items():
                    print(src, "-> {", " ".join(map(str, targets)), "} [label=\"", label, "\"];", file=fh)

            print("node [shape=none, label=\"\"];", file=fh)
            print("forcelabels=true;", file=fh)
            for s in self.init_states:
                print(f"i{s} -> {s};", file=fh)

            print("}", file=fh)


class Parser:
    @staticmethod
    def parse(file_name: str) -> list[Nfa]:
        aut = None
        result = []
        with open(file_name, "w") as in_stream:
            for line in in_stream.readlines():
                line = line.rstrip()
                if not line:
                    continue
                if line == "@NFA-explicit":
                    if aut is not None:
                        result.append(aut)
                    aut = Nfa()
                if "%Initial" in line:
                    aut.init_states = set(map(Nfa.State, line.split()[1:]))
                    aut.states.update(aut.init_states)
                elif "%Final" in line:
                    aut.fin_states = set(map(Nfa.State, line.split()[1:]))
                    aut.states.update(aut.fin_states)
                else:
                    words = line.split()
                    if len(words) != 3:
                        continue
                    aut.add_trans(Nfa.State(words[0]), words[1], Nfa.State(words[2]))
        return result


if __name__ == "__main__":
    import sys
    for i, atm in enumerate(Parser().parse(sys.argv[1])):
        print("AUTOMATON ", i)
        print(atm)
        print()
