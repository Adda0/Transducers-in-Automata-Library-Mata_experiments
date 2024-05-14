#!/usr/bin/env python3


import subprocess
import argparse
import sys
import os
import datetime
import seaborn

import datetime
import pandas as pd
import numpy as np
import re as re
import tabulate as tab
import plotnine as p9
import math
import mizani.labels as mizani
import warnings

# from __future__ import annotations
# warnings.filterwarnings('ignore')


from plotnine.themes.themeable import legend_key_width
# in seconds
TIMEOUT = 120_000
TIMEOUT_VAL = TIMEOUT
TIME_MIN = 0.01

HEADERS = ["method", "TOs", "min", "max", "mean", "q(0.25)", "median", "q(0.75)", "std. dev"]
ALL_TOOLS = ["mata", "mona"]


def composition_table(df, all_tools, operation):

    print(f"time:  {datetime.datetime.now()}")
    print(f"# of formulae: {len(df)}")

    summary_times = dict()
    tos = dict()

    # for column in df.columns:
    #     if "runtime" in column:
    #         df[column].fillna(TIMEOUT_VAL, inplace=True)
    for col in df.columns:
        if re.search('-runtime', col):
            tos[col] = dict()
            tos[col]['tos'] = df[col].isna().sum()
            # df[col] = df[col].str.strip()
            # summary_times[col]['unknowns'] = df[df[col] == "unknown"].shape[0] #[df[col] == "unknown"].shape[0]

    # print(tos)

    # Remove unknowns
    for col in df.columns:
        if re.search('-runtime', col):
            df = df.drop(df[df[col] == np.nan].index)
    # for tool in all_tools:
    #   df.loc[df[tool + "-result"] == "unknown", tool + '-runtime'] = np.NaN

    for col in df.columns:
        if re.search('-runtime', col):
            summary_times[col] = dict()
            summary_times[col]['max'] = df[col].max()
            summary_times[col]['min'] = df[col].min()
            summary_times[col]['mean'] = df[col].mean()
            summary_times[col]['q_025'] = df[col].quantile(0.25)
            summary_times[col]['median'] = df[col].median()
            summary_times[col]['q_075'] = df[col].quantile(0.75)
            summary_times[col]['std'] = df[col].std()
            summary_times[col]['tos'] = tos[col]['tos']

    df_summary_times = pd.DataFrame(summary_times).transpose()



    tab_interesting = []
    for i in all_tools:
        row = df_summary_times.loc[i + '-runtime']
        # unknown_row = dict(df_summary_times.loc[i + '-result'])
        row_dict = dict(row)
        row_dict.update({'name': i})
        tab_interesting.append([row_dict['name'],
                                row_dict['tos'],
                                row_dict['min'],
                                row_dict['max'],
                                row_dict['mean'],
                                row_dict['q_025'],
                                row_dict['median'],
                                row_dict['q_075'],
                                row_dict['std'],

                                # unknown_row['timeouts']
                                # unknown_row["unknowns"]
                                ])

    print("###################################################################################")
    print("####                                   Table 1                                 ####")
    print("###################################################################################")
    table = tab.tabulate(tab_interesting, headers=HEADERS, tablefmt="github")
    print(table)
    table_to_file(tab_interesting, HEADERS, f"{operation}")
    print("\n\n")

    # sanitizing NAs
    # for col in df.columns:
    #     if re.search('-runtime$', col):
    #         df[col].fillna(TIMEOUT_VAL, inplace=True)
    #         df.loc[df[col] < TIME_MIN, col] = TIME_MIN  # to remove 0 (in case of log graph)


    # # comparing wins/loses
    # compare_methods = []
    # for t in all_tools:
    #   if t == main_tool:
    #     continue
    #   compare_methods.append((main_tool + "-runtime", t + "-runtime"))


    # compare_methods = [("noodler-runtime", "z3-runtime"),
    #                    ("noodler-runtime", "cvc4-runtime")
    #                   ]

    # tab_wins = []
    # for left, right in compare_methods:
    #     left_over_right = df[df[left] < df[right]]
    #     right_timeouts = left_over_right[left_over_right[right] == TIMEOUT_VAL]

    #     right_over_left = df[df[left] > df[right]]
    #     left_timeouts = right_over_left[right_over_left[left] == TIMEOUT_VAL]

    #     tab_wins.append([right, len(left_over_right), len(right_timeouts), len(right_over_left), len(left_timeouts)])

    # headers_wins = ["method", "wins", "wins-timeouts", "loses", "loses-timeouts"]
    # print("######################################################################")
    # print("####                             Table 2                          ####")
    # print("######################################################################")
    # print(tab.tabulate(tab_wins, headers=headers_wins, tablefmt="github"))
    # #table_to_file(tab_wins, headers_wins, out_prefix + "_table1right")
    # print("\n\n")



