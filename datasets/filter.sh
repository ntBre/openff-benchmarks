#!/bin/bash
#SBATCH -J filter-dataset
#SBATCH -p standard
#SBATCH -t 72:00:00
#SBATCH --nodes=1
#SBATCH --cpus-per-task=1
#SBATCH --mem=16gb
#SBATCH --account dmobley_lab
#SBATCH --export ALL
#SBATCH --constraint=fastscratch
#SBATCH --output=logs/filter.out

date
hostname
echo $SLURM_JOB_ID

source ~/.bashrc
mamba activate fb-196-qcnew

echo $OE_LICENSE

make filtered-industry.json

date
