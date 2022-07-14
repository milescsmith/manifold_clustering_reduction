from python:3.9.11-slim

ENV DEBIAN_FRONTEND=noninteractive
RUN apt update --fix-missing \
    && apt install --no-install-recommends -y \
        git \
    && apt clean \
    && rm -rf /tmp/downloaded_packages/* \
    && rm -rf /var/lib/apt/lists/*

#RUN pip install "mcr[dash] @ git+https://github.com/milescsmith/manifold_clustering_reduction@main"

WORKDIR /opt
COPY . ./mcr
RUN pip install ./mcr[dash]

EXPOSE 8787

CMD [ "mcr-dash" ]