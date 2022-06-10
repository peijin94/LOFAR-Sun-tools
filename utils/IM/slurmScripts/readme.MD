# Run Imaging on Cluster


![](./slurm%20clean.png)

## Compute Job Submission

Submit job with ```sbatch``` script to start a few individual tasks in a few compute node in cluster.

In each task, it will start a singularity contianer of LOFAR-Interferometry-Imaging with necessary software installed, and run ```runOneJob.sh``` in the container.

The ```runOneJob.sh``` will init the software enviroment and and start the job command (DPPP or Clean) with a parameter ```${SLURM_ARRAY_TASK_ID}``` which specify the current index of compute job, this parameter is used to let the compute script now which Subband to work on.


