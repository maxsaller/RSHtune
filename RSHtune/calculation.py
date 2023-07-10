"""
RSHtune  - Calculation.

Setup adn running of calculations.
Dependencies: time, logging, subprocess
"""
import time
import logging
import subprocess as sb
from .input import QchemInput


class QchemCalculation():
    """Object for setting up and running a Qchem calculation."""\

    def __init__(self, fname: str, jname: str = "", nthreads: int = 0,
                 loggerLevel: str = "INFO") -> None:
        """Initialize input."""
        self.initLogging(loggerLevel)

        # Input File
        self.log.info(f"Creating QChem calculation from <{fname}> input file.")
        self.input = QchemInput(fname, loggerLevel=self.logLevel[0])

        # Molecular Geometry
        self.molecule = self.input.input["molecule"][0][1]
        self.log.info(f"Using molecular geometry in <{self.molecule}>.")

        # Jobname
        self.jobName = fname.split(".")[0] if jname is "" else jname
        self.log.info(f"This Qchem job will use jobname '{self.jobName}'.")

        # Number of Threads
        self.numThreads = 1 if nthreads is 0 else nthreads

    def initLogging(self, level: str) -> None:
        """Initialize logging."""
        _log_levels = {"CRITICAL": 50, "ERROR": 40, "WARNING": 30, "INFO": 20,
                       "DEBUG": 10, "NOTSET": 0}
        self.logLevel = (level, _log_levels[level])
        self.log = logging.getLogger("QchemCalculation")
        self.log.setLevel(logging.INFO)
        logStreamHandler = logging.StreamHandler()
        logStreamHandler.setLevel(self.logLevel[1])
        logFormatter = logging.Formatter("%(asctime)s " +
                                         "%(name)s:%(levelname)s " +
                                         "%(message)s")
        logStreamHandler.setFormatter(logFormatter)
        if (self.log.hasHandlers()):
            self.log.handlers.clear()
        self.log.addHandler(logStreamHandler)

    def submit(self) -> None:
        """Run a single Qchem caluclation."""
        self.log.info(f"Running Qchem with {self.numThreads} threads.")
        _start = time.time()
        self.calc = sb.run(["qchem",
                            "-save",
                            "-nt",
                            f"{self.numThreads}",
                            f"{self.jobName}.in",
                            f"{self.jobName}.out",
                            f"{self.jobName}"], capture_output=True)
        self.log.info(f"Completed Qchem run in {time.time() - _start:.1f}s.")
        self.log.info(f"Output written to <{self.jobName}.out>.")
