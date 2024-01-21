# Pudding-Jello data processing

A Python data processing script for a large-scale hedonic perceptions analysis study of neuropathic pain patients. 

## Instructions

### Setup

- Install the required Python depednencies with `python3 -m pip install -r requirements.txt`.

### Usage

- Place data file in this folder, rename it to `data.txt`.
    - Refer to `sample_data.txt` to see how this data looks like.
- Open `config.toml` in a text editor. Change:
    - Change participant category. Options:
        - OA
        - Healthy
    - Change food category. Options:
        - Pudding
        - Jello
        - Both
    - Change the subject ID and pudding/jello profiles.
- Call the processing script either in VS Code or with: `python3 process.py`.
- Output stored in `[id_food].xlsx`.