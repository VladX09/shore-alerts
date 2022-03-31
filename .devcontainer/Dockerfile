FROM python:3.10-buster
ENV DEBIAN_FRONTEND=noninteractive

ENV CODE_PATH=/code
WORKDIR ${CODE_PATH}
RUN apt-get update && apt-get install -y git ssh

COPY . ${CODE_PATH}
RUN pip install -r ${CODE_PATH}/alerts/requirements.txt
RUN pip install -r ${CODE_PATH}/.devcontainer/requirements.txt
