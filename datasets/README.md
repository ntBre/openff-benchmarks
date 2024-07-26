This directory contains datasets in the JSON-serialized
`OptimizationResultCollection` format from [qcsubmit][qcsubmit], as well as
scripts for retrieving and post-processing them.

| Type    | File                  | Description                                                                    |
|---------|-----------------------|--------------------------------------------------------------------------------|
| Script  | download.py           | Download a named dataset from [qcarchive][qcarchive]                           |
|         | filter.py             | Filter out problematic records from a dataset                                  |
|         | filter.sh             | Slurm script for filtering industry.json                                       |
|         | submit.sh             | Generalized Slurm script for running Make commands                             |
|         | Makefile              | Makefile showing how each file is produced                                     |
| Dataset | industry.json         | OpenFF Industry Benchmark Season 1 v1.1                                        |
|         | tm-supp.json          | OpenFF Torsion Multiplicity Optimization Benchmarking Coverage Supplement v1.0 |
|         | filtered-tm-supp.json | Filtered version of tm-supp.json                                               |

<!-- Refs -->
[qcsubmit]: https://github.com/openforcefield/openff-qcsubmit
[qcarchive]: https://qcarchive.molssi.org/
