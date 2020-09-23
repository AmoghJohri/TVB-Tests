import sys 
import full_testing
import full_testing_legacy

method = sys.argv[1]
run    = sys.argv[2]
enc    = sys.argv[3] 
l      = sys.argv[4]
r      = sys.argv[5]
input_ = sys.argv[6]
output = sys.argv[7]
from_ = sys.argv[8]
to = sys.argv[9]
ran = sys.argv[10]

l = int(l)
r = int(r) 
from_ = int(from_)
to = int(to)
ran = int(ran)
if enc == "both":
    enc = ["LR", "RL"]
else:
    enc = [enc]
if run == "both":
    run = [1, 2]
else:
    run = [int(run)]
if method == "rsHRF":
    full_testing.main(run, enc, l, r, input_, output, from_, to, ran)
elif method == "legacy":
    full_testing_legacy.main(run, enc, l, r, input_, output, from_, to, ran)
