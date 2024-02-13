#! /usr/bin/env bash
set -e

celery -A workers.celery_tasks worker -l info -Q main-queue -E