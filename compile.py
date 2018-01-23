#!/usr/bin/env python3


"""Compile specification for problem sheet into latex skeleton.

Copyright (c) 2018 Ragnar Ardal

https://opensource.org/licenses/MIT
"""


import argparse
import os
import pathlib
import string
import warnings


CHAPTER = "\\chapter{{{}}}{{{}}}\n"
SUBCHAPTER = "\t\\subchapter{{{}}}{{{}}}\n"
SUBFILE = "\t\t\\subfile{{problems/{}.{}.{}{}.tex}}\n"
BEGIN_DOC = "\\begin{document}\n"
END_DOC = "\\end{document}"
PROBLEM_PREAMBLE = """\\documentclass[../main.tex]{subfiles}\n"""
MAIN_CONTENT = r"""\title{{{}}}
\date{{}}
\author{{}}
\maketitle
"""
MAIN_PREAMBLE = r"""\documentclass[11pt,a4paper]{article}

\usepackage{enumerate}
\usepackage{subfiles}

\usepackage{mathtools}
\usepackage{amssymb}

\newcommand{\chapter}[2]{%
\setcounter{section}{#1-1}%
\section{#2}%
}

\newcommand{\subchapter}[2]{%
\setcounter{subsection}{#1-1}%
\subsection{#2}%
}

\newcommand{\problem}[1]{%
\setcounter{subsubsection}{#1-1}%
\subsubsection{\hfill}%
}

\newcommand{\solution}{%
\subsubsection*{Solution}%
}

% Misc math operators

\DeclarePairedDelimiter{\ceil}{\lceil}{\rceil}
\DeclarePairedDelimiter{\floor}{\lfloor}{\rfloor}

% Operators for predicate logic

\DeclareMathOperator{\T}{\text{\textbf T}}
\DeclareMathOperator{\F}{\text{\textbf F}}
\DeclareMathOperator{\lthen}{\to}
\DeclareMathOperator{\limplies}{\to}
\DeclareMathOperator{\lwhen}{\gets}
\DeclareMathOperator{\lif}{\gets}
\DeclareMathOperator{\liff}{\leftrightarrow}
\DeclareMathOperator{\lxor}{\oplus}

% Sets

\DeclarePairedDelimiter{\set}
	{\lbrace}
	{\rbrace}
\DeclareMathOperator{\ZZ}{\mathbb{Z}}
\DeclareMathOperator{\SetOfIntegers}{\ZZ}
\DeclareMathOperator{\ZZPos}{\mathbb{Z}^+}
\DeclareMathOperator{\SetOfPositiveIntegers}{\ZZPos}
\DeclareMathOperator{\NN}{\mathbb{N}}
\DeclareMathOperator{\SetOfNaturalNumbers}{\NN}
\DeclareMathOperator{\RR}{\mathbb{R}}
\DeclareMathOperator{\SetOfRealNumbers}{\RR}
\DeclareMathOperator{\RRPos}{\mathbb{R}^+}
\DeclareMathOperator{\SetOfPositiveRealNumbers}{\RRPos}
\DeclareMathOperator{\QQ}{\mathbb{Q}}
\DeclareMathOperator{\SetOfRationalNumbers}{\QQ}
\DeclareMathOperator{\CC}{\mathbb{C}}
\DeclareMathOperator{\SetOfComplexNumbers}{\CC}
"""


