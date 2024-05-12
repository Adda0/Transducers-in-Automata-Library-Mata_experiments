#include <cassert>
#include <chrono>
#include <functional>
#include <iomanip>
#include <iostream>
#include <vector>
#include <set>
#include <sstream>
#include <unistd.h>


extern "C" {
#include "BDD/bdd.h"
#include "DFA/dfa.h"
#include "Mem/mem.h"
}


class Timer {
    std::chrono::time_point<std::chrono::high_resolution_clock> start_time;
    bool running{ false };
public:
    long duration_mus{ 0 };

    void start() {
        start_time = std::chrono::high_resolution_clock::now();
        running = true;
    }

    void stop() {
        if (!running) {
            return;
        }
        auto end_time = std::chrono::high_resolution_clock::now();
        duration_mus += (end_time - start_time).count() / 1000;
        running = false;
    }

    void reset() {
        duration_mus = 0;
        running = false;
    }

    // void log_duration() {
    //     std::cerr << "Time: " << duration_mus << " \xC2\xB5s" << std::endl;
    // }

    void log_duration() {
        std::cout << "," << duration_mus;
    }

};


void get_file_info(std::string filename, unsigned &id, unsigned &nondet, unsigned &symbol_len, unsigned &num_of_bits) {
    // filename format ../nfa2mona/0_2_3_6.mona
    // file informations: {id}_{nondet}_{symbol_len}_{num_of_bits}.mona

    // Extracting the file name from the path
    std::string file_name = filename.substr(filename.find_last_of("/") + 1);

    // Removing the file extension
    std::string file_name_without_extension = file_name.substr(0, file_name.find_last_of("."));

    // Splitting the file name using '_' as delimiter
    std::vector<std::string> file_info;
    std::stringstream ss(file_name_without_extension);
    std::string token;
    while (std::getline(ss, token, '_')) {
        file_info.push_back(token);
    }

    // Parsing the file information
    id = std::stoi(file_info[0]);
    nondet = std::stoi(file_info[1]);
    symbol_len = std::stoi(file_info[2]);
    num_of_bits = std::stoi(file_info[3]);
}

std::vector<DFA*> copy_dfa_vector(const std::vector<DFA*> &dfas) {
    std::vector<DFA*> res;
    for (const auto &dfa : dfas) {
        res.push_back(dfaCopy(dfa));
    }
    return res;
}

void rename_indices(DFA *dfa, std::vector<unsigned> &renaming) {
    std::set<bdd_record*> visited;

    std::function<void(bdd_ptr)> dfs = [&](bdd_ptr p) {

        unsigned l, r, index;

        bdd_record *node = &dfa->bddm->node_table[p];

        LOAD_lri(node, l, r, index);

        if (index == BDD_LEAF_INDEX || visited.find(node) != visited.end()) {
            return;
        }

        visited.insert(node);
        dfs(l);
        dfs(r);
        STR_lri(node, l, r, renaming[index]);
    };

    for (unsigned i = 0; i < dfa->ns; i++) {
        dfs(dfa->q[i]);
    }
}

// Asserts that indices of BDD nodes are in increasing order.
void assert_indices(DFA* dfa) {
    std::function<void(bdd_ptr)> dfs = [&](bdd_ptr p) {
        unsigned l, r, index;

        bdd_record *node = &dfa->bddm->node_table[p];

        LOAD_lri(node, l, r, index);

        if (index == BDD_LEAF_INDEX) {
            return;
        }

        bdd_record *l_node = &dfa->bddm->node_table[l];
        bdd_record *r_node = &dfa->bddm->node_table[r];
        unsigned ll, lr, l_index, rl, rr, r_index;
        LOAD_lri(l_node, ll, rl, l_index);
        LOAD_lri(r_node, rl, rr, r_index);

        assert(l_index == BDD_LEAF_INDEX || l_index > index);
        assert(r_index == BDD_LEAF_INDEX || r_index > index);

        dfs(l);
        dfs(r);
    };

    bdd_manager *bddm_p = dfa->bddm;

    for (unsigned i = 0; i < dfa->ns; i++) {
        dfs(dfa->q[i]);
    }
}

// Projects-out first nondet bits from every symbol and determinizes the DFA
DFA *determinize(DFA *dfa, const unsigned symbol_len, const unsigned num_of_symbols, const unsigned nondet) {
    std::vector<unsigned> renaming(symbol_len * num_of_symbols, 0);
    unsigned new_index = 0;
    DFA *result = dfa;
    for (unsigned i = 0; i < num_of_symbols; i++) {
        for (unsigned j = 0; j < nondet; j++) {
            result = dfaProject(result, i * symbol_len + j);
        }
        for (unsigned j = nondet; j < symbol_len; j++) {
            renaming[i * symbol_len + j] = new_index++;
        }
    }
    rename_indices(result, renaming);

    // assert_indices(result);
    return result;
}

