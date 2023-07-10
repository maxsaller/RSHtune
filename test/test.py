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
    inp = tune.QchemInput(fname="RSH.in")
    print(inp)
    print(f"\n\n\n{80*'='}\n\n\n")

    # Calculation Testing
    calc = tune.QchemCalculation(fname="RSH.in", jname="RSH", nthreads=24)
    calc.submit()
    print(f"\n\n\n{80*'='}\n\n\n")

    # Tuning Testing
    tuning_run = tune.QchemTuning(fname="RSH.in", omega=0.2, nthreads=24)
    tuning_run.runCalculations()
    tuning_run.parseOutput()
    tuning_run.calculateOptimalTuning()
    for key in tuning_run.data.keys():
        tuning_run.log.info(f"{key}: {tuning_run.data[key]}")
    print(f"\n\n\n{80*'='}\n\n\n")

    # Tuning Run Testing
    omega = [float(i)/1000 for i in range(333, 337)]
    print(f"# omega         J_OT\n{22*'#'}")
    for o in omega:
        tuning_run = tune.QchemTuning(fname="RSH.in",
                                      omega=o,
                                      nthreads=24,
                                      loggerLevel="WARNING")
        tuning_run.runCalculations()
        try:
            tuning_run.parseOutput()
            tuning_run.calculateOptimalTuning()
            print(f"""{o:.3f}      {tuning_run.data['tuning']['JOT']:.4E}""")
        except ValueError:
            print(f"""{o:.3f}         ERROR""")
