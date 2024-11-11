import os
import re
import textwrap

import argparse
from rich.console import Console


def removeTrailingWhitespace(line):
    return [line.rstrip()]


def replaceTabsWithSpaces(line, spacesPerTab=4):
    return [line.replace("\t", " " * spacesPerTab)]


def trimExcessEmptyLines(filestring):
    # this is SO not optimal, should improve if slow in use
    while "\n\n\n" in filestring:
        filestring = filestring.replace("\n\n\n", "\n\n")
    if filestring[-2:-1] == "\n" == filestring[-1:]:
        return filestring[:-1]
    return filestring


def isSectionHeaderUnderline(line):
    if len(line) > 2:
        charsInLine = list(set(line))
        if len(charsInLine) == 1 and charsInLine[0] in ["#", "*", "=", "-", "^", '"']:
            return True
    return False


def fixSectionHeaderUnderlines(lines):
    for i in range(0, len(lines)):
        if isSectionHeaderUnderline(lines[i]):
            lines[i] = lines[i][0] * len(lines[i - 1])
    return lines


def addTrailingNewLine(lines):
    """Ensure the last element of a list of strings ends with a newline character.

    This function checks if the last element in the list `lines` ends with
    a newline character (`\\n`). If it does not, it appends a newline character
    to the list. If the last element already ends with a newline character,
    it returns the list unchanged.

    Parameters
    ----------
    lines : list of str
        A list of strings, each representing a line in a file.

    Returns
    -------
    list of str
        The modified list of strings. This list will be the same as the input
        list if the last string already ends with a newline character.
        Otherwise, it will be the input list with an additional newline character
        appended.

    Examples
    --------
    >>> addTrailingNewLine(["Line 1\\n", "Line 2"])
    ["Line 1\\n", "Line 2", "\\n"]

    >>> addTrailingNewLine(["Line 1\\n", "Line 2\\n"])
    ["Line 1\\n", "Line 2\\n"]

    >>> addTrailingNewLine(["Line 1", "Line 2"])
    ["Line 1", "Line 2", "\\n"]

    Notes
    -----
    - The function assumes that `lines` is a non-empty list.
      If an empty list is passed, the function will raise an `IndexError`.
    """

    if not lines[-1] == "\n":
        return lines + ["\n"]
    else:
        return lines


def getIndent(line):
    """Return leading spaces or leading bullets from a line of text

    This function replaces each occurrence of "- " "* " or "#. " (where # is a number)
    with spaces, and then returns the left leading spaces.

    Parameters
    ----------
    line : str
        A line of text

    Returns
    -------
    str
        A substring of the original line that consists only of the leading "indent",
        this could be spaces or bullets

    Examples
    --------
    >>> getIndent("    Item 1")
    '    '
    >>> getIndent("  - Item 2")
    '  - '
    >>> getIndent("  - 1. Item 3: stacked bullets are returned")
    '  - 1. '
    >>> getIndent("  - Item A 1. Item B: interrupted bullets are not")
    '  - '
    >>> getIndent("    * Item 4")
    '    * '
    >>> getIndent("\\t* Item 5")
    ''
    >>> getIndent("No leading space")
    ''
    """
    # This pattern matches a number followed by a period and a space,
    # or "*" or "-" followed by a space
    pattern = r"(\d+\.\s|\*\s|-\s)"

    def replacement(match):
        if match.group() in {"* ", "- "}:
            return "  "  # Replace "* " or "- " with two spaces
        else:
            return " " * len(
                match.group()
            )  # Replace digit and period with spaces, maintaining length

    newLine = re.sub(pattern, replacement, line)
    return line[0 : len(newLine) - len(newLine.lstrip(" "))]


def smartWrapLongLines(line):
    if len(line) > 120:
        indent = getIndent(line)
        noWrapLineEndings = ["\\", "+"]
        if len(indent) > 1 and line[-1] in noWrapLineEndings:
            return [line]
        newLines = textwrap.wrap(
            line,
            width=120,
            initial_indent="",
            subsequent_indent=" " * len(indent),
            break_long_words=False,
            replace_whitespace=False,
            break_on_hyphens=False,
        )
        if len(newLines) == 1 and indent + newLines[0] == line:
            return [line]
        else:
            return newLines
    else:
        return [line]


def getLineProcessingFunctions(args):
    replaceTabsWithSpacesCurried = lambda line: replaceTabsWithSpaces(
        line, spacesPerTab=args.spacesPerTab
    )
    funcListWithArgs = [
        [replaceTabsWithSpacesCurried, args.replaceTabsWithSpaces],
        [removeTrailingWhitespace, args.removeTrailingWhitespace],
        [smartWrapLongLines, args.smartWrapLongLines],
    ]

    funcsToUse = [func for func, enabled in funcListWithArgs if enabled]
    return funcsToUse


