# cmi-openmetrics

Create an [OpenMetrics text file](https://github.com/OpenObservability/OpenMetrics/blob/main/specification/OpenMetrics.md#text-format)
from a CSV file that was exportet from TA's [Control and Monitoring Interface (C.M.I)](https://www.ta.co.at/x2-bedienung-schnittstellen/cmi/).
The OpenMetrics data can then be [backfilled into Prometheus](https://prometheus.io/docs/prometheus/latest/storage/#backfilling-from-openmetrics-format).

## Backfilling procedure

### On a Windows machine

* use TA's [Winsol](https://www.ta.co.at/en/downloads/software/) to extract historic data from C.M.I. data logger
* export into csv file using TA's [Winsol](https://www.ta.co.at/en/downloads/software/)

### On your local workstation

* run C.M.I. CSV to OpenMetrics conversion, e.g. `./cmi-openmetrics.py <winsol_export.csv> <cmi_id> <job_name> > backfill.om`
* Linux optional, depending on the number of metrics and history, increase number of open files limit for the current session
  `ulimit -n 4096 # increase limit for number of open files`
* install Prometheus (including `promtool`)
* run Prometheus backfill command, e.g. `promtool tsdb create-blocks-from openmetrics backfill.om ./data --max-block-duration 96h`
* copy backfilled data to target machine running Prometheus, e.g. `scp -rp ./data <target_machine>:~/`

### On the target machine running Prometheus

* make a backup of current prometheus data, [take a snapshot](https://prometheus.io/docs/prometheus/latest/querying/api/#snapshot)
* apply corresponding permissions, e.g. running Prometheus via docker with a mounted volume `sudo chown -R nobody.nogroup ~/data/`
* make sure Prometheus runs with the `--storage.tsdb.allow-overlapping-blocks` command line flag
* move backfilled data into Prometheus data folder, e.g. running Prometheus via docker with a mounted volume `sudo mv ~/data/* ~/prometheus/prometheus/`

## Other Links

* [Technische Alternative (TA) website](https://www.ta.co.at/)
* [C.M.I. wiki entry](https://wiki.ta.co.at/C.M.I.)
* https://prometheus.io/docs/prometheus/latest/storage/#backfilling-from-openmetrics-format
