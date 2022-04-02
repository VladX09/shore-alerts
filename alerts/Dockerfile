FROM python:3.10-buster
ENV DEBIAN_FRONTEND=noninteractive

ENV CODE_PATH=/code
WORKDIR ${CODE_PATH}

COPY ./alerts ${CODE_PATH}
RUN pip install -r ${CODE_PATH}/alerts/requirements.txt
