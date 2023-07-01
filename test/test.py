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
    inp = tune.QchemInput(file="example.in")
    print(inp.getSection("xc_functional"))
    print(inp.XCfunc)