"""
RSHtune - Driver

Driver script for the RSHtune package
DependenciesL os, argparse, RSHtune (on PYTHONPATH)
"""
import os
import RSHtune as tune
import argparse as argp

if __name__ == "__main__":
    """Invoke a tuning instance using arguments from the command line."""

    parser = argp.ArgumentParser(description="""Driver for the RSHtune package
                                 for tuning RSH functionals using QChem.""")
    parser.add_argument("--inputFile", type=str, required=True, metavar="file",
                        help="Input file foe the NEUTRAL calculation.")
    parser.add_argument("--numThreads", type=int, default=1,
                        metavar="int", help="Number of CPU threads for Qchem.")
    parser.add_argument("--omegaStart", type=float, default=0.2,
                        metavar="float", help="Starting value for omega.")
    parser.add_argument("--omegaRange", type=float, nargs="*",
                        metavar="float", help="Range of omega values.")
    args = parser.parse_args()
