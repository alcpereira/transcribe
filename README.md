# Transcribe

## Description

This project extracts information from transcription (format `.trs` and `.trico`) into human readable insights.

## How to run it

Make sure to install the dependencies:

```sh
pip install -r requirements.txt
```

To run the project:

```sh
python main.py
```

For example to save the console output into the file `output.txt`, run:

```sh
python main.py > output.txt
```

## Charts

To display or save the charts on your local machine you can use:

```sh
python main.py --draw-timeline # to show the timeline charts
python main.py --save-timeline # to save the timeline charts
python main.py --draw-piechart # to show the pie charts
```

## How to run the tests

```sh
pytest
```

For coverage run:

```sh
coverage run -m pytest
```
