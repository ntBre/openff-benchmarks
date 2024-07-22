This directory contains datasets in the JSON-serialized
`OptimizationResultCollection` format from [qcsubmit][qcsubmit], as well as
scripts for retrieving and post-processing them.

| Type    | File          | Description                                          |
|---------|---------------|------------------------------------------------------|
| Script  | download.py   | Download a named dataset from [qcarchive][qcarchive] |
|         | filter.py     | Filter out problematic records from a dataset        |
|         | filter.sh     | Slurm script for filtering industry.json             |
|         | Makefile      | Makefile showing how each file is produced           |
| Dataset | industry.json | OpenFF Industry Benchmark Season 1 v1.1              |

<!-- Refs -->
[qcsubmit]: https://github.com/openforcefield/openff-qcsubmit
[qcarchive]: https://qcarchive.molssi.org/
