#!/usr/bin/env python3

import sys
from csv import reader, Sniffer
import cchardet as chardet
import locale
from datetime import datetime
from zoneinfo import ZoneInfo

if len(sys.argv) != 2:
    print('Arguments not matching! Usage:')
    print(sys.argv[0] + ' <csv_input_file>')
    sys.exit(1)

csv_file = sys.argv[1]

metric_mapping_config = {
    "2": {
        "metric": "collector_celsius"
    },
    "3": {
        "metric": "reservoir_celsius",
        "labels": {
            "layer": "top 1"
        }
    },
    "4": {
        "metric": "reservoir_celsius",
        "labels": {
            "layer": "bottom 2"
        }
    },
    "5": {
        "metric": "hot_water_circulation_celsius",
        "labels": {
            "direction": "flow"
        }
    },
    "6": {
        "metric": "solar_circulation_celsius",
        "labels": {
            "direction": "return"
        }
    },
    "8": {
        "metric": "solar_circulation_celsius",
        "labels": {
            "direction": "flow"
        }
    },
    "9": {
        "metric": "reservoir_celsius",
        "labels": {
            "layer": "top 2"
        }
    },
    "10": {
        "metric": "reservoir_celsius",
        "labels": {
            "layer": "middle 1"
        }
    },
    "11": {
        "metric": "reservoir_celsius",
        "labels": {
            "layer": "bottom 1"
        }
    },
    "12": {
        "metric": "boiler_circulation_celsius",
        "labels": {
            "direction": "flow"
        }
    },
    "13": {
        "metric": "outside_celsius"
    },
    "14": {
        "metric": "heating_circulation_celsius",
        "labels": {
            "direction": "flow"
        }
    },
    "15": {
        "metric": "reservoir_celsius",
        "labels": {
            "layer": "middle 2"
        }
    },
    "17": {
        "metric": "solar_circulation_flow_rate_lperh"
    },
    "18": {
        "metric": "boiler_circulation_flow_rate_lperh"
    },
    "19": {
        "metric": "boiler_circulation_celsius",
        "labels": {
            "direction": "return"
        }
    },
    "20": {
        "metric": "solar_power_kW"
    },
    "21": {
        "metric": "solar_energy_kWh_total"
    },
    "22": {
        "metric": "boiler_power_kW"
    },
    "23": {
        "metric": "boiler_energy_kWh_total"
    },

    "24": {
        "metric": "hot_water_circulation_pump_state"
    },
    "25": {
        "metric": "reservoir_charging_state",
        "labels": {
            "layer": "top"
        }
    },
    "26": {
        "metric": "reservoir_charging_state",
        "labels": {
            "layer": "middle"
        }
    },
    "27": {
        "metric": "solar_circulation_pump_state"
    },
    "29": {
        "metric": "boiler_circulation_pump_state"
    },
    "30": {
        "metric": "heating_circulation_pump_state"
    },
    "31": {
        "metric": "heating_circulation_mixer_state"
    },
    "32": {
        "metric": "heating_circulation_mixer_2_state"
    },
    "34": {
        "metric": "boiler_valve_state"
    },
    "39": {
        "metric": "solar_circulation_pump_2_state"
    }
}

common_labels = {
    'instance': 'cmi',
    'cmi_id': 'some cmi id'
}


def determine_file_encoding(filename):
    file = open(filename, "rb")

    encoded_bytes = file.read(8192)

    detection = chardet.detect(encoded_bytes)
    # print(detection)
    detected_encoding = detection["encoding"]
    # confidence = detection["confidence"]

    file.close()

    return detected_encoding


encoding = determine_file_encoding(csv_file)
locale.setlocale(locale.LC_ALL, 'de_DE.UTF-8')

# open file in read mode
with open(csv_file, 'r', encoding=encoding) as read_obj:
    dialect = Sniffer().sniff(read_obj.read(8192))

    reader_obj = reader(read_obj, dialect)

    # Create reader object by passing the file
    # object to reader method

    for mapping_key in metric_mapping_config.keys():
        # start in file beginning
        read_obj.seek(0)
        heading = next(reader_obj)

        index = int(mapping_key)

        mapping_config = metric_mapping_config[mapping_key]
        labelnames = list(common_labels.keys())
        labels = common_labels

        if 'labels' in mapping_config:
            labelnames = labelnames + list(mapping_config['labels'].keys())
            labels = labels | mapping_config['labels']

        # print(labelnames)
        # print(labels)

        label_strings = []
        for key2, value in labels.items():
            label_strings.append(key2 + '="' + value + '"')

        complete_label_string = ','.join(label_strings).join(['{', '}'])
        metric_name = mapping_config['metric']

        # Iterate over each row in the csv file
        # using reader object
        counter = 0

        print('# Help ' + metric_name + ' ' + heading[index])
        print('# Type ' + metric_name + ' gauge')
        for row in reader_obj:
            counter += 1
            if counter == 3:
                break

            # print(row)
            raw_value = row[index]
            date = row[0]
            time = row[1]

            dt = datetime.fromisoformat(date + ' ' + time).replace(tzinfo=ZoneInfo("Europe/Berlin"))
            ts = str(int(dt.timestamp()))

            # filter empty values
            if len(raw_value) == 0:
                continue

            value = locale.atof(raw_value)

            # filter wrong input
            if value == 9999.9:
                continue

            print(metric_name + complete_label_string + ' ' + str(value) + ' ' + ts)

        break

# print('done')
