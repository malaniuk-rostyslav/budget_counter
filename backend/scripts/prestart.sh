#! /usr/bin/env bash

# Create alias for manual using inside docker container
./scripts/alias.sh

# Let the DB start
python /backend/db/commands/init_db.py

# Run migrations
alembic upgrade head

# Create initial data in DB
python /backend/db/commands/initial_data.py
