#!/bin/sh
curl -XPOST http://localhost:2468/api/webhook --data-urlencode "name=$1"
