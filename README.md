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
| C | churn_by_student | | Produce churn report by student |
| f | folder | path | REQUIRED path to CSV data file folder |
| g | gender | | Produce gender report |
| h | help | | Print usage text and exit |
| m | minor | minor text | NOT IMPLEMENTED YET |
| M | major | major text | Major description text |

## Examples

```text
Howdie!
```
