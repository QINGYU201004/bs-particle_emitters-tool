# bs-particle_emitters-tool

A command-line toolkit for processing `particle_emitters` JSON files.

## Features

- Fix loose/non-standard JSON format and output sorted, pretty JSON.
- Convert newer particle emitter format to older compatible format.
- Search effects by emitter key and `movieclip` (`swf` / `name`) keywords.
- Extract unique SC names from `movieclip.swf` and export them as a CSV file with a header row.
- Read `ParticleEmitterName` values from a CSV file and export matched full key/value entries from `particle_emitters_old.json`.
- Safely merge one JSON file into another while skipping duplicate keys.
- Multi-language menu: English, Chinese, Russian.

## Requirements

- Python 3.8+

## Quick Start

```bash
python3 main.py
```

Then choose an action from the menu:

- `1`: Fix JSON (`fix.py`)
- `2`: Convert new format to old (`old.py`)
- `3`: Search/extract effects (`search.py`)
- `4`: Physical merge/append JSON (`add.py`)
- `5`: Switch language
- `6`: Extract SC names from `movieclip.swf` (`sc_extract.py`)
- `7`: Extract `ParticleEmitterName` matches from CSV into `_name.json` (`csv_name_extract.py`)

## Project Structure

```text
.
├── main.py
└── lib
    ├── add.py
    ├── fix.py
    ├── language.py
    ├── old.py
    ├── csv_name_extract.py
    ├── sc_extract.py
    └── search.py
```

## Notes

- Output filenames can be entered manually in the CLI prompts.
- For large JSON files, processing may take some time depending on device performance.

## License

No license file is currently included.
