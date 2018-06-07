#!/usr/bin/env bash

PYTHON='python -m'

usage () {
	echo "Usage:$0 tests [lib|all]
	-lib <runs library unit tests>
	-all <runs all unit tests>"
	exit 1
}


if [[ $# -eq 0 ]]; then
	usage
fi

lib_tests () {
	echo "Running Utils test"
	$PYTHON lib.test.UtilsTest

	echo "Running Server test"
	$PYTHON lib.test.ServerTest

	return 0
}

run_tests () {
	case $1 in
		lib)
			lib_tests
			;;
		all)
			lib_tests
			;;
		*)
			usage
			;;
	esac

	return 0
}

# With this while, you can go through command line arguments and have many 'key value',
# like './run.sh --user bijan --pass something'
while [[ $# > 0 ]]
do
	key="$1"
	case $key in
		tests)
			TESTPART="$2"
			shift # past argument

			run_tests $TESTPART
			;;
		*)
			usage
		;;
	esac

	shift # past argument

done