def workOnFileLines(args, fileOriginalLines):
    processedLines = []
    for originalLine in fileOriginalLines:
        lines = [originalLine]
        for f in getLineProcessingFunctions(args):
            for line in lines:
                lines = f(line)
        processedLines.extend(lines)

    if args.addTrailingNewLine:
        processedLines = addTrailingNewLine(processedLines)
    return processedLines


def workOnCompleteFileString(args, processedString):
    if args.trimExcessEmptyLines:
        processedString = trimExcessEmptyLines(processedString)
    return processedString


def processFile(file_path, args):
    try:
        # Read the file
        with open(file_path, "r") as file:
            fileOriginal = file.read()

        fileOriginalLines = fileOriginal.split("\n")

        processedLines = workOnFileLines(args, fileOriginalLines)
        if args.fixSectionHeaderUnderlines:
            processedLines = fixSectionHeaderUnderlines(processedLines)
        processedString = "\n".join(processedLines)
        processedString = workOnCompleteFileString(args, processedString)

        if not processedString == fileOriginal:
            # Write the processed lines back to the file
            with open(file_path, "w") as file:
                file.write(processedString)
            return True
        return False

    except Exception as e:
        print(f"Error processing the file {file_path}: {e}")


def setupConsole():

    return Console()


def collectFilesAndSendToProcessor(args, console):
    files = []
    if args.recurse:
        for root, dirs, filenames in os.walk(args.file[0]):
            for filename in filenames:
                files.append(os.path.join(root, filename))
    files.extend(args.file)

    changed = []
    for file in files:
        filename, fileExtension = os.path.splitext(file)
        if ".rst" == fileExtension[-4:]:
            change = processFile(file, args)
            if change:
                console.log("reformatted", file)
            changed.append([file, change])
    return changed


def handleCLIOutput(console, changed):
    if len(changed) == 0:
        console.print(
            "No rst files are present to be formatted. Nothing to do :sleeping_face:"
        )
        exit()

    console.print("All done! :revolving_hearts:\n")

    numChanged = sum([not change for file, change in changed])
    if numChanged > 0:
        console.print(f"{numChanged} files left unchanged")


def setupCLI():
    parser = argparse.ArgumentParser(
        description="Process a file to remove trailing whitespaces,"
        "replace tabs with spaces, and avoid extra newlines at the end."
    )
    parser.add_argument(
        "file",
        type=str,
        help="Path to the file to be processed, defaults to current directory",
        nargs="*",
        default=".",
    )
    parser.add_argument(
        "-rx",
        "--no-recurse",
        action="store_false",
        default=True,
        dest="recurse",
        help="Turns off recursively parsing subdirectories, on by default",
    )
    parser.add_argument(
        "--disable-no-trailing-whitespace",
        action="store_false",
        default=True,
        dest="removeTrailingWhitespace",
        help="Disables formatting that removes trailing whitespace on each line",
    )
    parser.add_argument(
        "--disable-fix-section-underlines",
        action="store_false",
        default=True,
        dest="fixSectionHeaderUnderlines",
        help="Disables formatting that extends/shortens section underlines to match title",
    )
    parser.add_argument(
        "--disable-replace-tabs",
        action="store_false",
        default=True,
        dest="replaceTabsWithSpaces",
        help="Disables replacing tabs with spaces in the provided text",
    )
    parser.add_argument(
        "--spaces-per-tab",
        type=int,
        default=4,
        dest="spacesPerTab",
        help="Number of spaces to replace each tab with (default: 4)",
    )
    parser.add_argument(
        "--disable-trim-excess-empty-lines",
        action="store_false",
        dest="trimExcessEmptyLines",
        help="Disables trimming excess empty lines from files",
    )
    parser.add_argument(
        "--disable-add-trailing-newline",
        action="store_false",
        default=True,
        dest="addTrailingNewLine",
        help="Disable ensuring files end with a newline character",
    )
    parser.add_argument(
        "--disable-smart-wrap",
        action="store_false",
        default=True,
        dest="smartWrapLongLines",
        help="Disable intelligently wrap long lines that exceed a certain width",
    )
    parser.add_argument(
        "--max-line-length",
        type=int,
        default=120,
        dest="lineLength",
        help="The maximum length of line after which wrapping should occur"
        + " (default: 120 characters).",
    )

    args = parser.parse_args()
    return args


def main():
    args = setupCLI()

    console = setupConsole()

    changed = collectFilesAndSendToProcessor(args, console)

    handleCLIOutput(console, changed)


if __name__ == "__main__":
    main()
