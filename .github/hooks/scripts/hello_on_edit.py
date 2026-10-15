import json
import sys

EDIT_TOOLS = {
    "replace_string_in_file",
    "multi_replace_string_in_file",
    "create_file",
    "edit_notebook_file",
    "apply_patch",
    "insert_edit_into_file",
}


def main() -> None:
    try:
        payload = json.load(sys.stdin)
    except json.JSONDecodeError:
        return
    if payload.get("tool_name") in EDIT_TOOLS:
        print(json.dumps({"systemMessage": "Hello! An edit tool is being called."}))


main()
