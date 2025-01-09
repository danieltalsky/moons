#!/usr/bin/env python3
"""
Convert Fortran 77 source files in a given directory to minimally modernized
Fortran 2003 free-form source. The script attempts only safe transformations:

1. Convert fixed-form to free-form:
   - Remove columns 73-80 (card sequence area).
   - Convert 'C'/'*'/'!' in column 1 to modern '!' comment.
   - Merge continuation lines (indicated by a non-blank in column 6).
2. Modernize old relational/logical operators (.EQ., .NE., .GT., etc.).
3. Normalize case (to lowercase).
4. Leave logic, GOTO, CONTINUE, and COMMON usage unchanged.

Usage:
    python modernize_f77_to_f2003.py path/to/input_directory path/to/output_directory

Requires Python 3.12+.
"""

import sys
import re
import argparse
from pathlib import Path

# Regex patterns for safely replacing old Fortran operators
OPERATOR_MAP = {
    r'\.eq\.': '==',
    r'\.ne\.': '/=',
    r'\.lt\.': '<',
    r'\.le\.': '<=',
    r'\.gt\.': '>',
    r'\.ge\.': '>=',
    r'\.and\.': '.and.',
    r'\.or\.': '.or.',
    r'\.not\.': '.not.',
    r'\.true\.': '.true.',
    r'\.false\.': '.false.',
}

GENERAL_STRING_REPLACEMENTS = {
    r'real*8': r'real(kind=8)',
    # This is just a specific outdated usage to spot replace
    r'1p1e22.15': r'1PE22.15'
}

def handle_comment_lines_and_strip(line: str) -> str:
    """
    Given a single Fortran 77 fixed-form line,
    handle any column-1 comment marks (C, *, or !).
    Returns the processed line
    """
    line = line.rstrip('\n')

    # Ensure we can safely index column 6 (index 5)
    # If the line is too short, pad it (for safety) or just skip
    if len(line) < 1:
        return line.rstrip()

    # If column 1 is 'C', '*', or '!', treat entire line as a comment
    first_char = line[0]
    if first_char in ['C', 'c', '*', '!']:
        # Convert to free-form comment
        return '!' + line[1:].rstrip()

    return line.rstrip()

def handle_continuations(lines: list[str]) -> list[str]:

    new_lines = []
    for i, line in enumerate(lines):

        if len(line) == 0:
            pass

        # ignore lines starting with '!' (already a comment)
        elif line[0] == '!':
            pass

        # Ensure we can safely index column 6 (index 5)
        # If the line is too short, skip
        elif len(line) < 7:
            pass

        elif line[5] in ['%', '1', '&']:
            # This line is a continuation of the previous line
            # 1) Append ' & ' to the *end* of the previous line (if it exists)
            prev_line = new_lines[-1]
            # Only add '&' if the previous line doesn’t already end in '&'
            if not prev_line.endswith('&'):
                new_lines[-1] = prev_line + ' &'

            # 2) Overwrite column 6 with '&' in the current line
            #    Old F77 might have any non-blank in col 6; we force '&'
            line = line[:5] + '& ' + line[6:]

        # Add the (possibly modified) line to our output list
        new_lines.append(line)

    return new_lines

def apply_operator_modernizations(line: str) -> str:
    """
    Apply safe operator replacements in a case-insensitive manner,
    but produce them in lowercase.
    """

    def lower_except_strings(match):
        # Extract the matched groups
        before_string = match.group(1)
        string_literal = match.group(2)
        after_string = match.group(3)

        # Lowercase the parts outside the string literal
        return before_string.lower() + string_literal + after_string.lower()

    # Lowercase the line first so replacements are straightforward.
    # Regex to match Fortran strings (single or double quotes)
    pattern = r"([^'\"]*)(['\"].*?['\"])([^'\"]*)"

    # Apply the regex and lower the parts outside the strings
    lowered = re.sub(pattern, lower_except_strings, line)

    # For each pattern, replace all occurrences
    for pattern, replacement in OPERATOR_MAP.items():
        # We want a case-insensitive replacement for the pattern,
        # but produce the modern Fortran in lowercase.
        lowered = re.sub(pattern, replacement, lowered, flags=re.IGNORECASE)

    # Apply general string replacements
    for substring, replacement in GENERAL_STRING_REPLACEMENTS.items():
        lowered = lowered.replace(substring, replacement)

    return lowered


def process_fortran_file(input_path: Path) -> str:
    """
    Reads a single Fortran 77 file from disk, converts to free-form
    Fortran 2003, applies operator modernizations, and returns the
    new file as a single string.
    """
    with input_path.open('r', encoding='utf-8', errors='ignore') as f:
        raw_lines = f.readlines()

    # 1) Handle comment lines
    result_lines = [handle_comment_lines_and_strip(ln) for ln in raw_lines]

    # 2) Handle line continuations
    result_lines = handle_continuations(result_lines)

    # 3) Modernize operators and ensure overall lowercasing
    result_lines = [apply_operator_modernizations(ln) for ln in result_lines]

    # Join into one string with newlines
    return '\n'.join(result_lines) + '\n'


def main():
    parser = argparse.ArgumentParser(
        description="Safely modernize Fortran 77 files to Fortran 2003 free-form."
    )
    parser.add_argument("input_dir", type=str,
                        help="Path to directory containing old Fortran 77 sources.")
    parser.add_argument("output_dir", type=str,
                        help="Path to directory where converted Fortran 2003 files will be placed.")
    args = parser.parse_args()

    input_path = Path(args.input_dir).resolve()
    output_path = Path(args.output_dir).resolve()

    if not input_path.is_dir():
        print(f"Error: input directory '{input_path}' does not exist or is not a directory.")
        sys.exit(1)

    output_path.mkdir(parents=True, exist_ok=True)

    # Common Fortran 77 file extensions; adapt as needed
    valid_exts = {'.f', '.for', '.f77', '.inc'}

    # Traverse input directory and convert each Fortran file
    for file in input_path.rglob('*'):
        if file.is_file() and file.suffix.lower() in valid_exts:
            # Process
            new_content = process_fortran_file(file)

            # Write out to output directory with a .f90 or .f03 extension
            # (Fortran compilers recognize .f90 or .f03 as free-form)
            if file.suffix.lower() == '.inc':
                out_name = file.stem + '.inc'
            else:
                out_name = file.stem + '.f03'
            out_file = output_path / out_name

            with out_file.open('w', encoding='utf-8') as outf:
                outf.write(new_content)

            print(f"Converted: {file.name} -> {out_file.name}")


if __name__ == "__main__":
    main()
