### Build and install packages
FROM python:3.8 as build-python

# Cleanup apt cache
RUN apt-get clean && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY ./requirements.txt /backend/

WORKDIR /backend/
RUN pip install -r requirements.txt
# jupyter lab --ip=0.0.0.0 --allow-root --NotebookApp.custom_display_url=http://127.0.0.1:8888
ARG INSTALL_JUPYTER=false
RUN bash -c "if [ $INSTALL_JUPYTER == 'true' ] ; then pip install jupyterlab ; fi"
### Final image
FROM python:3.8-slim

# Remove apt chache
RUN apt-get clean && rm -rf /var/lib/apt/lists/*

COPY --from=build-python /usr/local/lib/python3.8/site-packages/ /usr/local/lib/python3.8/site-packages/
COPY --from=build-python /usr/local/bin/ /usr/local/bin/

# Copy scripts for starting project
COPY backend/ /backend/
WORKDIR /backend/
RUN find . -type f -iname "*.sh" -exec chmod +x {} \;
# RUN apt update -y && apt install ffmpeg -y

EXPOSE 8000
ENV PYTHONPATH=.
CMD ["bash", "./scripts/worker-start.sh"]
