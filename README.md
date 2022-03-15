# SAT Generator

## Prerequisites

```bash
pip3 install python-sat
```

On MacOS M1, perhaps, you will need to invoke:

```bash
brew install hdf5
brew install netcdf
```

and then launch (replace the hdf5 version with yours):

```bash
HDF5_DIR=/opt/homebrew/Cellar/hdf5/1.13.0 pip3 install pysat
pip3 install python-sat
```

## Integer Factorization to SAT

The `PrimesProductToSAT.py` script demonstrates how to generate a SAT instance from the known product of two primes. Since our generator uses the Karatsuba multiplication algorithm recursively, the number of bits of each prime (and, hence, the product) must be a power of 2.

