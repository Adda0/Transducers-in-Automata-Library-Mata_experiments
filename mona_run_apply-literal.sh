#!/bin/bash

MATA_AUTOMATA=""
OUTPUT_DIR=""
TEMP_DIR_CREATED=false
DOT=false
MONA=mona/apply-literal
MATA2MONA=mata2mona/mata2mona.py
MONA2MATA=mona2mata/mona2mata.py

# Cleanup function to remove temporary files
function cleanup {
    rm -f output.mona
    if [ "$TEMP_DIR_CREATED" = true ]; then
            rm -rf $OUTPUT_DIR
    fi
}

# Trap SIGINT to cleanup temporary files
trap cleanup SIGINT

# Print help message and exit
function help {
        echo "Usage: $0 <INPUT_FILE> [OUTPUT_FOLDER] [-h|--help] [--dot]"
        echo ""
        echo "Computes operations defined in mona/main on MATA automata from the input file."
        echo "The results, .mona and .dot (if --dot is set) files, are stored in current directory."
        echo ""
        echo "   INPUT_FILE:        The input file with MATA automata."
        echo "   OUTPUT_FOLDER:     The output folder to store the generated MONA automata."
        echo "   -h, --help:        Print this help message."
        echo "   --dot:             Generate DOT files for the generated MONA automata. And"
        echo "                      for resulting MATA automaton."
}

# Parse command line arguments
while (( "$#" )); do
    case "$1" in
        -h|--help)
            help
            exit 0
            ;;
        --dot)
            DOT=true
            shift
            ;;
        *)
            if [ -z "$MATA_AUTOMATA" ]; then
                MATA_AUTOMATA=$1
            elif [ -z "$OUTPUT_DIR" ]; then
                OUTPUT_DIR=$1
            else
                echo "Unknown argument: $1"
                help
                exit 1
            fi
            shift
            ;;
    esac
done

# Check if input folder is provided
if [ -z "$MATA_AUTOMATA" ]; then
        echo "Input folder is required."
        help
fi

# If output folder is not provided, create a temporary folder
if [ -z "$OUTPUT_DIR" ]; then
        TEMP_DIR_CREATED=true
        OUTPUT_DIR=$(mktemp -d)
fi

# Check if mona, mata2mona and mona2mata are installed.
if [ ! -f "$MONA" ]; then
        echo "The mona/main executable is not found. Please compile mona first."
        exit 1
fi
if [ ! -f "$MATA2MONA" ]; then
        echo "The mata2mona/mata2mona.py script is not found."
        exit 1
fi
if [ ! -f "$MONA2MATA" ]; then
        echo "The mona2mata/mona2mata.py script is not found."
        exit 1
fi

# Expand mata automata for composition with self loops and synchronized levels.
./mona/expand_composition_inputs $MATA_AUTOMATA $OUTPUT_DIR

# Convert MATA automata to MONA automata
python3 $MATA2MONA $OUTPUT_DIR/expanded_before_composition.mata $OUTPUT_DIR

#echo "list output dir"
#ls $OUTPUT_DIR
#cat $OUTPUT_DIR/expanded_before_composition.mata

# Run mona on the generated MONA automata
if [ $DOT = true ]; then
    ./$MONA $OUTPUT_DIR/*.mona 1> output.mona
else
#    echo "running Mona"
    ./$MONA $OUTPUT_DIR/*.mona
fi

# Convert MONA automata to MATA and DOT automata
if [ $DOT = true ]; then
    random_input=$(ls $OUTPUT_DIR/*.mona | head -n 1)
    # {i}_{bitvector.nondet_prefix_len}_{bitvector_total_len}_{num_of_vars}.mona
    nondet_prefix_len=$(echo $random_input | cut -d'_' -f2)
    total_len=$(echo $random_input | cut -d'_' -f4 | cut -d'.' -f1)
    num_of_bits=$((total_len - nondet_prefix_len))
    python3 $MONA2MATA output.mona $num_of_bits --dot --trim > output.dot
fi

# Cleanup temporary files
cleanup
