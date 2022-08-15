#!/usr/bin/env bash
echo "Start task 1 script"
rq worker --url redis://redis:6379
