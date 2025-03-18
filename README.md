# Vulnerability Management Domain Discovery

The vulnman-domain-discovery project is a tool used to discover a list of target domains, which are then scanned by vulnerability scanners.

Domains are collected from various sources; currently supported sources are [BBOT](https://github.com/blacklanternsecurity/bbot) and Lubos (CSIRT-MU internal scanner built atop of Masscan). The domains are then saved to a database. Other tools may then use the database as a source of their scans.  

Domain Discovery (DD2) supports the blacklisting of domains; these are defined in the `blacklist.txt` file.

This repository contains only BBOT runner.

## Setup (Ansible)

See [SOCCER-Project-DEP/vulnman-ansible](https://github.com/SOCCER-Project-DEP/vulnman-ansible) for Ansible that deploys this tool alongside [vulnman-nuclei-orchestrator](https://github.com/SOCCER-Project-DEP/vulnman-nuclei-orchestrator).

## Setup (standalone)

```bash
# install dependencies
poetry install

# fill in PostgreSQL connection string
cp .env.example .env
```

## Usage

```bash
poetry run python src/main.py --help

# Or docker
docker run -it vulnman/domain-discovery poetry run python src/main.py --help
```

## Custom module

You can create custom modules to fetch domains from other sources. Put desired python file to `src/modules` directory and ensure that module has `main()` function that returns list of Domains (data model defined `src/lib/models.py`).

## Debbuging && FAQ

1. `Exception: Environment variable DB_CONN_STR is not set` - This error is thrown when the `DB_CONN_STR` environment variable is not set. This variable should contain the connection string to the database. Supply the PostgreSQL connection string in the `.env` file.

2. BBOT directly integrates with nuclei; what is the benefit of this tool? This solution is more flexible, and we are not locked in with just nuclei.

## Additional information

- This repository is being developed as a part of the [SOCCER](https://soccer.agh.edu.pl/en/) project.
- Developed by the cybersecurity team of [Masaryk University](https://www.muni.cz/en). 
- This project is a "mirror" of the original repository hosted on university Gitlab. New features and fixes here are being added upon new releases of the original repository.

## Help

Are you missing something? Do you have any suggestions or problems? Please create an issue.
Or ask us at `csirt-info@muni.cz`; we are happy to help you, answer your questions, or discuss your ideas.