// Composes two DFAs.
// NOTE: The function changes lhs and rhs.
DFA *compose(DFA *lhs, DFA *rhs, const unsigned sync_symbol, const unsigned symbol_len) {
    // Adding epsilon transitions
    // lhs = add_epsilon(lhs, 2, symbol_len);
    // rhs = add_epsilon(rhs, 2, symbol_len);

    // Synchronize lhs and rhs to have the sync_symbol on the same index
    // const unsigned prefix_len = symbol_len;
    // unsigned num_of_indices = 2 * symbol_len;
    // bdd_manager *bddm_p = rhs->bddm;
    // std::vector<unsigned> renaming_prefix(num_of_indices, 0);
    // for (unsigned i = 0; i < num_of_indices; i++) {
    //     renaming_prefix[i] = i + prefix_len;
    // }
    // rename_indices(rhs, renaming_prefix);

    // Compute product of lhs and rhs
    DFA *result = dfaProduct(lhs, rhs, dfaAND);

    // // Project-out every bit of synchronization symbol
    // for (unsigned i = 0; i < symbol_len; i++) {
    //     result = dfaProject(result, sync_symbol * symbol_len + i);
    // }

    // // Decrease indices greater than projected indices
    // const unsigned start_index = sync_symbol * symbol_len;
    // const unsigned end_index = (sync_symbol + 1) * symbol_len - 1;
    // unsigned num_of_indices = 3 * symbol_len;
    // bdd_manager* bddm_p = result->bddm;
    // std::vector<unsigned> renaming_project(num_of_indices, 0);
    // for (unsigned i = 0, new_i = 0; i < num_of_indices; i++, new_i += (i < start_index || i > end_index) ? 1 : 0) {
    //     renaming_project[i] = new_i;
    // }
    // rename_indices(result, renaming_project);

    // assert_indices(result);
    return result;
}



DFA *long_pipe_benchmark(const std::vector<DFA*> &dfas, const unsigned symbol_len) {
    // std::cout << "running long_pipe\n";
    // std::cout << dfas.size() << "\n";
    // NFT1 | NFT2 | ... | NFTn
    assert(dfas.size() >= 2);
    DFA *res = compose(dfas[0], dfas[1], 1, symbol_len);
    // std::cout << "First compose done" << "\n";
    for (unsigned i = 2; i < dfas.size(); i++) {
        res = compose(res, dfas[i], 1, symbol_len);
    }
    return res;
}

DFA *double_pipe_benchmark(const std::vector<DFA*> &dfas, const unsigned symbol_len) {
    // (NFT1a | NFT1b) | (NFT2a | NFT2b) | ... | (NFTna | NFTnb)
    assert(dfas.size() >= 2);
    DFA *res = compose(dfas[0], dfas[1], 1, symbol_len);
    bool is_odd = dfas.size() % 2 == 1;
    unsigned even_size = is_odd ? dfas.size() - 1 : dfas.size();

    for (unsigned i = 2; i < even_size; i += 2) {
        assert(i < even_size);
        assert(i < dfas.size());
        assert(i + 1 < dfas.size());
        res = compose(res, compose(dfas[i], dfas[i + 1], 1, symbol_len), 1, symbol_len);
    }
    if (is_odd) {
        res = compose(res, dfas[even_size], 1, symbol_len);
    }

    return res;
}

DFA *tree_pipe_benchmark(std::vector<DFA*> &dfas, const unsigned symbol_len) {
    // ((NFT1a | NFT1b) | (NFT2a | NFT2b)) | ... |  ((NFTn-1a | NFTn-1b) |  (NFTna | NFTnb))
    assert(dfas.size() >= 2);
    bool is_odd = dfas.size() % 2 == 1;
    unsigned even_size = is_odd ? dfas.size() - 1 : dfas.size();
    while (even_size > 1) {
        for (unsigned i = 0; i < even_size; i += 2) {
            dfas[i / 2] = compose(dfas[i], dfas[i + 1], 1, symbol_len);
        }
        even_size /= 2;
    }

    DFA *res = dfas[0];
    if (is_odd) {
        res = compose(res, dfas[dfas.size() - 1], 1, symbol_len);
    }

    return res;
}

long project_out_benchmark(DFA* dfa, const unsigned symbol_to_project) {
    Timer timer;
    timer.start();
    dfa = dfaProject(dfa, symbol_to_project);
    timer.stop();
    return timer.duration_mus;
}

