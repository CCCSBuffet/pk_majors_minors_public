# Tools to process Major and Minor reports

This is an internal tool. This is not a student project.

## Preparing the data

Reports are provided monthly (currently by mjonas1@carthage.edu) as an `xlsx` file. 

This tool expects `CSV` files be collected in a single folder. `xlsx` files, being compressed cannot be directly read as text. Currently, this means each file must be loaded into Excel then saved as a `csv`. Someday, this will change with the writing of a dedicated tool to use Excel `interop`.

An additional complication is that no date information is contained in a report and all reports have the same title. This means that during the export process, some file name differentiation must be added. This tool expects file names to be in the form of:

```text
MM-YYYY-mm.csv
```

Where:

| Symbol | Meaning |
| ------ | ------- |
| MM | This is a literal string |
| YYYY | Four digit year |
| mm | Two digit month |

For example:

```text
$ ls csv
MM-2019-09.csv  MM-2019-10.csv  MM-2019-11.csv  MM-2019-12.csv  MM-2020-01.csv
```

### Headings

The tool(s) are designed to use header values as keys rather than column indices. This makes the correct operation of the tool(s) dependent upon those values. This is a weakness but preferred to using indicies which may be even more fragile.

## Command line options

| -Short | --Long | Argument | Function |
| ------ | ------ | -------- | -------- |
| c | churn_by_month | | Produce churn report month by month |
| C | churn_by_student | | Produce churn report by student - NOT IMPLEMENTED YET |
| f | folder | path | REQUIRED path to CSV data file folder |
| g | gender | | Produce gender report |
| h | help | | Print usage text and exit |
| m | minor | minor text | NOT IMPLEMENTED YET |
| M | major | major text | Major description text |

## Examples - Discussion

### Gender report

```text
hyde pk_majors_minors $> python3 mmreport.py -M "Computer Science" --gender
Report    Majors                    Minors
              F    M Total   Ratio     F    M Total   Ratio
2019-08      18   61    79    0.23    16   14    30    0.53
2019-09      19   61    80    0.24    15   17    32    0.47
2019-10      19   59    78    0.24    16   18    34    0.47
2019-11      19   57    76    0.25    14   16    30    0.47
2019-12      18   53    71    0.25    11   16    27    0.41
2020-01      18   53    71    0.25     9   16    25    0.36
2020-02      18   54    72    0.25     9   15    24    0.38
hyde pk_majors_minors $>
```

You will note that a folder containing `CSV` files spanning months in which students typically graduate will show a drop in the next month of churn report. This is of course, to be expected.

### Churn by month report

```text
--- MAJORS ---

Adds  - In 2019-09 but not in 2019-08
STUDENT     STUDENT       F 3.166 STUDENT@carthage.edu       2021   RC

Drops - In 2019-08 but not in 2019-09
None

Adds  - In 2019-10 but not in 2019-09
STUDENT    STUDENT        F 0.000 STUDENT@carthage.edu       2023   RC

Drops - In 2019-09 but not in 2019-10
STUDENT    STUDENT        M 0.000 STUDENT@carthage.edu       2023   RC
STUDENT    STUDENT        M 0.000 STUDENT@carthage.edu       2023   RC
STUDENT    STUDENT        F 2.287 STUDENT@carthage.edu       2022   RC

REPORT CONTINUES - REMOVED FOR BREVITY
```

In the churn by month report, information about each student is provided so as to provide some clue as to why they might have taken the action they took.

For example, you may see that a student who appears to have dropped a major or minor also specified an expected graduate year and term that corresponds to the
month in which the left the source data.

You may see that a student dropped a major or minor with a very low cumulative GPA. This could be a reason for the drop. Note, that first year students will show a 0.00 GPA. These students dropping can reasonably be explained as being those who were tasting the major or minor and decided to switch.

Another reasonable explanation for a drop of a minor is that the student found the demands of their major too large. Or, they picked up a different minor more suited to their interests.

### Churn by student

This is not implemented yet.

## Requirements

This tool is written for Python 3. The library modules it uses are standard with Python 3 so do not require additional installation.

This tool is run from the command line. It can be made to launch from the desktop with some effort.
