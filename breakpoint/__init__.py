from prompt_toolkit import prompt
from prompt_toolkit.application import get_app
from prompt_toolkit.key_binding.vi_state import InputMode
from bullet import Check
import json
import bullet.colors
from pathlib import Path
from datetime import datetime

EMPTY_DATA = {"count": 0, "breakpoints": []}
DATA_DIR = Path.home() / ".breakpoint"
DATA_FILEPATH = DATA_DIR / "data.json"


def get_prompt_text(prompt):
    def inner():
        input_mode_map = {
            InputMode.INSERT: ("bg:ansigreen fg:white bold", "[I]"),
            InputMode.NAVIGATION: ("bg:ansired fg:white bold", "[N]"),
            InputMode.REPLACE: ("bg:ansigreen fg:white bold", "[R]"),
            InputMode.INSERT_MULTIPLE: ("bg:ansigreen fg:white bold", "[II]"),
        }
        input_mode = input_mode_map[get_app().vi_state.input_mode]
        # Make escape key register instantly--this is hacky but I don't want to
        # make a full-fledged Prompt Toolkit Application until I absolutely have
        # to
        get_app().ttimeoutlen = 0
        # input_mode = 'I' if get_app().vi_state.input_mode == InputMode.INSERT
        return [
            input_mode,
            ("", " "),
            ("", f"{prompt}: "),
        ]

    return inner


def load_data():
    if not DATA_DIR.exists():
        DATA_DIR.mkdir()

    if not DATA_FILEPATH.exists():
        with open(DATA_FILEPATH, "w") as data_file:
            json.dump(EMPTY_DATA, data_file)
        return EMPTY_DATA

    with open(DATA_FILEPATH) as data_file:
        return json.load(data_file)


def breakpoint():
    data = load_data()

    print()
    print("\x1b[1;31;40m●\x1b[0m breakpoint")
    print()

    # TODO: Consider https://python-prompt-toolkit.readthedocs.io/en/master/pages/asking_for_input.html#adding-custom-key-bindings
    automatic_thought = prompt(get_prompt_text("automatic thought"), vi_mode=True)

    distortions_checklist = Check(
        "cognitive distortions (see man page for more info): ",
        choices=[
            "all-or-nothing thinking",
            "overgeneralization",
            "focusing on negatives",
            "minimizing positives",
            "discounting the facts",
            "mind reading",
            "fortune telling",
            "emotional reasoning",
            "should statements",
            "labellng",
            "blaming self",
            "blaming others",
        ],
        check=" ✔",
        margin=2,
        # check_color = bullet.colors.bright(bullet.colors.foreground["red"]),
        # check_on_switch = bullet.colors.bright(bullet.colors.foreground["red"]),
        # background_color = bullet.colors.background["black"],
        # background_on_switch = bullet.colors.background["white"],
        # word_color = bullet.colors.foreground["white"],
        # word_on_switch = bullet.colors.foreground["black"]
    )

    distortions = distortions_checklist.launch()

    challenge = prompt(get_prompt_text("challenge"), vi_mode=True)
    replacement_thought = prompt(get_prompt_text("replacement thought"), vi_mode=True)

    data["count"] += 1

    breakpoint_data = {
        "id": data["count"],
        "date": datetime.now().isoformat(),
        "automatic_thought": automatic_thought,
        "distortions": distortions,
        "challenge": challenge,
        "replacement_thought": replacement_thought,
    }

    with open(DATA_FILEPATH, "w") as data_file:
        data["breakpoints"].append(breakpoint_data)
        json.dump(data, data_file, indent=4)


def list_breakpoints():
    data = load_data()

    for item in data["breakpoints"]:
        print()
        print(f'--- {item["id"]} ---')
        print()

        print(f'id: ')
        print(f'date: {item["date"]}')
        print(f'automatic thought: {item["automatic_thought"]}')
        print(f"distortions:")
        for distortion in item["distortions"]:
            print(f"- {distortion}")
        print(f'challenge: {item["challenge"]}')
        print(f'replacement thought: {item["replacement_thought"]}')
