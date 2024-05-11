#!/usr/bin/env python3


import subprocess
import argparse
import sys
import os
import datetime


now = datetime.datetime.now()
now_time = str(now.time()).replace(":", "-").split(".")[0]
file_name = f"results/raw/{now.date()}-{now_time}.csv"
output_file = open(file_name, "w+")
output_file.write(f"benchmark,operation,mata-runtime,mona-runtime\n")


def run_operation(file, operation, runs: int = 1, TIMEOUT: int = 120):
    print(f"Running {operation} on: {file}")
    for i in range(runs):
        output_file.write(f"{file},{operation}")
        if operation == "composition":
            # Run Mata.
            try:
                print("Running mata composition")
                res = subprocess.run(["./mata/composition", f"{file}"], timeout=TIMEOUT, text=True, capture_output=True)
                output_file.write(f"{res.stdout}")
            except subprocess.TimeoutExpired as e:
                output_file.write(f",TO")
            # Run Mona.
            try:
                print("Running mona composition")
                res = subprocess.run(["./mona_run_composition.sh", f"{file}"], timeout=TIMEOUT, text=True, capture_output=True)
                output_file.write(f"{res.stdout}")
            except subprocess.TimeoutExpired as e:
                output_file.write(f",TO")
        elif operation == "projection":
            # Run Mata.
            try:
                res = subprocess.run(["./mata/projection", f"{file}"], timeout=TIMEOUT, text=True, capture_output=True)
                output_file.write(f"{res.stdout}")
            except subprocess.TimeoutExpired as e:
                output_file.write(f",TO")
            # Run Mona.
            try:
                res = subprocess.run(["./mona_run_projection.sh", f"{file}"], timeout=TIMEOUT, text=True, capture_output=True)
                output_file.write(f"{res.stdout}")
            except subprocess.TimeoutExpired as e:
                output_file.write(f",TO")
        elif operation == "apply_language":
            # Run Mata.
            try:
                res = subprocess.run(["./mata/apply-language", f"{file}"], timeout=TIMEOUT, text=True, capture_output=True)
                output_file.write(f"{res.stdout}")
            except subprocess.TimeoutExpired as e:
                output_file.write(f",TO")
            # Run Mona.
            try:
                res = subprocess.run(["./mona_run_apply-language.sh", f"{file}"], timeout=TIMEOUT, text=True, capture_output=True)
                output_file.write(f"{res.stdout}")
            except subprocess.TimeoutExpired as e:
                output_file.write(f",TO")
        elif operation == "apply_literal":
            # Run Mata.
            try:
                res = subprocess.run(["./mata/apply-literal", f"{file}"], timeout=TIMEOUT, text=True, capture_output=True)
                output_file.write(f"{res.stdout}")
            except subprocess.TimeoutExpired as e:
                output_file.write(f",TO")
            # Run Mona.
            try:
                res = subprocess.run(["./mona_run_apply-literal.sh", f"{file}"], timeout=TIMEOUT, text=True, capture_output=True)
                output_file.write(f"{res.stdout}")
            except subprocess.TimeoutExpired as e:
                output_file.write(f",TO")

        output_file.write(f"\n")


def walk(path, operation, runs, timeout):
    if os.path.isdir(path):
        print(f"Entering: {path}")
        for current_path, directories, files in os.walk(path):
            for file in files:
                file_path = os.path.join(current_path, file)
                run_operation(file_path, operation, runs, timeout)
            for directory in directories:
                directory_path = os.path.join(current_path, directory)
                walk(directory_path, operation, runs, timeout)

    elif os.path.isfile(path):
        run_operation(path, operation, runs, timeout)
    else:
        raise ValueError(f"Invalid path {path}.")


def main():
    parser = argparse.ArgumentParser(
        prog='Run on benchmark',
        description='Run operation on a benchmark'
    )
    parser.add_argument('operation', action="store", metavar="OPERATION",
                        help="Operation to run the benchmark on.")
    parser.add_argument('path', action="store", nargs="+", metavar="PATH",
                        help="Path to the benchmark files or directories to run operation on.")
    parser.add_argument('--runs', action="store", type=int, metavar="RUNS", default=1,
                        help="Number of runs to perform on each benchmark.")
    parser.add_argument('--timeout', action="store", type=int, metavar="TIMEOUT", default=120,
                        help="Timeout to stop running the benchmark instance.")

    args = parser.parse_args(sys.argv[1:])

    for path in args.path:
        walk(path, args.operation, args.runs, args.timeout)

    output_file.close()

if __name__ == "__main__":
    main()
