# lapl-directories

Explore phone directories in the Los Angeles Public Library:

https://rescarta.lapl.org/

## Install

    uv venv
    source .venv/bin/activate
    uv pip install -r requirements.txt
    
## Run

To generate a CSV of the phone directories and the number of pages in each:

    ./metadata.py > metadata.csv


