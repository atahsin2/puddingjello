# Pudding-Jello data processing

## Instructions

- Place data file in this folder, rename it to `data.txt`
- Open `config.toml` in a text editor. Change:
    - Change participant category. Options:
        - OA
        - Healthy
    - Change food category. Options:
        - Pudding
        - Jello
        - Both
    - Change the subject ID and pudding/jello profiles
- Call the processing script either in VS Code or with: `python3 process.py`
- Output stored in `[id_food].xlsx`