def projection_table(df, all_tools):

    print(f"time:  {datetime.datetime.now()}")
    print(f"# of formulae: {len(df)}")

    summary_times = dict()
    tos = dict()

    # for column in df.columns:
    #     if "runtime" in column:
    #         df[column].fillna(TIMEOUT_VAL, inplace=True)
    for col in df.columns:
        if re.search('-runtime', col):
            tos[col] = dict()
            tos[col]['tos'] = df[col].isna().sum()
            # df[col] = df[col].str.strip()
            # summary_times[col]['unknowns'] = df[df[col] == "unknown"].shape[0] #[df[col] == "unknown"].shape[0]

    # Remove unknowns
    for col in df.columns:
        if re.search('-runtime', col):
            df = df.drop(df[df[col] == np.nan].index)
    # for tool in all_tools:
    #   df.loc[df[tool + "-result"] == "unknown", tool + '-runtime'] = np.NaN

    for col in df.columns:
        if re.search('-runtime-', col):
            summary_times[col] = dict()
            summary_times[col]['max'] = df[col].max()
            summary_times[col]['min'] = df[col].min()
            summary_times[col]['mean'] = df[col].mean()
            summary_times[col]['q_025'] = df[col].quantile(0.25)
            summary_times[col]['median'] = df[col].median()
            summary_times[col]['q_075'] = df[col].quantile(0.75)
            summary_times[col]['std'] = df[col].std()
            summary_times[col]['tos'] = tos[col]['tos']

    df_summary_times = pd.DataFrame(summary_times).transpose()



    tab_interesting = []
    for i in all_tools:
        for tape in range(2):
            row = df_summary_times.loc[i + '-runtime-' + str(tape)]
            # unknown_row = dict(df_summary_times.loc[i + '-result'])
            row_dict = dict(row)
            row_dict.update({'name': i + '-' + str(tape)})
            tab_interesting.append([row_dict['name'],
                                    row_dict['tos'],
                                    row_dict['min'],
                                    row_dict['max'],
                                    row_dict['mean'],
                                    row_dict['q_025'],
                                    row_dict['median'],
                                    row_dict['q_075'],
                                    row_dict['std'],
                                    # unknown_row['timeouts']
                                    # unknown_row["unknowns"]
                                    ])

    print("###################################################################################")
    print("####                                   Table 1                                 ####")
    print("###################################################################################")
    table = tab.tabulate(tab_interesting, headers=HEADERS, tablefmt="github", floatfmt=".2f")
    print(table)
    table_to_file(tab_interesting, HEADERS, "projection")
    print("\n\n")

    # sanitizing NAs
    # for col in df.columns:
    #     if re.search('-runtime$', col):
    #         df[col].fillna(TIMEOUT_VAL, inplace=True)
    #         df.loc[df[col] < TIME_MIN, col] = TIME_MIN  # to remove 0 (in case of log graph)


    # # comparing wins/loses
    # compare_methods = []
    # for t in all_tools:
    #   if t == main_tool:
    #     continue
    #   compare_methods.append((main_tool + "-runtime", t + "-runtime"))


    # compare_methods = [("noodler-runtime", "z3-runtime"),
    #                    ("noodler-runtime", "cvc4-runtime")
    #                   ]

    # tab_wins = []
    # for left, right in compare_methods:
    #     left_over_right = df[df[left] < df[right]]
    #     right_timeouts = left_over_right[left_over_right[right] == TIMEOUT_VAL]

    #     right_over_left = df[df[left] > df[right]]
    #     left_timeouts = right_over_left[right_over_left[left] == TIMEOUT_VAL]

    #     tab_wins.append([right, len(left_over_right), len(right_timeouts), len(right_over_left), len(left_timeouts)])

    # headers_wins = ["method", "wins", "wins-timeouts", "loses", "loses-timeouts"]
    # print("######################################################################")
    # print("####                             Table 2                          ####")
    # print("######################################################################")
    # print(tab.tabulate(tab_wins, headers=headers_wins, tablefmt="github"))
    # #table_to_file(tab_wins, headers_wins, out_prefix + "_table1right")
    # print("\n\n")



