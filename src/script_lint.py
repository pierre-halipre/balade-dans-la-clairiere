"""Copyright 2023 Pierre Halipré

This file is part of Balade dans la clairière.

Balade dans la clairière is free software: you can redistribute it and/or
modify it under the terms of the GNU General Public License as published by the
Free Software Foundation, either version 3 of the License, or (at your option)
any later version.

Balade dans la clairière is distributed in the hope that it will be useful, but
WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or
FITNESS FOR A PARTICULAR PURPOSE. See the GNU General Public License for more
details.

You should have received a copy of the GNU General Public License along with
Balade dans la clairière. If not, see <https://www.gnu.org/licenses/>.
"""

import io
import os
import pylint.lint
import pylint.reporters.text
import pycodestyle

REPORTS = "--reports=false"
SCORE = "--score=false"
RECURSIVE = "--recursive=true"
EXTENSION = "--unsafe-load-any-extension=true"
DISABLE = (
    "--disable=" +
    "missing-module-docstring" +
    ", " +
    "missing-class-docstring" +
    ", " +
    "missing-function-docstring"
)

for file in os.listdir("."):
    if file.endswith(".py"):
        print(format(file, "_<79"))
        pylint_output = io.StringIO()
        reporter = pylint.reporters.text.TextReporter(pylint_output)
        argv = (REPORTS, SCORE, RECURSIVE, EXTENSION, DISABLE, file)
        pylint.lint.Run(argv, reporter=reporter, exit=False)

        if pylint_output.getvalue() != "":
            print(pylint_output.getvalue())
        else:
            pass

        checker = pycodestyle.Checker(file, show_source=True)
        checker.check_all()
    else:
        pass
