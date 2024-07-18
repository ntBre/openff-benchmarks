# openff-benchmarks
Input files and scripts for benchmarking OpenFF force fields with yammbs

## Usage

### Generating datasets

TODO

### Running benchmarks

The provided `scripts/general.sh` is the easiest way to run a benchmark on HPC3.
The only required argument is the base name of the force field you want to
benchmark, for example:

``` shell
./scripts/general.sh example
```

This makes several assumptions for convenience:
1. The full path to the force field .offxml file is `forcefields/example.offxml`
2. The benchmark dataset (in [yammbs][yammbs] cache format) is in `datasets/cache/industry.json`
3. A mamba environment with the name `fb-196-qcnew` exists
4. You want 48 CPUs, 32 GB of RAM, and 84 hours of walltime

You can override all of these, except for the `forcefields` and `datasets/cache`
directories, by passing flags to the script. The table below lists each of the
available flags, along with descriptions and their default values.

| Flag | Description                                                 | Default        |
|------|-------------------------------------------------------------|----------------|
| -h   | Print usage information                                     | None           |
| -c   | Number of CPUs to request                                   | 48             |
| -t   | Walltime to request in hours                                | 84             |
| -m   | Memory to request in GB                                     | 32             |
| -s   | Cached dataset JSON file in `datasets/cache` to use         | `industry`     |
| -d   | Print generated Slurm input to stdout instead of submitting | false          |
| -e   | The conda environment to activate                           | `fb-196-qcnew` |

For example, the fully-specified default invocation of `general.sh` could also
be written:

``` shell
./scripts/general.sh example -c 48 -t 84 -m 32 -s industry -e fb-196-qcnew
```

Invoking this with the `-d` (dry run) flag produces this Slurm input:

``` shell
generating input for force field example, with 48 cpus, 32 gb, and 84 hours
#!/bin/bash
#SBATCH -J ib-example
#SBATCH -p standard
#SBATCH -t 84:00:00
#SBATCH --nodes=1
#SBATCH --cpus-per-task=48
#SBATCH --mem=32gb
#SBATCH --account dmobley_lab
#SBATCH --export ALL
#SBATCH --constraint=fastscratch
#SBATCH --output=bench.slurm.out

date
hostname
echo $SLURM_JOB_ID

source ~/.bashrc
mamba activate fb-196-qcnew

echo $OE_LICENSE

python -u main.py \
	   --forcefield forcefields/example.offxml \
	   --dataset datasets/cache/industry.json \
	   --sqlite-file example.sqlite \
	   --out-dir output/industry/example \
	   --procs 48 \
	   --invalidate-cache

date
```

[yammbs][yammbs] also requires that the OpenEye toolkits are available, so
you'll see that this prints the `$OE_LICENSE` environment variable. `main.py`
also asserts that `OpenEye` is available before running.

#### Output

This will produce CSV files corresponding to the DDE, RMSD, TFD, and
internal-coordinate RMSD (ICRMSD) metrics computed by [yammbs][yammbs], as well
as plots of the DDE, RMSD, and TFD values. The DDEs are plotted as a histogram,
while the TFDs and RMSDs are kernel density estimates (KDEs). The default output
directory is `output/$dataset/$ff`, where `$ff` and `$dataset` are taken from
the input provided to the script above.

<!-- References -->
[qcsubmit]: https://github.com/openforcefield/openff-qcsubmit
[yammbs]: https://github.com/openforcefield/yammbs
