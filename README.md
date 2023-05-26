# Sasquatch (Search for SBox using STP) 
_Release: 25 May 2023._

This repository contains source codes and related material for the paper; **"Finding Desirable Substitution Boxes with SASQUATCH"** ([IACR ePrint](https://eprint.iacr.org/2023/742)); by Manas Wadhwa, Anubhab Baksi and others.

The objective is to find SBox for various cryptographic operations as specified by a set of given constraints, using the [Simple Theorem Prover (STP)](https://stp.github.io/) solver. On running the command, one SBox will be found satisfying the required criteria mentioned in the configuration file. 

## Feature and Option
To find an SBox $S$, the following parameters/options are supported:

* `size`: Size of $S$ ($n$). Expects an integer $ 3 \leq n$ (may not work efficiently for $n \geq 6$). 
* `fp` (fixed point): When `true`, $S[x] = x$, for some $x$: Accepts Boolean value `true` or `false`. 
* `du` (differential uniformity): Expects values from $2$ (inclusive) to $2^n$ (inclusive)
* `frequency_du` (frequency of differential uniformity): Expects values from $0$ to $2^{n+1}$. 
* `lu` (linear uniformity): Expects values from $-2^{n-1}$ (inclusive) to $2^{n-1}$ (inclusive).
* `frequency_alu` (frequency of absolute linear uniformity): Expects values from $0$ to $2^{2n}$. 
* `bddt` (bad input bad output of DDT): Expects values from $0$ (inclusive) to $n^2$ (inclusive). 
* `dbn` (differential branch number): Expects values from $0$ to $2^n$ (both inclusive). 
* `lbn` (linear branch number): Expects values from $0$ to $2^n$ (both inclusive).
* `solution_fn`: Name of solution file (this file will be generated/overwritten and will contain the SBox in a comma separated decimal format). Default is `final_sol_<timestamp>_<PID>.sbox`. This file contains the final solution as INPUT and OUTPUT. If no sbox is found, OUTPUT will mention VALID and an empty sbox. If a sbox is found, then at the end of the file, VALID will be written along with the exact Sbox as an array of comma separated values.  
* `stpo_fn`: Name of file with the STP solution (this file will be generated/overwritten, not intended for reading by a human). Default is `stp_output_<timestamp>_<PID>.txt`. 
* `is_bct`: Accepts Boolean `true` or `false` depending on whether boomerang connectivity table is required or not. 
* `global_timeout`: Specify the time in seconds, it will wait for finding each sboxe mentioned in the configuration file. If this parameter is specified then it will override the individual timeout option of a particular sbox.
* `is_bijective`: Accepts Boolean `true` or `false` depending on whether the desired SBox is required to be bijective or not. 

## Directory Structure

```
.
├── 4bit-LS
│   ├── dbn_2_lbn_3.txt
│   └── involution_dbl_lbn_at_least_2.txt
├── README.md
├── config.json
├── gen_search_sbox.py
├── sasquatch.log
├── sasquatch_run.py
└── stp_finalsbox.py
```
* Main code for searching for the desired SBox is in [`gen_search_sbox.py`](gen_search_sbox.py).
* Log for every search is maintained in [`sasquatch.log`](sasquatch.log) (created if not existed, appended if exists). In case multiprocessing is activated, locks are implemented to prevent race conditions. 
* Search configuration can be specified in [`config.json`](config.json) (this is read by the tool as default) or in another file with compatible syntax.
* Outcome for $4$-bit SBox with linear structures can be found in [`4bit-LS/`](4bit-LS/) directory, where we list a number of SBoxes in two files (both files are non-exhaustive) as Hexadecimal string format:
   * [`dbn_2_lbn_3.txt`](4bit-LS/dbn_2_lbn_3.txt): Contains $2$ DBN and $3$ LBN SBoxes.
   * [`involution_dbl_lbn_at_least_2.txt`](4bit-LS/involution_dbl_lbn_at_least_2.txt): Contains involutory SBoxes with $\geq 2$ DBN and $\geq 2$ LBN.

## Dependency

* **STP:** Installation instruction for the STP solver can be found [here](https://github.com/stp/stp).
* **Pebble:** Installation instruction can be referred to [here](https://pypi.org/project/Pebble/). 
* Our tool is tested with (Python 3.7.6, STP 2.3.3, Pebble 4.6.3 running on Ubuntu 20.04.4 LTS).

## How-to-run
  
1. Edit (as needed) the parameters in the configuration file [`config.json`](config.json) is used by default) for finding the corresponding SBox. 
2. Enter the command `python3 sasquatch_run.py`. In this case, [`config.json`](config.json) is passed implicitly. The solution file and STP output file with names as provided in the configuration file appended with time and process PID are generated in the same directory. If one wants, the configuration file can be specified as `python3 sasquatch_run.py <configuration file>`. 
3. The final SBox (if found) satisfying the required properties can be found in `<solution_fn>_<timestamp>_<PID>.txt`. 
4. The file `<stpo_fn>_<timestamp>_<PID>.txt` shows the assignment to the variables that satisfy the required constraints. If we find a solution, then after all the assignments, `INVALID` will be written. Else, if no solution is found then `VALID` will be written.   

### Terminal Command
```
$ python3 sasquatch_run.py
```

<!--
### CVC Output (file name)

### Generated SBox (file name)
-->

### Sample Configuration ([`config.json`](config.json))
```
{
   "global_timeout": null,
   "sequential": true,
   "output_dir": null, 
   "debug": true, 
   "my_sbox1": {
      "size": 4,
      "fp": null,
      "du": null,
      "frequency_du": null,
      "alu": {
         "val": 8,
         "exp": "=="
      },
      "frequency_alu": 1,
      "bddt": null,
      "blat": null,
      "dbn": null,
      "lbn": null,
      "bct": false,
      "involution": false,
      "lookup": null,
      "solution_fn": null,
      "time_out": null
   },
   "my_sbox2": {
      "size": 4,
      "fp": null,
      "du": {
         "val": 8,
         "exp": "=="
      },
      "frequency_du": {
         "val": 4,
         "exp": ">="
      },
      "alu": null,
      "frequency_alu": null,
      "bddt": null,
      "blat": null,
      "dbn": null,
      "lbn": null,
      "bct": false,
      "involution": false,
      "lookup": null,
      "solution_fn": null,
      "time_out": null
   }
 }
 ```
### Sample Logging ([`sasquatch.log`](sasquatch.log))
This file records every SBox search input and output files. Locks have been implemented to prevent race conditions in this file, in case multiprocessing is used. 

### Note
* All the options are compulsory, `null` can be specified if no constraint is imposed (e.g., `"lbn": null`).
* In case of conflicting options for parameters, some parameters may be ignored (a warning will be thrown in such a situation). Examples (including, but not limited to): 
   * If `frequency_du` is not `null` then `du` must also not be `null`.
   * If `frequency_alu` is not `null` then `lu` must also not be `null`.
* The option `du` supersedes this option (if `du` is not null then `frequency_du` will be automatically assumed to be at least $1$).
* The option `lu` supersedes this option (if `lu` is not null then `frequency_alu` will be automatically assumed to be at least $1$). 
* There an option to switch off logging all the information in the non-developer mode.

## Known Issue
* Although this may seem counterintuitive, when we specify `QUERY FALSE;` in the CVC file (which is used as the input to STP solver), it will look for all possible values in the search space and if it finds any that satisfies all the assertions then the query is not false. By including the line `Counterexample;` to the CVC file, it shows the particular assignment for which it is not false. Hence, `INVALID` means that the query is not false as we found some set of values that satisfy all the assertions. If we do not find any set of values that satisfy all the assertions then the output will be `VALID` as the query is actually false for any possible set of values. 
* If `INVALID` is not printed, then the search has been inconclusive (most likely the process crashed unexpectedly).
* Larger SBox (size $8$ or more) search generally crashes. One option could be to increase `ulimit` in Linux (specially when an error like "`ERROR: memory manager can't handle the load.`" is displayed).
