#!/usr/bin/env sh

# Running projection benchmarks.
./run_on_benchmark.py --runs 3 --timeout 120 projection ../benchmarks/non-incremental-QF_SLIA-20230403-webapp/projection/
./run_on_benchmark.py --runs 3 --timeout 120 projection ../benchmarks/non-incremental-QF_SLIA-20230331-transducer-plus/projection/

# Running composition benchmarks.
./run_on_benchmark.py --runs 3 --timeout 120 composition ../benchmarks/non-incremental-QF_SLIA-20230403-webapp/composition/pair/
./run_on_benchmark.py --runs 3 --timeout 120 composition ../benchmarks/non-incremental-QF_SLIA-20230331-transducer-plus/composition/pair/

# Running composition constring replace benchmarks.
./run_on_benchmark.py --runs 3 --timeout 120 composition ../benchmarks/non-incremental-QF_SLIA-20230403-webapp/composition/construct_replace/
./run_on_benchmark.py --runs 3 --timeout 120 composition ../benchmarks/non-incremental-QF_SLIA-20230331-transducer-plus/composition/construct_replace/

# Running apply language benchmarks.
./run_on_benchmark.py --runs 3 --timeout 120 apply_language ../benchmarks/non-incremental-QF_SLIA-20230403-webapp/apply_language/
./run_on_benchmark.py --runs 3 --timeout 120 apply_language ../benchmarks/non-incremental-QF_SLIA-20230331-transducer-plus/apply_language/

# Running apply language backward benchmarks.
./run_on_benchmark.py --runs 3 --timeout 120 apply_language_backward ../benchmarks/non-incremental-QF_SLIA-20230403-webapp/apply_language_backward/
./run_on_benchmark.py --runs 3 --timeout 120 apply_language_backward ../benchmarks/non-incremental-QF_SLIA-20230331-transducer-plus/apply_language_backward/

# Running apply literal benchmarks.
./run_on_benchmark.py --runs 3 --timeout 120 apply_literal ../benchmarks/non-incremental-QF_SLIA-20230403-webapp/apply_literal/
./run_on_benchmark.py --runs 3 --timeout 120 apply_literal ../benchmarks/non-incremental-QF_SLIA-20230331-transducer-plus/apply_literal/

# Running apply literal backward benchmarks.
./run_on_benchmark.py --runs 3 --timeout 120 apply_literal_backward ../benchmarks/non-incremental-QF_SLIA-20230403-webapp/apply_literal_backward/
./run_on_benchmark.py --runs 3 --timeout 120 apply_literal_backward ../benchmarks/non-incremental-QF_SLIA-20230331-transducer-plus/apply_literal_backward/
