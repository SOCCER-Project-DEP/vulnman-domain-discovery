FROM python:latest
WORKDIR /vulnman-domain-discovery

COPY . .

# Install dependencies
RUN apt-get update && apt-get install -y curl

# Install poetry
RUN curl -sSL https://install.python-poetry.org | POETRY_HOME=/usr/ python3 -
RUN /usr/bin/poetry install

# Install bbot
RUN pip install bbot
RUN bbot --install-all-deps

RUN mkdir /var/log/domain_discovery/