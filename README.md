# GATKCNVSnakemake


This repo is my implementation of [GATK CNV Calling](https://gatk.broadinstitute.org/hc/en-us/articles/360035531152--How-to-Call-common-and-rare-germline-copy-number-variants) as a [Snakemake](https://snakemake.readthedocs.io/en/stable/) pipeline. My hope is this repo will help make cnv calling quick and easy for anyone. The skeleton of this pipeline originates from [Dmytro Kryvokhyzha's pipeline](https://evodify.com/gatk-cnv-snakemake/)

## Install

If you haven't already, install [conda](https://conda.io/projects/conda/en/latest/user-guide/install/index.html). This tool uses an older version of snakemake 4.3.1, where the `dynamic()` function still existed for easier scattering and parallelization. In the future I hope to update this to use `checkpoint`s and the most recent version of snakemake instead, but that is a huge headache and this works.

To install all necessary tools simply run

`conda env create -n gatk_snakemake -f environment.yml`

## Usage

Start the conda enviroment

`conda activate gatk_snakemake`

Example command

`snakemake --cluster "sbatch -J {cluster.job-name} -t {cluster.time}  -N {cluster.nodes}  -n {cluster.ntasks}  -p {cluster.partition}  --mem={cluster.mem} " --cores 640 -s gatk.snake --resources load=640 --cluster-config conf/cluster_config.yaml --rerun-incomplete  --config ref_samples="ref_absolute_paths.txt" samples="non_ref_absolute_paths.txt" ref_genome="/scratch/Shares/layer/ref/hg37/human_g1k_v37.fasta" ref_dict="/scratch/Shares/layer/ref/hg37/human_g1k_v37.dict" ploidy_priors="ploidy_priors.tsv"`

`ref_samples` : the file for this parameter should be a list of the **absolute** file paths for the bam files you want to use as the reference panel for SavvyCNV. Each `.bam` file should have an accompanying `.bai` in the same location.

Example:

```
/the/absolute/path/ref_sample_1.bam
/the/absolute/path/ref_sample_2.bam
/the/absolute/path/ref_sample_3.bam
```

`samples` : the file for this parameter should be a list of the **absolute** file paths for the bam files you want to call CNVs on. Each `.bam` file should have an accompanying `.bai` in the same location.

Example:
```
/the/absolute/path/sample_A.bam
/the/absolute/path/sample_B.bam
/the/absolute/path/sample_C.bam
```

`ref_genome`: reference genome `.fasta` file

`ref_dict` : reference genome `.dict` file

`ploidy_priors` : tsv file of the ploid priors for each chromosome. See the file `ploid_priors.tsv` for a basic example in humans.

`load` : this is a made up resource to help snakemake govern the allocation of jobs and total cores better.
Most rule in this pipeline need very few resources and run relatively quick, but a few like the cnv calling rule are massively resource intensive.
Snakemake's slurm integration does not handle this situtation very well, snakemake's integration with slurm only allows you to govern total number of jobs and cores per job. 
Thus I have created load units.
Essentially 1 load unit = 1 core.
In the case you are on shared computing platform with a cap on the number of cores a single user can request at a time, using just these two parameters is problematics because it will result in either too few small jobs which then become an unnecessary limit reagent, or too many large jobs which may violate the clusters usage limits.
Load units solves this problem.
When I run this pipeline I allocate 640 cores to snakemake and a corresponding 640 load units. Most rules have a specified 2 load units / cores in the .snake file, but a few of resource intensive rules have load = 64 (the total number of cores on each node of the cluster I use), so they consume the whole node.
This results in small rules running up to 320 jobs or the large rules running up to 10 jobs. I borrowed got the idea of load units from [this stackoverflow post](https://stackoverflow.com/questions/51977436/restrict-number-of-jobs-by-a-rule-in-snakemake)


### Notes:

All file paths need to be absolute, not relative, as the pipeline will be symlinking the files.

Each sample's `.bam` must have a unique name and an accompanying `.bai`. 

The the final output calls will be saved in `work/chr{j}_{sample}_intervals_cohort.vcf.gz` and `work/chr{j}_{sample}_segments_cohort.vcf.gz`.
