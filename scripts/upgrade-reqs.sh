#!/bin/bash
cd `dirname "$0"`
cd ..
pipreqs . --savepath docker/requirements.pip "$@"
