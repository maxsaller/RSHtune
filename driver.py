"""
RSHtune - Driver

Driver script for the RSHtune package
DependenciesL os, argparse, RSHtune (on PYTHONPATH)
"""
import os
import RSHtune as tune
import argparse as argp


def dryRun(inputFile: str, dir: str = None,
           multiplicities: list = None) -> None:
    """Navigate to a directory and analyze tuning files already present."""
    if dir is not None:
        os.chdir(dir)
    _dirContents = os.listdir('.')
    _omega = { float(i.split("_")[0].split('w')[1])/1000 for i in _dirContents
                if i.split(".")[-1] == "out"
                and f"{i.split('_')[0]}_neutral.out" in _dirContents
                and f"{i.split('_')[0]}_anion.out" in _dirContents
                and f"{i.split('_')[0]}_cation.out" in _dirContents }
    print(f"#omega         J_OT\n{22*'#'}")
    for _o in sorted(list(_omega)):
        if multiplicities is not None:
            tuning_run = tune.QchemTuning(fname=inputFile,
                                          omega=_o,
                                          nthreads=nthreads,
                                          neutralSpMlt=multiplicities[0],
                                          anionSpMlt=multiplicities[1],
                                          cationSpMlt=multiplicities[2],
                                          loggerLevel="WARNING")
        else:
            tuning_run = tune.QchemTuning(fname=inputFile,
                                          omega=_o,
                                          nthreads=1,
                                          loggerLevel="WARNING")
        try:
            tuning_run.parseOutput()
            tuning_run.calculateOptimalTuning()
            print(f"{_o:.3f}      {tuning_run.data['tuning']['JOT']:.4E}")
        except ValueError:
            print(f"{_o:.3f}         ERROR")

def singlePoint(inputFile: str, nthreads: int,
                omega: float, dir:str = None,
                multiplicities: list = None) -> None:
    """Run a single tuning calculation for a given value of omega."""
    if dir is not None:
        os.chdir(dir)
    if multiplicities is not None:
        tuning_run = tune.QchemTuning(fname=inputFile,
                                      omega=omega,
                                      nthreads=nthreads,
                                      neutralSpMlt=multiplicities[0],
                                      anionSpMlt=multiplicities[1],
                                      cationSpMlt=multiplicities[2],
                                      loggerLevel="WARNING")
    else:
        tuning_run = tune.QchemTuning(fname=inputFile,
                                      omega=omega,
                                      nthreads=nthreads,
                                      loggerLevel="WARNING")
    print(f"#omega         J_OT\n{22*'#'}")
    tuning_run.runCalculations()
    try:
        tuning_run.parseOutput()
        tuning_run.calculateOptimalTuning()
        print(f"{omega:.3f}      {tuning_run.data['tuning']['JOT']:.4E}")
    except ValueError:
        print(f"{omega:.3f}         ERROR")

def rangeTuning(inputFile: str, nthreads: int,
                omega: list, dir:str = None,
                multiplicities: list = None) -> None:
    """Run a series of tuning calculation over a range of omega."""
    if dir is not None:
        os.chdir(dir)
    print(f"#omega         J_OT\n{22*'#'}")
    for _o in omega:
        if multiplicities is not None:
            tuning_run = tune.QchemTuning(fname=inputFile,
                                          omega=_o,
                                          nthreads=nthreads,
                                          neutralSpMlt=multiplicities[0],
                                          anionSpMlt=multiplicities[1],
                                          cationSpMlt=multiplicities[2],
                                          loggerLevel="WARNING")
        else:
            tuning_run = tune.QchemTuning(fname=inputFile,
                                          omega=_o,
                                          nthreads=nthreads,
                                          loggerLevel="WARNING")
        tuning_run.runCalculations()
        try:
            tuning_run.parseOutput()
            tuning_run.calculateOptimalTuning()
            print(f"""{_o:.3f}      {tuning_run.data['tuning']['JOT']:.4E}""")
        except ValueError:
            print(f"""{_o:.3f}         ERROR""")


if __name__ == "__main__":
    """Invoke a tuning instance using arguments from the command line."""

    parser = argp.ArgumentParser(description="""Driver for the RSHtune package
                                 for tuning RSH functionals using QChem.""")
    parser.add_argument("--inputFile", type=str, required=True, metavar="file",
                        help="NEUTRAL calculation input file. Respects --dir!")
    parser.add_argument("--numThreads", type=int, default=1,
                        metavar="int", help="Number of CPU threads for Qchem.")
    parser.add_argument("--omega", type=float, default=None,
                        metavar="float", help="Single value for omega.")
    parser.add_argument("--omegaRange", type=float, nargs="*",
                        metavar="float", help="Range of omega values.")
    parser.add_argument("--dir", type=str, default=None, metavar="dir",
                        help="Working directory if different to CWD.")
    parser.add_argument("--multiplicities", nargs=3, type=int, default=None,
                        metavar="int int int",
                        help="Spin-multiplicities: neutral anion cation.")
    parser.add_argument("--dry", action="store_true", default=False,
                        help="Analyze files present in directory.")

    args = parser.parse_args()

    if args.dry:
        print(f"# Printing completed tuning runs in directory <{args.dir}>")
        dryRun(args.inputFile, args.dir, args.multiplicities)

    if args.omega and args.omegaRange:
        sys.exit("Choose either --omega or --omegaRange")

    if args.omega:
        print(f"# Single point tuning claculation at omega={args.omega}.")
        singlePoint(args.inputFile, args.numThreads, args.omega, args.dir,
                    args.multiplicities)

    if args.omegaRange:
        print(f"# Tuning calculations over range omega={args.omegaRange}.")
        rangeTuning(args.inputFile, args.numThreads, args.omegaRange, args.dir,
                    args.multiplicities)        