# RSHtune


## Installation
In order to be able to use this library, add the following to your `.bashrc` file:
```bash
export PYTHONPATH=$PYTHONPATH:<path/to/RSHtune>
```
The Makefile included with the package will both do this and source the modified `.bashrc` file for the current session when invoked using
```bash
make install
```

## Basic Usage
The `driver.py` file provides a interface for the three most common taskt in tuning an RSH functional:

- Run a single tuning calculation (neutral, anion, cation) at a given range separation parameter value, omega, and calculate the optimal tuning error.
- Run a series of tuning calculations over a range of values for omega and tabulate the optimal tuning error for each.
- Tabulate the optimal tuning error values based on prior calculations, already present in a given directory.

## Command Line Arguments

| Argument        | Required | Function   |
|:----------------|:--------:|:-----------|
| `--inputFile`     | yes      | Input file for the neutral species. Note: respects `--dir`. |
| `--dir`          | no       | Directory in which to carry out tuning, store and locate files. |
| `--dry`          | no       | Tabulate preexisting tuning results only, no calculations. |
| `--omega`        | no       | Carry out a single tuning calculation at omega. |
| `--omegaRange`    | no       | Tune over a range of values for omega. Conflicts with `--omega`!|
| `--numThreads`    | no       | Number of threads to run QChem with. Default: 1 |
| `--multiplicities` | no       | Specify spin-multiplicities: neutral anion cation |


## License
**Copyright 2003 Maximilian Saller**

Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the “Software”), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED “AS IS”, WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
