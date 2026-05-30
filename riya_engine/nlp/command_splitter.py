
def split_commands(text: str):
    """
    Split multi-action user commands into
    sequential executable commands.
    """

    connectors = [
        " and ",
        " then ",
        " after that ",
        " also ",
        ","
    ]

    commands = [text]

    for connector in connectors:
        new_commands = []

        for cmd in commands:
            parts = cmd.split(connector)
            new_commands.extend(parts)

        commands = new_commands

    # clean whitespace
    commands = [c.strip() for c in commands if c.strip()]

    print(f"[Splitter] Commands detected: {commands}")

    return commands