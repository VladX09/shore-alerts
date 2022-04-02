FROM python:3.10-buster
ENV DEBIAN_FRONTEND=noninteractive

ENV CODE_PATH=/code

COPY ./alerts ${CODE_PATH}
RUN pip install -r ${CODE_PATH}/requirements.txt

COPY ./common_lib /common_lib
RUN pip install -r /common_lib/requirements.txt
# TODO: remove dev flag
RUN pip install -e /common_lib

WORKDIR ${CODE_PATH}/alerts
