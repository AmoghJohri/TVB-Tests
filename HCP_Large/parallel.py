import subprocess
from mpi4py import MPI

comm = MPI.COMM_WORLD
size = comm.Get_size()
rank = comm.Get_rank()

total = 767.
buckets = []
x = int(total/(size-1)) 
x_ = int(total - x*(size-1))

for i in range(0, size-1):
    buckets.append([i*x,(i+1)*x])
buckets.append([(size-1)*x,(size-1)*x+x_])

sudo_password = 'password'
command = ("docker run -v /path/to/HCP_YA_BIDS:/path/to/HCP_YA_BIDS -v /path/to/output_legacy:/Final_Output_Legacy -v /path/to/C_Input:/C_Input amoghjohri/tvbpipeline_aws python pipeline.py legacy 1 LR " + str(buckets[rank][0]) + " " + str(buckets[rank][1]) + " /path/to/HCP_YA_BIDS 0 61 4")
command = command.split()

cmd1 = subprocess.Popen(['echo',sudo_password], stdout=subprocess.PIPE)
cmd2 = subprocess.Popen(['sudo','-S'] + command, stdin=cmd1.stdout, stdout=subprocess.PIPE)

output = cmd2.stdout.read().decode() 