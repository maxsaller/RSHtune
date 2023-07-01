"""
RSHtune  - Calculation - Input.

Reasing and writing of QChem input files.
Dependencies: sys, logging
"""
import sys
import logging


class QchemInput():
    """Object for reading and modifying input for Q-Chem."""

    def __init__(self, file: str) -> None:
        """Initialize input."""
        self.initLogging()

        self.file = file
        try:
            with open(self.file, "r") as f:
                self.log.info(f"Reading input from <{self.file}>")
                self.parseInput(f.readlines())
        except FileNotFoundError:
            self.log.error(f"File <{self.file}> could not be found.")
            self.log.error(f"Exiting!")
            sys.exit()

        # User definition of XC functional handling
        if "xc_functional" in self.input.keys():
            self.parseXCfunctional()

    def initLogging(self) -> None:
        """Initialize logging."""
        self.log = logging.getLogger("QchemInput")
        self.log.setLevel(logging.INFO)
        logStreamHandler = logging.StreamHandler()
        logStreamHandler.setLevel(logging.INFO)
        logFormatter = logging.Formatter("%(asctime)s " +
                                         "%(name)s:%(levelname)s " +
                                         "%(message)s")
        logStreamHandler.setFormatter(logFormatter)
        self.log.addHandler(logStreamHandler)

    def parseInput(self, content: list[str]) -> None:
        """Parse contents of a provided input file."""
        key = None
        self.input = {}
        for line in content:
            if line != "\n":
                ln = self.lineParse(line)
                if ln[0][0] == "$" and ln[0][1:] != "end":
                    key = ln[0][1:].lower()
                    self.input[key] = {}
                if ln[0][0] != "$":
                    try:
                        if ln[0].upper() not in self.input[key].keys():
                            self.input[key][ln[0].upper()] = ln[1:]
                        else:
                            if ln[1:] != self.input[key][ln[0]]:
                                self.input[key][ln[0].upper()].append(ln[1])
                                self.input[key][ln[0].upper()].append(ln[2])
                            else:
                                self.log.warning(f"Possible duplicate line " +
                                                 f"in input file:\n" +
                                                 f"{line.strip()}")
                    except KeyError:
                        self.log.error("Check input file for $section" +
                                       "inconsistencies!")
        self.log.info(f"Read {len(content)} lines, " +
                      f"finding {len(self.input.keys())} input sections ")

    def lineParse(self, line: str) -> list[str]:
        """Extract line arguments and unify styling."""
        ln = line.split("#")[0]
        ln = ln.strip().split()

        for j, item in enumerate(ln):
            if item == "=":
                ln.pop(j)
            if item[0] == "=" and len(item) > 1:
                ln[j] = ln[j][1:]
            if item[-1] == "=" and len(item) > 1:
                ln[j] = ln[j][:-1]
        return ln

    def valParse(self, val: str) -> str:
        """Baeutify values."""
        if val.lower() in ["true", "false"]:
            return val.upper()
        return f"{val:10s}"

    def getSection(self, sec: str) -> str:
        """Return the contents of a $ section in the input as a string."""
        try:
            return self.input[sec.lower()].__repr__()
        except KeyError:
            self.log.error(f"Input contains no ${sec} section!")
            sys.exit()

    def parseXCfunctional(self) -> None:
        """Create a dict to handle user-sepcification of the XC fuctional."""
        XC = self.input["xc_functional"]
        self.XCfunc = {}
        for k in XC.keys():
            if len(XC[k]) == 2:
                self.XCfunc[k] = {XC[k][0]: float(XC[k][1])}
            else:
                self.XCfunc[k] = {XC[k][i]: float(XC[k][i+1]) for i in range(0, len(XC[k]), 2)}

    def __repr__(self) -> str:
        """Provide string representation of object."""
        repr = ""
        for sec in self.input.keys():
            repr += f"${sec}\n"
            for key in self.input[sec].keys():
                repr += f"  {key:20s}"
                for val in self.input[sec][key]:
                    if type(val) == list:
                        repr += f"\n  {key:20s}"
                        for val2 in val:
                            repr += f"{self.valParse(val2)} "
                    else:
                        repr += f"{self.valParse(val)} "
                repr += "\n"
            repr += f"$end\n\n"
        return repr
