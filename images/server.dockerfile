### Build and install packages
FROM python:3.8 as build-python

# Cleanup apt cache
RUN apt-get clean && rm -rf /var/lib/apt/lists/*
RUN apt-get install wget -y

WORKDIR /backend/


# Install Python dependencies
COPY ./requirements.txt /backend/

RUN pip install -r requirements.txt

# Final build
FROM python:3.8-slim

# Remove apt chache
RUN apt-get clean && rm -rf /var/lib/apt/lists/*

COPY --from=build-python /usr/local/lib/python3.8/site-packages/ /usr/local/lib/python3.8/site-packages/
COPY --from=build-python /usr/local/bin/ /usr/local/bin/

WORKDIR /backend/

# Copy scripts for starting project
COPY ./backend/ /backend/

RUN find . -type f -iname "*.sh" -exec chmod +x {} \;

EXPOSE 8000
ENV PYTHONPATH=.
CMD ["./scripts/start.sh"]
