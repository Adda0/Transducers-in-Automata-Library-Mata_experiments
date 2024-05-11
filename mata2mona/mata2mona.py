import sys
from mona import Mona
from nft import Parser
from bitvector import Bitvector


def main() -> None:
    if len(sys.argv) < 3:
        print("Usage: python3 mata2mona.py <input_file> <output_dir> [--dot]")
        sys.exit(1)
    if {"-h", "--help"}.intersection(sys.argv):
        print("Usage: python3 mata2mona.py <input_file> <output_dir> [--dot]")
        sys.exit(0)

    automata = Parser().parse(sys.argv[1])
    alphabet = {symbol for nft in automata for symbol in nft.get_alphabet()}

    for i, input_nft in enumerate(Parser().parse(sys.argv[1])):
        bitvector = Bitvector(alphabet, input_nft.max_num_of_nondet())
        bitvector_total_len = bitvector.nondet_prefix_len + bitvector.vector_len
        num_of_vars = bitvector_total_len * input_nft.levels_cnt
        aux_nfa = input_nft.to_vector_transitions(bitvector)
        bdd = Mona(aux_nfa)
        bdd.vars_cnt = num_of_vars
        if "--dot" in sys.argv:
            bdd.print_to_DOT(f"{sys.argv[2]}/{i}_{bitvector.nondet_prefix_len}_{bitvector_total_len}_{num_of_vars}.dot")
        bdd.save(f"{sys.argv[2]}/{i}_{bitvector.nondet_prefix_len}_{bitvector_total_len}_{num_of_vars}.mona")


if __name__ == "__main__":
    main()
