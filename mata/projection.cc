#include <cassert>
#include <chrono>
#include <functional>
#include <iomanip>
#include <iostream>
#include <vector>
#include <set>
#include <sstream>
#include <unistd.h>
#include <fstream>


#include <mata/alphabet.hh>
#include <mata/nfa/nfa.hh>
#include <mata/nft/nft.hh>
#include <mata/nft/builder.hh>

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
        duration_mus += (end_time - start_time).count()
         / 1000
         ;
        running = false;
    }

    void reset() {
        duration_mus = 0;
        running = false;
    }

    void log_duration() {
        std::cout << "," << duration_mus;
    }

};


int main(int argc, char *argv[]) {
    if (argc != 2) {
        std::cerr << "Usage: " << argv[0] << " mata_file.mata" << std::endl;
        return 1;
    }

    std::string filename = argv[1];

    std::fstream fs(filename, std::ios::in);
    if (!fs) {
        std::cerr << "Could not open file \'" << filename << "'\n";
        return EXIT_FAILURE;
    }

    mata::parser::Parsed parsed;
    std::vector<mata::nft::Nft> nfts;
    try {
        const std::string nft_str = "NFT";
        mata::parser::Parsed parsed{ mata::parser::parse_mf(fs) };
        for (auto& parsed_sec: parsed) {
            const std::string automaton_type{ parsed_sec.type };
            if (automaton_type.compare(0, nft_str.length(), nft_str) != 0) {
                throw std::runtime_error("The type of input automaton is '" + automaton_type + "'. Required is 'NFT'\n");
            }
            mata::IntAlphabet alphabet;
            // return construct(IntermediateAut::parse_from_mf(parsed)[0], &alphabet);
            nfts.push_back(mata::nft::builder::construct(parsed[0], &alphabet));
        }
    }
    catch (const std::exception& ex) {
        fs.close();
        std::cerr << "libMATA error: " << ex.what() << "\n";
        return EXIT_FAILURE;
    }

    Timer timer;
    mata::nft::Nft projected;
    for (auto& nft: nfts) {
        // nft.print_to_mata(std::cout);
        timer.start();
        projected = mata::nft::project_out(nft, 0);
        timer.stop();
        timer.log_duration();
        // projected.print_to_mata(std::cout);
        timer.reset();

        timer.start();
        projected = mata::nft::project_out(nft, 1);
        timer.stop();
        timer.log_duration();
        // projected.print_to_mata(std::cout);
    }
    std::cout << "\n";
    return EXIT_SUCCESS;
}
