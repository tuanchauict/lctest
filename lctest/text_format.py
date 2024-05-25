import re

_text_formats = ['b', 'f', 'i', 'u']
_dark_colors = ["black", "red", "green", "yellow", "blue", "magenta", "cyan", "gray"]
_light_colors = ["brightblack", "brightred", "brightgreen", "brightyellow", "brightblue",
                 "brightmagenta", "brightcyan", "white"]


def _code(number):
    return f"\x1b[{number:02d}m"


_codes = {
    "</t>": _code(0),  # End text format
    "</c>": _code(39),  # End foreground color
    "</b>": _code(49),  # End background color
    "</>": _code(0) + _code(39) + _code(49) # End for all
}

for i, text_format in enumerate(_text_formats):
    _codes[f"<{text_format}>"] = _code(i + 1)

for i, (dark, light) in enumerate(list(zip(_dark_colors, _light_colors))):
    _codes[f"<{dark}>"] = _code(i + 30)
    _codes[f"<{light}>"] = _code(i + 90)

    _codes[f"<b:{dark}>"] = _code(i + 40)
    _codes[f"<b:{light}>"] = _code(i + 100)


def textformat(template, enabled=True):
    arr = re.split(r"(<.+?>)", template)
    for i, text in enumerate(arr):
        if text in _codes:
            arr[i] = _codes[text] if enabled else ""
    return "".join(arr)


if __name__ == '__main__':
    print(textformat("<b><b:red>home</b></c> is</t> <i>a <green>place</c> to <b><u>sleep</t>"))
    print(textformat("<b><b:red>home</b></c> is</t> <i>a <green>place</c> to <b><u>sleep</t>", enabled=False))
