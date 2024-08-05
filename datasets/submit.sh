#!/bin/bash

# Usage:
# ./submit.sh COMMAND...
#
# All of the arguments to this script are passed into the body of the sbatch
# invocation below. This is intended as a more general replacement for
# filter.sh, which would be equivalent to:
#
# ./submit.sh make filtered-industry.json
#
# Slurm output is saved to logs/$date.$pid.out

usage="Usage: $0 CMDS... [-h] [-t CPU_HOURS] [-m GB_MEMORY]"

case $# in
	0) echo 'error: no arguments provided'
	   echo $usage
	   exit 1;;
esac

# default options
hours=72
mem=32

while getopts "ht:m:" arg
do
	case $arg in
		h) echo $usage
		   exit 0;;
		t) hours=$OPTARG;;
		m) mem=$OPTARG;;
	esac
done

day=$(date +%Y-%m-%d)
pid=$$

logfile=logs/$day.$pid.out

echo saving slurm output to
echo $logfile
echo requesting $hours CPU hours and $mem GB of RAM

sbatch <<INP
#!/bin/bash
#SBATCH -J filter-dataset
#SBATCH -p standard
#SBATCH -t ${hours}:00:00
#SBATCH --nodes=1
#SBATCH --cpus-per-task=1
#SBATCH --mem=${mem}gb
#SBATCH --account dmobley_lab
#SBATCH --export ALL
#SBATCH --constraint=fastscratch
#SBATCH --output=${logfile}

date
hostname
echo \$SLURM_JOB_ID

source ~/.bashrc
mamba activate openff-benchmarks

echo \$OE_LICENSE

$*

date
INP
