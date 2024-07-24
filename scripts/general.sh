set -e

ncpus=48
hours=84
mem=32
env=openff-benchmarks
dataset=industry

cmd=sbatch

usage="Usage: $0 -f FORCEFIELD [-c CPUS] [-t CPU_HOURS] [-m GB_MEMORY] [-h]"

case $# in
	0) echo 'error: no arguments provided'
	   echo $usage
	   exit 1;;
esac

while getopts "dhc:t:m:s:e:f:" arg; do
	case $arg in
		h) echo $usage
		   exit 0;;
		c) ncpus=$OPTARG ;;
		t) hours=$OPTARG ;;
		m) mem=$OPTARG ;;
		s) dataset=$OPTARG ;;
		d) cmd=cat ;; # dry run
		e) env=$OPTARG ;; # conda env
		f) ff=$OPTARG ;;
	esac
done

if [[ -z "$ff" ]]
then
	echo 'error: no force field provided'
	echo $usage
	exit 1
fi

# allow providing just the base of the ff filename if it's present in the
# forcefields directory; otherwise, arrange to pass this exact path to the
# toolkit and extract the base of the filename for the output dir and name of
# the sqlite file
if [[ -f forcefields/$ff.offxml ]]
then
	ffpath=forcefields/$ff.offxml
else
	ffpath=$ff
	ffbase=$(basename $ff)
	ff=${ffbase%.offxml}
fi

# like the force field, allow providing just the base name of the dataset in the
# datasets/cache dir. otherwise, assume the full path of the file was provided
if [[ -f $dataset ]]
then
	dspath=$dataset
	dsbase=$(basename $dataset)
	dataset=${dsbase%.json}
else
	dspath=datasets/cache/$dataset.json
fi

if [[ ! -f $dspath ]]
then
	echo "error: dataset file not found at $dspath"
	exit 1
fi

echo generating input for
echo force field = $ff
echo dataset = $dataset
echo ncpus = $ncpus
echo mem = $mem gb
echo walltime = $hours hours

$cmd <<INP
#!/bin/bash
#SBATCH -J bench-$ff
#SBATCH -p standard
#SBATCH -t $hours:00:00
#SBATCH --nodes=1
#SBATCH --cpus-per-task=$ncpus
#SBATCH --mem=${mem}gb
#SBATCH --account dmobley_lab
#SBATCH --export ALL
#SBATCH --constraint=fastscratch
#SBATCH --output=logs/bench.$$.out

date
hostname
echo \$SLURM_JOB_ID

source ~/.bashrc
mamba activate $env

echo \$OE_LICENSE

python -u main.py \
       --forcefield $ffpath \
       --dataset $dspath \
       --sqlite-file $ff.sqlite \
       --out-dir output/$dataset/$ff \
       --procs $ncpus \
       --invalidate-cache

date
INP
