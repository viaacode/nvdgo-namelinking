#!/bin/bash
cd $(dirname "$0")
cd ..
rsync --exclude="revindexes/" --exclude="indexes/" --exclude="pythonmodules/ner/gmb/" --exclude=config.ini --exclude='.idea/' --exclude="*.pyc" --exclude='*.log' --exclude='.git/' --exclude='__pycache__/' --exclude='*.psql' -avz . do-tst-mke-01.do.viaa.be:./scripts/nvdgo-namelinking "$@"
