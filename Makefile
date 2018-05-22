sync:
	rsync --exclude='.git/' --exclude='__pycache__/' --exclude=nvdgo.psql -avz . do-tst-mke-01.do.viaa.be:./scripts/nvdgo-namelinking