def main(
        spec,
        dest=None,
        *,
        overwrite=False,
    ):
    # TODO: Docstring
    # Resolve paths
    spec = pathlib.Path(spec).expanduser().resolve()
    if dest is None:
        dest = spec.parent
    else:
        dest = pathlib.Path(dest).expanduser().resolve()

    # Make destination directory
    dest.mkdir(exist_ok=True)
    (dest/"problems").mkdir(exist_ok=True)

    # Read all the lines of the specification file
    lines = iter(open(spec, "r").read().splitlines())

    # The title of the latex document
    title = next(lines)

    # Create the main document
    main_file_path = dest/"main.tex"
    if main_file_path.exists() and not overwrite:
        # The file exists and we don't want to overwrite it
        print("Not overwriting main.tex")
        main_file = open(os.devnull, "w")
    else:
        print("Writing main.tex")
        main_file = open(main_file_path, "w")
        main_file.write(MAIN_PREAMBLE)
        main_file.write("\n")
        main_file.write(BEGIN_DOC)
        main_file.write("\n")
        main_file.write(MAIN_CONTENT.format(title))
        main_file.write("\n")

    # Whether a processing error has occurred
    panic_mode = False

    # The numbers of the things (in string form)
    chapter = None
    subchapter = None
    problem = None
    subproblems = None  # This will just be a string; e.g., "abcf"

    for line in lines:  # pylint: disable=too-many-nested-blocks
        original_line = line
        line = line.split(maxsplit=2)
        if line:
            try:
                if line[0] == "#":
                    # # chapter_number chapter_name
                    assert len(line) == 3
                    chapter = line[1]
                    main_file.write(CHAPTER.format(chapter, line[2]))
                elif line[0] == "##":
                    # ## subchapter_number subchapter_name
                    assert len(line) == 3
                    subchapter = line[1]
                    main_file.write(SUBCHAPTER.format(subchapter, line[2]))
                else:
                    if line[0] == "###":
                        # ### problem_number subproblems
                        assert len(line) < 4
                        problem = line[1]
                        subproblems = line[2] if len(line) == 3 else ""
                    else:
                        # problem_number subproblems
                        assert len(line) < 3
                        problem = line[0]
                        subproblems = line[1] if len(line) == 2 else ""
                    assert set(subproblems).issubset(string.ascii_lowercase)
                    problem_file_name = "{}.{}.{}{}.tex".format(
                        chapter,
                        subchapter,
                        problem,
                        subproblems,
                    )
                    problem_file_path = dest/"problems"/problem_file_name
                    if problem_file_path.exists() and not overwrite:
                        # It already exists and we are not to overwrite it
                        print("Not overwriting", problem_file_name)
                    else:
                        print("Writing", problem_file_name)
                        content = []
                        content.append(PROBLEM_PREAMBLE)
                        content.append("\n")
                        content.append(BEGIN_DOC)
                        content.append("\n")

                        problem_structure = []
                        if subproblems:
                            problem_structure.append("\\begin{enumerate}[a)]\n")
                            subproblem_number = 0
                            for character in subproblems:
                                next_number = ord(character) - ord("a")
                                if next_number != subproblem_number:
                                    problem_number = next_number
                                    problem_structure.append(
                                        "\t\\setcounter{{enumi}}{{{}}}\n".format(problem_number),
                                    )
                                problem_structure.append("\t\\item \n")
                                subproblem_number += 1
                            problem_structure.append("\\end{enumerate}\n")
                        else:
                            problem_structure.append("\n")



                        content.append("\\problem{" + problem + "}\n")
                        content.extend(problem_structure)
                        content.append("\n")
                        content.append("\\solution\n")
                        content.extend(problem_structure)
                        content.append("\n")

                        content.append(END_DOC)

                        problem_file = open(problem_file_path, "w")
                        for content_line in content:
                            problem_file.write(content_line)

                    # Lastly, write to the main file
                    # If this or a previous step fails, the main file can still be compiled

                    main_file.write(
                        SUBFILE.format(
                            chapter,
                            subchapter,
                            problem,
                            subproblems,
                        ),
                    )
                    main_file.write("\t\t\\pagebreak\n")

            except Exception:  # pylint: disable=broad-except
                if panic_mode:
                    warnings.warn("Entering panic mode, output may be faulty")
                    panic_mode = True
                warnings.warn("Failure processing specification line: " + repr(original_line))

    main_file.write("\n")
    main_file.write(END_DOC)


def _run_as_script():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "specification_file",
        metavar="FILE",
        help="The specification file to compile",
    )
    parser.add_argument(
        "-o",
        dest="destination",
        metavar="DESTINATION",
        help="The directory to compile to, defaults to same as specification file",
    )
    parser.add_argument(
        "-f",
        dest="overwrite",
        action="store_true",
        help="Overwrite existing files",
    )
    args = parser.parse_args()
    main(args.specification_file, args.destination, overwrite=args.overwrite)


if __name__ == "__main__":
    _run_as_script()
