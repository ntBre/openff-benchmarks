set -e

ff=$1
shift
ncpus=48
hours=84
mem=32
env=openff-benchmarks
dataset=industry

cmd=sbatch

while getopts "dhc:t:m:s:e:" arg; do
	case $arg in
		h) echo 'usage: [-c CPUS] [-t CPU_HOURS] [-m GB_MEMORY] [-h]' ;;
		c) ncpus=$OPTARG ;;
		t) hours=$OPTARG ;;
		m) mem=$OPTARG ;;
		s) dataset=$OPTARG ;;
		d) cmd=cat ;; # dry run
		e) env=$OPTARG ;; # conda env
	esac
done

echo generating input for force field $ff, with $ncpus cpus, $mem gb, and $hours hours

$cmd <<INP
#!/bin/bash
#SBATCH -J ib-$ff
#SBATCH -p standard
#SBATCH -t $hours:00:00
#SBATCH --nodes=1
#SBATCH --cpus-per-task=$ncpus
#SBATCH --mem=${mem}gb
#SBATCH --account dmobley_lab
#SBATCH --export ALL
#SBATCH --constraint=fastscratch
#SBATCH --output=bench.slurm.out

date
hostname
echo \$SLURM_JOB_ID

source ~/.bashrc
mamba activate $env

echo \$OE_LICENSE

python -u main.py \
       --forcefield forcefields/$ff.offxml \
       --dataset datasets/cache/$dataset.json \
       --sqlite-file $ff.sqlite \
       --out-dir output/$dataset/$ff \
       --procs $ncpus \
       --invalidate-cache

date
INP
