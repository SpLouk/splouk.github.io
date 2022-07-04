#!/bin/sh
aws s3 cp src s3://www.loukidelis.com --recursive --exclude "*.swp"
