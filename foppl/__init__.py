#
# This file is part of PyFOPPL, an implementation of a First Order Probabilistic Programming Language in Python.
#
# License: MIT (see LICENSE.txt)
##
# 19. Dec 2017, Tobias Kohn
# 18. Jan 2018, Tobias Kohn
#
class Options(object):
    """
    This class provides flags and general options to control the compilation process.

    `eager_conditionals`:
        Controls whether conditional statements (`if`-expressions) should be evaluated eagerly or lazily.
        _At the moment, only eager evaluation is supported._

    `uniform_conditionals`:
        If this flag is set to `True`, the compiler will transform all comparisons (except for equality) to be
        in the form `X >= 0`. For instance, `x < 5` will thus be transformed to `not (x-5 >= 0)`.

    `conditional_suffix`:
        A string suffix that is appended to conditional variables.
    """

    eager_conditionals = True

    uniform_conditionals = True

    conditional_suffix = '.data[0]'