# For reading in files
def read_file(filename):
    """Reads a CSV file into Panda's data frame"""
    df_loc = pd.read_csv(
        filename,
        sep=",",
        comment="#",
        na_values=['ERR', 'TO', 'MISSING'],
        # na_values=['TO', 'MISSING'],
        # na_values=['TO'],
        )
    # for column in df_loc.columns:
    #     if "runtime" in column:
    #         df_loc[column].fillna(TIMEOUT_VAL, inplace=True)
    for column in df_loc.columns:
        if "runtime" in column:
            df_loc[column] = df_loc[column] / 1_000
    print(f"Handling {filename}:")
    print(f"# of instances: {len(df_loc) / 3}")
    return df_loc

# For reading in files
def read_file_no_nan(filename):
    """Reads a CSV file into Panda's data frame"""
    df_loc = pd.read_csv(
        filename,
        sep=";",
        comment="#",
        # na_values=['ERR', 'TO', 'MISSING'],
        # na_values=['TO', 'MISSING'],
        # na_values=['TO'],
        )
    return df_loc


# For printing scatter plots
def scatter_plot(
    df, xcol, ycol, domain, operation: str | None = None, xname=None, yname=None, log=False, width=6, height=6, clamp=True, tickCount=5, title = None, tick_scale= None
):
    assert len(domain) == 2

    POINT_SIZE = 1.0
    DASH_PATTERN = (0, (6, 2))

    if xname is None:
        xname = xcol
    if yname is None:
        yname = ycol

    # formatter for axes' labels
    # if tick_scale:
    ax_formatter = mizani.custom_format('{:n}')
        # ax_formatter = mizani.label_timedelta(units='us')
    # else:
        # ax_formatter = mizani.label_timedelta(units='us')
    # ax_formatter = mizani.custom_format(lambda x: f"{(result:=/1000)}")

    if clamp:  # clamp overflowing values if required
        df = df.copy(deep=True)
        df.loc[df[xcol] > domain[1], xcol] = domain[1]
        df.loc[df[ycol] > domain[1], ycol] = domain[1]

    for column in df.columns:
        if "runtime" in column:
            df[column] = df[column].fillna(TIMEOUT_VAL)

    # generate scatter plot
    scatter = p9.ggplot(df)
    scatter += p9.aes(x=xcol, y=ycol,
                      color="Benchmark"
                      )
    scatter += p9.geom_point(size=POINT_SIZE, na_rm=True)
    args = {}
    if title:
        args["title"] = title
    elif operation:
        args["title"] = operation.replace('_', ' ').capitalize()

    scatter += p9.labs(x=xname, y=yname, **args
    )
    scatter += p9.theme(legend_key_width=2)
    scatter += p9.scale_color_hue(l=0.4, s=0.9, h=0.1)

    # rug plots
    scatter += p9.geom_rug(na_rm=True, sides="tr", alpha=0.05)

    if log:  # log scale
        scatter += p9.scale_x_log10(limits=domain, labels=ax_formatter)
        scatter += p9.scale_y_log10(limits=domain, labels=ax_formatter)
    else:
        scatter += p9.scale_x_continuous(limits=domain, labels=ax_formatter)
        scatter += p9.scale_y_continuous(limits=domain, labels=ax_formatter)

    # scatter += p9.theme_xkcd()
    scatter += p9.theme_bw()
    scatter += p9.theme(panel_grid_major=p9.element_line(color='#666666', alpha=0.5))
    scatter += p9.theme(panel_grid_minor=p9.element_blank())
    scatter += p9.theme(figure_size=(width, height))
    scatter += p9.theme(axis_text=p9.element_text(size=24, color="black"))
    scatter += p9.theme(axis_title=p9.element_text(size=24, color="black"))
    scatter += p9.theme(legend_text=p9.element_text(size=12))

    # generate additional lines
    scatter += p9.geom_abline(intercept=0, slope=1, linetype=DASH_PATTERN)  # diagonal
    scatter += p9.geom_vline(xintercept=domain[1], linetype=DASH_PATTERN)  # vertical rule
    scatter += p9.geom_hline(yintercept=domain[1], linetype=DASH_PATTERN)  # horizontal rule

    res = scatter

    return res


