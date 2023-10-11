# GATKCNVSnakemake


This repo is my implementation of [GATK CNV Calling](https://gatk.broadinstitute.org/hc/en-us/articles/360035531152--How-to-Call-common-and-rare-germline-copy-number-variants) as a [Snakemake](https://snakemake.readthedocs.io/en/stable/) pipeline on a cluster using the [Slurm Workload Manager](https://slurm.schedmd.com/documentation.html). Alternate workflow managers can be used by changing the start command and settings saved in `conf/cluster_config.yaml`, refer to the (Snakemake documentation for more detail)[https://snakemake.readthedocs.io/en/stable/executing/cluster.html]. The skeleton of this pipeline originates from [a blog post by Dmytro Kryvokhyzha](https://evodify.com/gatk-cnv-snakemake/). May this repo and pipeline help you avoid the hell of setting up gCNV on your own.

## Install

If you haven't already, install [conda](https://conda.io/projects/conda/en/latest/user-guide/install/index.html). This tool uses an older version of Snakemake (4.3.1), where the `dynamic()` function still existed for easier scattering and parallelization. In the future, I hope to update this to use `checkpoint`s and the most recent version of snakemake instead, but that is a huge headache and this works just fine for now.

To install all necessary tools simply run

`conda env create -n gatk_snakemake -f gatk_gcnv.yml`

## Usage

Start the conda environment

`conda activate gatk_gcnv`

Example command

`snakemake --cluster "sbatch -J {cluster.job-name} -t {cluster.time}  -N {cluster.nodes}  -n {cluster.ntasks}  -p {cluster.partition}  --mem={cluster.mem} " --cores 640 -s gatk.snake --resources load=640 --cluster-config conf/cluster_config.yaml --rerun-incomplete  --config ref_samples="ref_absolute_paths.txt" samples="non_ref_absolute_paths.txt" ref_genome="/scratch/Shares/layer/ref/hg37/human_g1k_v37.fasta" ref_dict="/scratch/Shares/layer/ref/hg37/human_g1k_v37.dict" ploidy_priors="ploidy_priors.tsv"`

`ref_samples`: the file for this parameter should be a list of the **absolute** file paths for the bam files you want to use as the reference panel for SavvyCNV. Each `.bam` file should have an accompanying `.bai` in the same location.

Example:

```
/the/absolute/path/ref_sample_1.bam
/the/absolute/path/ref_sample_2.bam
/the/absolute/path/ref_sample_3.bam
```

`samples`: the file for this parameter should be a list of the **absolute** file paths for the bam files you want to call CNVs on. Each `.bam` file should have an accompanying `.bai` in the same location.

Example:
```
/the/absolute/path/sample_A.bam
/the/absolute/path/sample_B.bam
/the/absolute/path/sample_C.bam
```

`ref_genome`: reference genome `.fasta` file

`ref_dict`: reference genome `.dict` file

`ploidy_priors`: tsv file of the ploid priors for each chromosome. See the file `ploid_priors.tsv` for a basic example in humans.

`load`: this is a made-up resource to help snakemake govern the allocation of jobs and total cores better.
Most rules in this pipeline need very few resources and run relatively quickly, but a few like the cnv calling rule are massively resource-intensive.
Snakemake's slurm integration does not handle this situation very well, snakemake's integration with slurm only allows you to govern a total number of jobs and cores per job. 
Thus I have created load units.
Essentially 1 load unit = 1 core.
In the case you are on a shared computing platform with a cap on the number of cores a single user can request at a time, using just these two parameters is problematic because it will result in either too few small jobs which then become an unnecessary limit reagent, or too many large jobs which may violate the clusters usage limits.
Load units solves this problem.
When I run this pipeline I allocate 640 cores to snakemake and a corresponding 640 load units. Most rules have a specified 2 load units/cores in the .snake file, but a few of resource intensive rules have load = 64 (the total number of cores on each node of the cluster I use), so they consume the whole node.
This results in small rules running up to 320 jobs or large rules running up to 10 jobs. I borrowed got the idea of load units from [this stackoverflow post](https://stackoverflow.com/questions/51977436/restrict-number-of-jobs-by-a-rule-in-snakemake)


### Notes:

All file paths need to be absolute, not relative, as the pipeline will be symlinking the files.

Each sample's `.bam` must have a unique name and an accompanying `.bai`. In the code it assumes that files are named `file1.bam` and `file1.bam.bai`. To change this assumption you can dig through the code of `gatk.snake`, it would need to be changed in two calls of the `replace` function in the rule `create_symlink_script`. 

The number of cores used for each job have been hard-coded into  `gatk.snake`. It assumes 1 whole compute node has 64 cores and requests a whole node for each job spawned for the rules `cnvcall`, `process_cnvcalls`, and `determine_ploidy`. The GATK processes automatically expand to use all available cores and changing this behavior has surprisingly proven difficult.

The final output calls will be saved in `work/chr{j}_{sample}_intervals_cohort.vcf.gz` and `work/chr{j}_{sample}_segments_cohort.vcf.gz`.
