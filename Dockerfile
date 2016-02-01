FROM ubuntu

RUN apt-get update \
    && apt-get install -y \
        python-dev \
        python3-dev \
        libffi-dev \
        libssl-dev \
        python-pip \
        python3-pip \
        python-tox \
        git \
    && git clone https://github.com/sstephenson/bats.git && cd bats && ./install.sh /usr/local/ && cd -

ADD . /serverauditor

WORKDIR /serverauditor

CMD tox
