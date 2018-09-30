#!/bin/bash
cd `dirname $0`
solr create_collection -c altosearch -shards 2 -replicationFactor 2 -d `pwd`