# Print a matrix of plots
def matrix_plot(list_of_plots, cols):
    assert len(list_of_plots) > 0
    assert cols >= 0

    matrix_plot = None
    row = None
    for i in range(0, len(list_of_plots)):
        if i % cols == 0:  # starting a new row
            row = list_of_plots[i]
        else:
            row |= list_of_plots[i]

        if (i + 1) % cols == 0 or i + 1 == len(list_of_plots):  # last chart in a row
            if not matrix_plot:  # first row finished
                matrix_plot = row
            else:
                matrix_plot &= row

    return matrix_plot


# table to LaTeX file
def table_to_file(table, headers, out_file):
    with open(f"plots/{out_file}_table.tex", mode='w') as fl:
        print(tab.tabulate(table, headers=headers, tablefmt="latex", floatfmt=".2f"), file=fl)


def projection():
    webapp_projection_df = read_file("../results/processed/webapp_projection.csv")
    transducer_plus_projection_df = read_file("../results/processed/transducer-plus_projection.csv")

    webapp_projection_df = webapp_projection_df.groupby(["benchmark", "operation"], as_index=False).mean()
    webapp_projection_df["Benchmark"] = "webapp"

    transducer_plus_projection_df = transducer_plus_projection_df.groupby(["benchmark", "operation"], as_index=False).mean()
    transducer_plus_projection_df["Benchmark"] = "transducer plus"

    # print(webapp_projection_df)
    # print(transducer_plus_projection_df)

    projection_df = pd.concat([webapp_projection_df, transducer_plus_projection_df], ignore_index=True)
    # print(projection_df)
    # projection_df = webapp_projection_df.append(transducer_plus_projection_df, ignore_index=True)

    scatter = scatter_plot(
        projection_df, "mata-runtime-0", "mona-runtime-0", [0, 15], xname="Mata [ms]", yname="Mona [ms]",
        title="Projection to tape 1", log=False, width=12, height=6, clamp=True, tickCount=5, operation="projection",
        tick_scale=1000
    )
    # scatter.show()
    scatter.save(filename="plots/projection_scatter_0.pdf", dpi=1000)

    max_runtime = max(projection_df["mata-runtime-1"].max(), projection_df["mona-runtime-1"].max())
    scatter = scatter_plot(
        projection_df, "mata-runtime-1", "mona-runtime-1", [0, 100], xname="Mata [ms]", yname="Mona [ms]",
        title="Projection to tape 0" , log=False, width=12, height=6, clamp=True, tickCount=5, operation="projection",
        tick_scale=1000
    )
    # scatter.show()
    scatter.save(filename="plots/projection_scatter_1.pdf", dpi=1000)

    projection_table(projection_df, ALL_TOOLS)

def composition(operation):
    webapp_df = read_file(f"../results/processed/webapp_{operation}.csv")
    transducer_plus_df = read_file(f"../results/processed/transducer-plus_{operation}.csv")

    webapp_df = webapp_df.groupby(["benchmark", "operation"], as_index=False).mean()
    webapp_df["Benchmark"] = "webapp"

    transducer_plus_df = transducer_plus_df.groupby(["benchmark", "operation"], as_index=False).mean()
    transducer_plus_df["Benchmark"] = "transducer plus"

    # print(webapp_df)
    # print(transducer_plus_df)

    df = pd.concat([webapp_df, transducer_plus_df], ignore_index=True)
    # print(df)

    max_runtime = max(df["mata-runtime"].max(), df["mona-runtime"].max())
    scatter = scatter_plot(
        df, "mata-runtime", "mona-runtime", [0, max_runtime], xname="Mata [ms]", yname="Mona [ms]",
        title=f"{operation.replace('_', ' ').title()}", log=False, width=12, height=6, clamp=True, tickCount=5, operation=operation
    )
    # scatter.show()
    scatter.save(filename=f"plots/{operation}_scatter.pdf", dpi=1000)

    composition_table(df, ALL_TOOLS, operation)


def main():
    parser = argparse.ArgumentParser(
        prog='Analyse experiment results',
        description='Analyse results of experiments.'
    )
    # parser.add_argument('results_file', action="store", metavar="RESULTS.csv",
    #                     help="Path to the CSV file of the results of the experiments.")
    args = parser.parse_args(sys.argv[1:])

    projection()
    composition("composition")
    composition("composition_construct_replace")
    composition("apply_literal")
    composition("apply_literal_backward")
    composition("apply_language")
    composition("apply_language_backward")


if __name__ == "__main__":
    main()
