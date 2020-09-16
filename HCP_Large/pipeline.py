import sys 
import full_testing
import full_testing_legacy

method = sys.argv[1]
run    = sys.argv[2]
enc    = sys.argv[3] 
l      = sys.argv[4]
r      = sys.argv[5]

l = int(l)
r = int(r) 
if enc == "both":
    enc = ["LR", "RL"]
else:
    enc = [enc]
if run == "both":
    run = [1, 2]
else:
    run = [int(run)]
if method == "rsHRF":
    full_testing.main(run, enc, l, r)
elif method == "legacy":
    full_testing_legacy.main(run, enc, l, r)
