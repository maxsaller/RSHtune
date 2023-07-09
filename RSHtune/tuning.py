"""
RSHtune  - Tuning.

Tune the range separation parameter of an RSH funtional.
Dependencies: os,sys, time, copy, logging, argparse, subprocess
"""
import os
import sys
import time
import copy
import logging
import argparse as ag
import subprocess as sb
from .input import QchemInput
from .calculation import QchemCalculation


class QchemTuning():
    """Object for tuning the RSH range separation parameter"""

    def __init__(self, fname: str, omega: float, nthreads: int = None,
                 neutralSpMlt: int = None,
                 anionSpMlt: int = None,
                 cationSpMlt: int = None) -> None:
        """Set up the tuning process."""
        self.initLogging()

        # Check for input file
        if not os.path.isfile(fname):
            self.log.error(f"Cannot find neutral input file <{fname}>!")
            sys.exit()

        # Neutral Input
        self.neutralInput = QchemInput(fname=fname)
        self.neutralMolecule = self.neutralInput.input["molecule"][0][1]

        # Spin Multiplities
        self.spinMulti(neutralSpMlt, anionSpMlt, cationSpMlt)
        
        # Generate molecule files
        self.createGeometries()

        # Generate input files
        self.createInputFiles(omega)

        # Run Qchem Calculations
        self.runCalculations(nthreads)


    def initLogging(self) -> None:
        """Initialize logging."""
        self.log = logging.getLogger("QchemTuning")
        self.log.setLevel(logging.INFO)
        logStreamHandler = logging.StreamHandler()
        logStreamHandler.setLevel(logging.INFO)
        logFormatter = logging.Formatter("%(asctime)s " +
                                       "%(name)s:%(levelname)s " +
                                       "%(message)s")
        logStreamHandler.setFormatter(logFormatter)
        if (self.log.hasHandlers()):
            self.log.handlers.clear()
        self.log.addHandler(logStreamHandler)


    def spinMulti(self, neutral, anion, cation) -> None:
        """Determine spin multiplicities."""
        self.neutralSpinMulti = neutral if neutral is not None else 1
        self.anionSpinMulti = anion if anion is not None else 2
        self.cationSpinMulti = cation if cation is not None else 2

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
        with open(self.anionMolecule, "w") as fanion:
            fanion.write(_neutralGeometry[0])
            fanion.write(f"{-1} {self.anionSpinMulti}\n")
            for line in _neutralGeometry[2:]:
                fanion.write(line)
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
        with open(self.anionFile, "w") as fanion:
            _anionInput = copy.deepcopy(self.neutralInput)
            for j, item in enumerate(_anionInput.input["rem"]):
                if item[0] == "omega":
                    _anionInput.input["rem"][j][1] = int(self.omega*1000)
                _anionInput.input["molecule"][0][1] = self.anionMolecule
            fanion.write(str(_anionInput))
        self.log.info(f"Written working anion input to <{self.anionFile}>")
        
        self.cationFile = f"w{int(self.omega*1000):3}_cation.in"
        with open(self.cationFile, "w") as fanion:
            _cationInput = copy.deepcopy(self.neutralInput)
            for j, item in enumerate(_anionInput.input["rem"]):
                if item[0] == "omega":
                    _anionInput.input["rem"][j][1] = int(self.omega*1000)
            _anionInput.input["molecule"][0][1] = self.cationMolecule
            fanion.write(str(_anionInput))
        self.log.info(f"Written working cation input to <{self.cationFile}>")

    def runCalculations(self, nthreads:int) -> None:
        """Run three Qchem calculations for anion, cation and neutral."""
        # Number of Threads
        self.numThreads = 1 if nthreads is None else nthreads

        _calc = QchemCalculation(fname=self.neutralFile,
                                    nthreads=self.numThreads)
        _calc.submit()

        _calc = QchemCalculation(fname=self.anionFile,
                                    nthreads=self.numThreads)
        _calc.submit()

        _calc = QchemCalculation(fname=self.cationFile,
                                    nthreads=self.numThreads)
        _calc.submit()
        