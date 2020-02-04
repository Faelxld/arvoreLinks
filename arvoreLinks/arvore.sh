#!/bin/bash
PATH=/sbin:/usr/sbin:/bin:/usr/bin
if ps -ef | grep -v grep | grep arvore; then
  exit 0
else
  cd /home/mgsilva/crawlerLinks/arvoreLinks/arvoreLinks/
  sudo scrapy crawl arvore
  curl " http://192.168.1.7:8983/solr/admin/cores?action=RELOAD&core=links"
  exit 0
fi
