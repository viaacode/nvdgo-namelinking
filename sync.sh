#!/bin/bash
rsync --exclude='gmb-2.2.0/' --exclude="*.pyc" --exclude='*.log' --exclude='.git/' --exclude='__pycache__/' --exclude='*.psql' -avz . do-tst-mke-01.do.viaa.be:./scripts/nvdgo-namelinking "$@"
