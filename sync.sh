#!/bin/bash
rsync --exclude="pythonmodules/ner/gmb/" --exclude='.idea/' --exclude="*.pyc" --exclude='*.log' --exclude='.git/' --exclude='__pycache__/' --exclude='*.psql' -avz . do-tst-mke-01.do.viaa.be:./scripts/nvdgo-namelinking "$@"
