# BLS Data Puller

A small Python web app that pulls time series data from the U.S. Bureau of Labor Statistics API.

## Features

- Pull one or more BLS series IDs in one request.
- Configure start and end year.
- Uses registration key `f13fb030464043779475304f2e82c979` by default (can be overridden with environment variable).
- Displays returned data in a table.

## Run locally

```bash
python app.py
```

Then open <http://localhost:5000>.

## Configuration

Set `BLS_REGISTRATION_KEY` if you want to use a different key:

```bash
export BLS_REGISTRATION_KEY="your-key"
```
