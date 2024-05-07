# Pink RST 🩷
Opinionated ReStructured Text (.rst) Formatter inspired by [Black](https://github.com/psf/black). 

Remember: [RST Files wear pink EVERY day of the week.](https://www.youtube.com/watch?v=xBbOAVSBvpE)

## Install

``` bash
pip3 install git+https://github.com/biosafetylvl5/pinkrst.git
```

or

``` bash
pip install git+https://github.com/biosafetylvl5/pinkrst.git
```

## Usage

``` bash
pink file.rst # to process individual file
```

``` bash
pink --max-line-length 100 file.rst # set max line length
```

``` bash
pink # to process files in dir and recursively processes sub-folder files
```

``` bash
pink --no-recurse # to process files in dir WITHOUT recusion
```

``` bash
pink --no-recurse # to process files in dir WITHOUT recusion
```

``` bash
pink --no-recurse --replace-tabs --spaces-per-tab 4 --smart-wrap --max-line-length 100 directory/ # or go crazy, see next section
```

### CLI Arguments

### Optional Arguments

| Argument                          | Description                                                               |
|-----------------------------------|---------------------------------------------------------------------------|
| `-h, --help`                      | Show help message and exit.                                               |
| `-rx, --no-recurse`               | Turns off recursively parsing subdirectories. Recursion is enabled by default. |
| `--disable-no-trailing-whitespace`| Disables the removal of trailing whitespace on each line                  |
| `--disaple-replace-tabs`          | Disables replacing tabs with spaces                                        |
| `--spaces-per-tab SPACESPERTAB`   | Specifies the number of spaces to replace each tab with. Default is 4 spaces. |
| `--disable-trim-excess-empty-lines` | Disables trimming excess empty lines from files.                        |
| `--disable-trailing-newline`      | Disable ensuring that files end with a newline character.                          |
| `--disable-smart-wrap`            | Disable intelligently wraps long lines that exceed a specified width.             |
| `--max-line-length LINELENGTH`    | Sets the maximum line length after which wrapping should occur. Default is 120 characters. |


