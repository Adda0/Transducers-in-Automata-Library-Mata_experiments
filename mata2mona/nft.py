from collections import defaultdict
from nfa import Nfa
from bitvector import Bitvector


class Nft(Nfa):
    def __init__(self) -> None:
        super().__init__()
        self.levels = defaultdict(int)
        self.levels_cnt = 0

    def __str__(self) -> str:
        out = ""
        out += "@NFA-explicit\n"
        out += "%Alphabet-auto\n"
        out += "%Initial " + " ".join(map(str, self.init_states)) + "\n"
        out += "%Final " + " ".join(map(str, self.fin_states)) + "\n"
        out += "%LevelsCnt " + self.levels_cnt + "\n"
        out += "%Levels " + " ".join(map, lambda x, y: f"{x}:{y}", self.levels.items())
        for source in self.trans:
            for label, targets in self.trans[source].items():
                for target in targets:
                    out += f"{source} {label} {target}\n"
        return out

    def add_state_with_level(self, state:int, level:int) -> None:
        self.states.add(state)
        self.levels[state] = level

    def rename_states(self) -> dict:
        renaming = super().rename_states()
        self.levels = {renaming[s]: l for s, l in self.levels.values()}
        return renaming

    def to_vector_transitions(self, bitvector: Bitvector) -> Nfa:
        result = Nfa()
        result.init_states = self.init_states
        result.fin_states = self.fin_states

        def dfs_visit(source: Nft.State, state: Nft.State, label: str) -> None:
            if self.levels[state] == 0:
                result.add_trans(root, label, state)
                return
            for symbol, symbol_post in self.trans[state].items():
                for nondet_cnt, target in enumerate(symbol_post):
                    dfs_visit(source, target, label + bitvector.translate(symbol, nondet_cnt))

        for root in self.states:
            if self.levels[root] != 0:
                continue
            for symbol, symbol_post in self.trans[root].items():
                for nondet_cnt, target in enumerate(symbol_post):
                    dfs_visit(root, target, bitvector.translate(symbol, nondet_cnt))

        result.rename_states()
        return result

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
            for s, l in self.levels.items():
                print(s, f"[label=\"{s}:{l}\"];", file=fh)
            for s in self.init_states:
                print(f"i{s} -> {s};", file=fh)

            print("}", file=fh)


class Parser:
    @staticmethod
    def parse(file_name: str) -> list[Nft]:
        aut = None
        result = []
        with open(file_name, "r") as in_stream:
            for line in in_stream.readlines():
                line = line.rstrip()
                if not line:
                    continue
                if line == "@NFT-explicit":
                    if aut is not None:
                        result.append(aut)
                    aut = Nft()
                if "%Initial" in line:
                    aut.init_states = set(map(Nft.State, line.split()[1:]))
                    aut.states.update(aut.init_states)
                elif "%Final" in line:
                    aut.fin_states = set(map(Nft.State, line.split()[1:]))
                    aut.states.update(aut.fin_states)
                elif "%LevelsCnt" in line:
                    aut.levels_cnt = int(line.split()[1])
                elif "%Levels" in line:
                    for state_with_level in line.split()[1:]:
                        aut.add_state_with_level(Nft.State(state_with_level.split(":")[0]),
                                                int(state_with_level.split(":")[1]))
                else:
                    words = line.split()
                    if len(words) != 3:
                        continue
                    aut.add_trans(Nft.State(words[0]), words[1], Nft.State(words[2]))
        if aut is not None:
            result.append(aut)
        return result


if __name__ == "__main__":
    import sys
    for i, atm in enumerate(Parser().parse(sys.argv[1])):
        print("AUTOMATON ", i)
        print(atm)
        print()
