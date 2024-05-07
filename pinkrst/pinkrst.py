import os
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


def addTrailingNewLine(filelines):
    if not filelines[-1] == "\n":
        return filelines + ["\n"]
    else:
        return filelines


def getIndent(line):
    newLine = line.replace("- ", "  ").replace("* ", "  ")
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
        processedString = "\n".join(processedLines)
        processedString = workOnCompleteFileString(args, processedString)

        if not processedString == fileOriginal:
            # Write the processed lines back to the file
            with open(file_path, "w") as file:
                file.write(processedString)
            return True
        return False

    except Exception as e:
        print(f"Error processing the file {file}: {e}")


def setupConsole():

    return Console()


def main():
    args = setupCLI()

    console = setupConsole()

    changed = sendFilesToProcessor(args, console)

    handleCLIOutput(console, changed)


def sendFilesToProcessor(args, console):
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


if __name__ == "__main__":
    main()
