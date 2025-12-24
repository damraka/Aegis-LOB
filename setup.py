from setuptools import setup
import pybind11
from pybind11.setup_helpers import Pybind11Extension, build_ext

# --- Build Configuration for C++ Extension ---
# This section defines the compilation of the C++ source code into a Python-ready module.
# It links the pybind11 headers with the core Aegis-LOB include files.
ext_modules = [
    Pybind11Extension(
        "aegis_lob",
        ["wrappers/python_bindings.cpp"],
        include_dirs=[pybind11.get_include(), "core/include"],
        language='c++',
    ),
]

setup(
    name="aegis_lob",
    version="1.0.0",
    description="A high-performance C++ Order Book for the Aegis-LOB Quant Framework",
    ext_modules=ext_modules,
    cmdclass={"build_ext": build_ext},
    zip_safe=False,
)