"""
RSHtune  - Tuning.

Tune the range separation parameter of an RSH funtional.
Dependencies: os,sys, copy, logging
"""
import os
import sys
import copy
import logging
from .input import QchemInput
from .calculation import QchemCalculation


class QchemTuning():
    """Object for tuning the RSH range separation parameter."""

    def __init__(self, fname: str, omega: float, nthreads: int = 0,
                 neutralSpMlt: int = 0,
                 anionSpMlt: int = 0,
                 cationSpMlt: int = 0,
                 loggerLevel: str = "INFO") -> None:
        """Set up the tuning process."""
        self.initLogging(loggerLevel)

        # Check for input file
        if not os.path.isfile(fname):
            self.log.error(f"Cannot find neutral input file <{fname}>!")
            sys.exit()

        # Neutral Input
        self.neutralInput = QchemInput(fname=fname,
                                       loggerLevel=self.logLevel[0])
        self.neutralMolecule = self.neutralInput.input["molecule"][0][1]

        # Number of Threads
        self.numThreads = 1 if nthreads == 0 else nthreads

        self.setSpinMultiplicities(neutralSpMlt, anionSpMlt, cationSpMlt)
        self.createGeometries()
        self.createInputFiles(omega)

    def initLogging(self, level: str) -> None:
        """Initialize logging."""
        _log_levels = {"CRITICAL": 50, "ERROR": 40, "WARNING": 30, "INFO": 20,
                       "DEBUG": 10, "NOTSET": 0}
        self.logLevel = (level, _log_levels[level])
        self.log = logging.getLogger("QchemTuning")
        self.log.setLevel(self.logLevel[1])
        logStreamHandler = logging.StreamHandler()
        logStreamHandler.setLevel(self.logLevel[1])
        logFormatter = logging.Formatter("%(asctime)s " +
                                         "%(name)s:%(levelname)s " +
                                         "%(message)s")
        logStreamHandler.setFormatter(logFormatter)
        if (self.log.hasHandlers()):
            self.log.handlers.clear()
        self.log.addHandler(logStreamHandler)

    def setSpinMultiplicities(self, neutral, anion, cation) -> None:
        """Determine spin multiplicities."""
        self.neutralSpinMulti = neutral if neutral != 0 else 1
        self.anionSpinMulti = anion if anion != 0 else 2
        self.cationSpinMulti = cation if cation != 0 else 2

        self.log.info("Geometry and Spin Multiplicities:")
        self.log.info(f"  - Neutral geometry:     <{self.neutralMolecule}>")
        self.log.info(f"  - Neutral Charge Spin:   0 {self.neutralSpinMulti}")
        self.log.info(f"  - Anion Charge Spin:    -1 {self.anionSpinMulti}")
        self.log.info(f"  - Cation Charge Spin:   +1 {self.cationSpinMulti}")

    def createGeometries(self) -> None:
        """Create molecule files."""
        with open(self.neutralMolecule, "r") as f:
            _neutralGeometry = f.readlines()
        self.anionMolecule = f"{self.neutralMolecule.split('.')[0]}_anion.mol"
        self.cationMolecule = f"{self.neutralMolecule.split('.')[0]}_cation.mol"
        with open(self.anionMolecule, "w") as _fanion:
            _fanion.write(_neutralGeometry[0])
            _fanion.write(f"{-1} {self.anionSpinMulti}\n")
            for line in _neutralGeometry[2:]:
                _fanion.write(line)
        self.log.info(f"Written anion geometry to <{self.anionMolecule}>.")
        with open(self.cationMolecule, "w") as fcation:
            fcation.write(_neutralGeometry[0])
            fcation.write(f"{1} {self.cationSpinMulti}\n")
            for line in _neutralGeometry[2:]:
                fcation.write(line)
        self.log.info(f"Written cation geometry to <{self.cationMolecule}>.")

    def createInputFiles(self, omega: float) -> None:
        """Create input files."""
        self.omega = omega
        self.neutralFile = f"w{int(self.omega*1000):3}_neutral.in"
        with open(self.neutralFile, "w") as fneutral:
            for j, item in enumerate(self.neutralInput.input["rem"]):
                if item[0] == "omega":
                    self.neutralInput.input["rem"][j][1] = int(self.omega*1000)
            self.neutralInput.input["molecule"][0][1] = self.neutralMolecule
            fneutral.write(str(self.neutralInput))
        self.log.info(f"Written working neutral input to <{self.neutralFile}>")

        self.anionFile = f"w{int(self.omega*1000):3}_anion.in"
        with open(self.anionFile, "w") as _fanion:
            _anionInput = copy.deepcopy(self.neutralInput)
            for j, item in enumerate(_anionInput.input["rem"]):
                if item[0] == "omega":
                    _anionInput.input["rem"][j][1] = int(self.omega*1000)
                _anionInput.input["molecule"][0][1] = self.anionMolecule
            _fanion.write(str(_anionInput))
        self.log.info(f"Written working anion input to <{self.anionFile}>")

        self.cationFile = f"w{int(self.omega*1000):3}_cation.in"
        with open(self.cationFile, "w") as _fcation:
            _cationInput = copy.deepcopy(self.neutralInput)
            for j, item in enumerate(_cationInput.input["rem"]):
                if item[0] == "omega":
                    _cationInput.input["rem"][j][1] = int(self.omega*1000)
            _cationInput.input["molecule"][0][1] = self.cationMolecule
            _fcation.write(str(_cationInput))
        self.log.info(f"Written working cation input to <{self.cationFile}>")

    def runCalculations(self) -> None:
        """Run three Qchem calculations for anion, cation and neutral."""
        _calc = QchemCalculation(fname=self.neutralFile,
                                 nthreads=self.numThreads,
                                 loggerLevel=self.logLevel[0])
        _calc.submit()

        _calc = QchemCalculation(fname=self.anionFile,
                                 nthreads=self.numThreads,
                                 loggerLevel=self.logLevel[0])
        _calc.submit()

        _calc = QchemCalculation(fname=self.cationFile,
                                 nthreads=self.numThreads,
                                 loggerLevel=self.logLevel[0])
        _calc.submit()

    def parseOutput(self) -> None:
        """Read output files and store relevant data."""
        self.data = {"neutral": {}, "anion": {}, "cation": {}}

        with open(f"{self.neutralFile.split('.')[0]}.out", "r") as nout:
            _homo = []
            _lumo = []
            _lines = nout.readlines()
            for j, line in enumerate(_lines):
                if "Convergence criterion met" in line:
                    self.data["neutral"]["SCFenergy"] = float(line.split()[1])
                if "-- Virtual --" in line:
                    _homo.append(float(_lines[j-1].split()[-1]))
                    _lumo.append(float(_lines[j+1].split()[0]))
            self.data["neutral"]["HOMO"] = max(_homo)
            self.data["neutral"]["LUMO"] = min(_lumo)

        with open(f"{self.anionFile.split('.')[0]}.out", "r") as aout:
            _homo = []
            _lumo = []
            _lines = aout.readlines()
            for j, line in enumerate(_lines):
                if "Convergence criterion met" in line:
                    self.data["anion"]["SCFenergy"] = float(line.split()[1])
                if "-- Virtual --" in line:
                    _homo.append(float(_lines[j-1].split()[-1]))
                    _lumo.append(float(_lines[j+1].split()[0]))
            self.data["anion"]["HOMO"] = max(_homo)
            self.data["anion"]["LUMO"] = min(_lumo)

        with open(f"{self.cationFile.split('.')[0]}.out", "r") as cout:
            _homo = []
            _lumo = []
            _lines = cout.readlines()
            for j, line in enumerate(_lines):
                if "Convergence criterion met" in line:
                    self.data["cation"]["SCFenergy"] = float(line.split()[1])
                if "-- Virtual --" in line:
                    _homo.append(float(_lines[j-1].split()[-1]))
                    _lumo.append(float(_lines[j+1].split()[0]))
            self.data["cation"]["HOMO"] = max(_homo)
            self.data["cation"]["LUMO"] = min(_lumo)

    def calculateOptimalTuning(self) -> None:
        """Calculate optimal tuning error from neutral, anion and cation."""
        self.data["tuning"] = {}
        self.data["tuning"]["IP"] = (self.data["cation"]["SCFenergy"] -
                                     self.data["neutral"]["SCFenergy"])
        self.data["tuning"]["EA"] = (self.data["neutral"]["SCFenergy"] -
                                     self.data["anion"]["SCFenergy"])
        self.data["tuning"]["JOT"] = ((self.data["tuning"]["IP"] +
                                       self.data["neutral"]["HOMO"])**2 +
                                      (self.data["tuning"]["EA"] +
                                       self.data["neutral"]["LUMO"])**2)
