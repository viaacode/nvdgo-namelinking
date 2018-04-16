#!/bin/bash
rsync --exclude="db.sqlite3" --exclude='.git/' --exclude='__pycache__/' -avz . do-tst-mke-01.do.viaa.be:./scripts/nvdgo-namelinking
