import sys
import subprocess

from_ = sys.argv[1]

sudo_password = 'password'
command = ("docker run -v /path/to/HCP_YA_BIDS:/path/to/HCP_YA_BIDS -v /path/to/output_legacy:/Final_Output_Legacy -v /path/to/C_Input:/C_Input amoghjohri/tvbpipeline_aws python pipeline.py legacy 1 LR " + from_ + " " + str(int(from_) + 1) + " /path/to/HCP_YA_BIDS 0 61 4")
command       = command.split()

cmd1   = subprocess.Popen(['echo',sudo_password], stdout=subprocess.PIPE)
cmd2   = subprocess.Popen(['sudo','-S'] + command, stdin=cmd1.stdout, stdout=subprocess.PIPE)

output = cmd2.stdout.read().decode() 