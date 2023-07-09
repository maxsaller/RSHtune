"""
RStune Testing.

Simple testing and demonstration of the RSHtune package's capabilities.
"""
if __name__ == "__main__":
    """Executing this file directly implements simple testing."""
    import os
    import sys
    sys.path.append(os.path.abspath("../"))
    import RSHtune as tune

    # Input Testing
    # inp = tune.QchemInput(fname="example.in")
    # print(inp)

    # Calculation Testing
    # calc = tune.QchemCalculation(fname="RSH.in", jname="RSH", nthreads=24)
    # calc.submit()

    # Tuning Testing
    tune = tune.QchemTuning(fname="RSH.in", omega=0.2, nthreads=24)
    