NAME

    network_crawler -- networks' international calling costs web crawler

INSTALLATION

    cd network_crawler
    python setup.py install

SYNOPSIS

    network_crawler --data [file] [-h] [--json] [--log-dir [dir]] [--log-level [level]] [-o [of]] [-q] [-v]

    (See the OPTIONS section for alternate option syntax with long option names.)

DESCRIPTION

    network_crawler is a simple web crawler for networks’ international calling costs.

    The script queries a network’s website directly to obtain a list of calling costs.
    These costs are: based on country zones, per minute and only related to calls to
    a foreign country from the UK.

    network_crawler requires a JSON file containing:
        - operator name
        - operator URL
        - list of country zones
        - list of actions for the Selenium driver
        - load time: the maximum amount of time to wait for a page element to get loaded
        - sleep time: the amount of time of sleeping after each action

    A log file can be used to track the crawling process, if not supplied then all the
    messages will be printed to STDOUT (default).

OPTIONS

    --data			        File containing the operator URL,
				            the list of country zones and the file
				            structure for the Selenium driver.

    -h, --help       		Show this help message and exit.

    --json           		Write the results using a JSON format.

    --log-dir dir    		Write log file (.log) to a specific
                            folder (default /tmp).

    --log-level level		Log levels: unset, debug, info, warning,
                            error, critical (default info).

    -o of, --out of  		Write output to file (default STDOUT).

    -q, --quiet      		Run in quiet mode.

    -v, --version    		Show version number.

EXAMPLES

    Run with logging at debug level, printing to STDOUT:

        network_crawler --data operators.json -l "debug"

    Print the output to STDOUT in JSON format:

        network_crawler --data operators.json --json

    Print the output to a file in JSON format:

        network_crawler --data operators.json --json --out file.json

    Log the process to a specific directory:

        network_crawler --data operators.json --lod-dir /var/log/

    Dry-run mode, only prints the logging messages:

        network_crawler --data operators.json -q

REQUIREMENTS

    Python modules: argparse, coloredlogs, chromedriver, selenium

EXIT CODES

    0 - Success
    1 - Failure

TESTS

    python tests/test_operator_web_site.py

    or

    py.test

AUTHOR

    Luigi Riefolo <luigi.riefolo@gmail.com>

LICENSE

    The MIT License (MIT).

VERSION

    network_crawler 1.0