// Tests equivalence of two DFAs by comparing their canonical BDDs using DFS.
bool are_equal(DFA* lhs, DFA* rhs) {
    lhs = dfaMinimize(lhs);
    rhs = dfaMinimize(rhs);


    if ((lhs->ns == 0 && rhs->ns != 0) || (lhs->ns != 0 && rhs->ns == 0)) {
        return false;
    }
    if (lhs->ns == 0 && rhs->ns == 0) {
        return true;
    }

    std::set<std::pair<unsigned, unsigned>> visited;

    std::function<bool(const unsigned, const unsigned)> visit = [&](const unsigned lhs_node, const unsigned rhs_node) {
        bdd_record *lhs_node_ptr = &lhs->bddm->node_table[lhs_node];
        bdd_record *rhs_node_ptr = &rhs->bddm->node_table[rhs_node];
        unsigned lhs_l, lhs_r, lhs_index;
        unsigned rhs_l, rhs_r, rhs_index;
        LOAD_lri(lhs_node_ptr, lhs_l, lhs_r, lhs_index);
        LOAD_lri(rhs_node_ptr, rhs_l, rhs_r, rhs_index);

        if (lhs_index == BDD_LEAF_INDEX && rhs_index == BDD_LEAF_INDEX) {

            if ((lhs->f[lhs_l] == 1 && rhs->f[rhs_l] != 1) || (lhs->f[lhs_l] != 1 && rhs->f[rhs_l] == 1)) {
                return false;
            }

            if (visited.find({lhs_node, rhs_node}) == visited.end()) {
                return true;
            }

            visited.insert({lhs_l, rhs_l});
            return visit(lhs_l, rhs_l);
        }
        if (lhs_index == rhs_index) {
            assert(visited.find({lhs_l, rhs_l}) == visited.end() && visited.find({lhs_r, rhs_r}) == visited.end());
            return visit(lhs_l, rhs_l) && visit(lhs_r, rhs_r);
        }

        return false;
    };

    if ((lhs->f[lhs->s] == 1 && rhs->f[rhs->s] != 1) || (lhs->f[lhs->s] != 1 && rhs->f[rhs->s] == 1)) {
        return false;
    }

    visited.insert({lhs->q[lhs->s], rhs->q[rhs->s]});
    return visit(lhs->q[lhs->s], rhs->q[rhs->s]);
}

int main(int argc, char *argv[]) {
    if (argc < 2) {
        std::cerr << "Usage: " << argv[0] << " <NFT0> <NFT1> ... <NFTn>" << std::endl;
        return 1;
    }

    std::vector<DFA*> dfas_orig(argc - 1);
    unsigned symbol_len, num_of_bits, num_of_symbols;

    // Loading and determinizing NFTs
    try {
        for (int i = 1; i < argc; i++) {
            unsigned id, nondet, symbol_len_local, num_of_bits_local, num_of_symbols_local;
            get_file_info(argv[i], id, nondet, symbol_len_local, num_of_bits_local);
            num_of_symbols_local = num_of_bits_local / symbol_len_local;
            if (i == 1) {
                symbol_len = symbol_len_local - nondet;
                num_of_bits = num_of_bits_local - nondet * num_of_symbols_local;
                num_of_symbols = num_of_symbols_local;
            } else {
                assert(symbol_len == symbol_len_local - nondet);
                assert(num_of_bits == num_of_bits_local - nondet * num_of_symbols_local);
                assert(num_of_symbols == num_of_symbols_local);
            }
            DFA *dfa = dfaImport(argv[i], NULL, NULL);
            dfa = determinize(dfa, symbol_len_local, num_of_symbols_local, nondet);
            dfas_orig[id] = dfa;
        }
    } catch (const std::invalid_argument &e) {
        std::cerr << "Error: " << "Invalid .mata file naming convention" << std::endl;
        std::cerr << "Expected format: {id}_{nondet}_{symbol_len}_{num_of_bits}.mona where:" << std::endl;
        std::cerr << "  - id: unique identifier of the NFT, contiguous sequence starting from 0" << std::endl;
        std::cerr << "  - nondet: number of nondeterministic bits per symbol" << std::endl;
        std::cerr << "  - symbol_len: length of the symbol in bits" << std::endl;
        std::cerr << "  - num_of_bits: total number of bits in NFT transition between states with level 0" << std::endl;
        return 1;
    }


    // Benchmarking
    ///////////////////////////////////////////////////////////////
    Timer timer;
    std::vector<DFA*> dfas;

    // Project-out first and second symbol benchmarks
    // Long pipe benchmark
    // NFT1 | NFT2 | ... | NFTn
    dfas = copy_dfa_vector(dfas_orig);
    timer.start();
    DFA *res_long = long_pipe_benchmark(dfas, symbol_len);
    timer.stop();
    // res_long = dfaMinimize(res_long);
    timer.log_duration();

    return 0;
}
