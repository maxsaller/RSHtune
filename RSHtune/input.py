"""
RSHtune  - Calculation - Input.

Reasing and writing of QChem input files.
Dependencies: sys, logging
"""
import sys
import logging


class QchemInput():
    """Object for reading and modifying input for Q-Chem."""

    def __init__(self, fname: str, loggerLevel: str = "INFO") -> None:
        """Initialize input."""
        self.initLogging(loggerLevel)

        self.inputFile = fname
        try:
            with open(self.inputFile, "r") as f:
                self.log.info(f"Reading input from <{self.inputFile}>.")
                self.parseInput(f.readlines())
        except FileNotFoundError:
            self.log.error(f"File <{self.inputFile}> could not be found.")
            self.log.error(f"Exiting!")
            sys.exit()

    def initLogging(self, level: str) -> None:
        """Initialize logging."""
        _log_levels = {"CRITICAL": 50, "ERROR": 40, "WARNING": 30, "INFO": 20,
                       "DEBUG": 10, "NOTSET": 0}
        self.logLevel = (level, _log_levels[level])
        self.log = logging.getLogger("QchemInput")
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

    def parseInput(self, content: list) -> None:
        """Parse contents of a provided input file."""
        key = None
        self.input = {}
        for line in content:
            if line != "\n":
                ln = self.lineParse(line)
                if ln[0][0] == "$" and ln[0][1:] != "end":
                    key = ln[0][1:].lower()
                    self.input[key] = []
                elif ln[0][0] != "$":
                    self.input[key].append(ln)
        self.log.info(f"Read {len(content)} lines, " +
                      f"finding {len(self.input.keys())} input sections.")

    def lineParse(self, line: str) -> list:
        """Extract line arguments and unify styling."""
        ln = line.split("#")[0].split("!")[0]
        ln = ln.strip().split()

        for j, item in enumerate(ln):
            if item == "=":
                ln.pop(j)
            elif item[0] == "=" and len(item) > 1:
                ln[j] = ln[j][1:]
            elif item[-1] == "=" and len(item) > 1:
                ln[j] = ln[j][:-1]
            elif "=" in item:
                ln = [*ln[j].split("="), *ln[j+1:]]
        return ln

    def valParse(self, val: str) -> str:
        """Baeutify values."""
        if type(val) == str and val.lower() in ["true", "false"]:
            return val.upper()
        return val

    def keyParse(self, key: str) -> str:
        """Baeutify keys."""
        return f"{key.lower():<30s}"

    def __repr__(self) -> str:
        """Provide string representation of object."""
        repr = ""
        for sec in self.input.keys():
            repr += f"${sec}\n"
            for line in self.input[sec]:
                if len(line) == 2:
                    repr += f"{self.keyParse(line[0])} "
                    repr += f"{self.valParse(line[1])}\n"
                else:
                    for item in line:
                        repr += f"{item:<10s}"
                    repr += "\n"
            repr += f"$end\n\n"
        return repr
