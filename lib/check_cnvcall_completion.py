import sys
from os.path import exists

"""
How to use this file.
1. j, the chromosome
2. fragment, the shard in question
3. n, the number of samples being run through the pipeline
4. name of the check file to be procuded if all is well
"""

#  work/cohort-calls_chr{j}/frag_{fragment}-calls/SAMPLE_{s_index}/sample_name.txt
path_to_file_template = 'work/cohort-calls_chr{j}/frag_{fragment}-calls/SAMPLE_{s_index}/sample_name.txt'
frag = sys.argv[2].split('/')[2]
for i in range(int(sys.argv[3])):
    path_to_file = path_to_file_template.format(j=sys.argv[1],fragment=frag,s_index=str(i))
    if not exists(path_to_file):
        print('Missing file {}'.format(path_to_file))
        quit()

with open(sys.argv[4],'w') as f:
    f.write('All files are present')


