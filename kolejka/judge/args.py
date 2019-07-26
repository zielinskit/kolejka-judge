# vim:ts=4:sts=4:sw=4:expandtab
import argparse
import glob
import logging
import pathlib
import sys
assert sys.version_info >= (3, 6)


from kolejka.judge import ctxyaml


__all__ = [ 'parse_args', 'write_results' ]
def __dir__():
    return __all__


DEFAULT_TESTS_FILE='tests/tests.yaml'
DEFAULT_SOLUTION_GLOB='solution/*'
DEFAULT_ENVIRONMENT='local'
DEFAULT_JUDGE_DESCRIPTION='SATORI KOLEJKA judge'


def known_systems():
    from kolejka.judge.systems import LocalSystem, PsutilSystem, ObserverSystem
    known_systems = {
        'local': LocalSystem,
        'psutil': PsutilSystem,
        'observer': ObserverSystem,
        #'kolejka' : KolejkaTask,
    }
    return known_systems


def argument_parser(description=DEFAULT_JUDGE_DESCRIPTION):
    parser = argparse.ArgumentParser(description=description)
    parser.add_argument('-v', '--verbose', action='store_true', default=False, help='show more info')
    parser.add_argument('-d', '--debug', action='store_true', default=False, help='show debug info')
    envs = known_systems()
    for env_id, env_cls in envs.items():
        parser.add_argument(
            '--{}'.format(env_id),
            dest='system',
            action='store_const',
            const=env_id,
            default=DEFAULT_ENVIRONMENT,
        )
    if pathlib.Path(DEFAULT_TESTS_FILE).is_file():
        parser.add_argument('--tests', default=DEFAULT_TESTS_FILE, type=str, help='Tests description')
    else:
        parser.add_argument('--tests', required=True, type=str, help='Tests description')
    parser.add_argument('--test', type=str, help='Test to run')
    solution = list(glob.glob(DEFAULT_SOLUTION_GLOB))
    if len(solution) == 1:
        parser.add_argument('--solution', default=solution[0], type=str, help='Solution file')
    else:
        parser.add_argument('--solution', required=True, type=str, help='Solution file')
    parser.add_argument('--output-dir', default='results', type=str, help='Output directory')
    parser.add_argument('--results', default='results/results.yaml', type=str, help='Results file')
    return parser


def write_results(args, results):
    args.results.parent.mkdir(parents=True, exist_ok=True)
    with args.results.open('w') as results_file:
        ctxyaml.dump(results, results_file)


def parse_args(args=None, namespace=None, description=DEFAULT_JUDGE_DESCRIPTION):
    envs = known_systems()
    parser = argument_parser(description=description)
    args = parser.parse_args(args=args, namespace=namespace)
    level=logging.WARNING
    if args.verbose:
        level=logging.INFO
    if args.debug:
        level=logging.DEBUG
    logging.basicConfig(level=level)

    if not pathlib.Path(args.tests).is_file():
        parser.error('TESTS file {} does not exist'.format(args.tests))

    try:
        import kolejka.judge.ctxyaml as ctxyaml
        with open(args.tests) as tests_file:
            tests = ctxyaml.load(tests_file)
    except:
        parser.error('Failed to load TESTS file {}'.format(args.tests))

    try:
        if args.test is not None:
            tests = {
                args.test : tests[args.test]
            }
    except:
        parser.error('TEST {} does not exist in TESTS file {}'.format(args.test, args.tests))
    
    if not pathlib.Path(args.solution).is_file():
        parser.error('SOLUTION file {} does not exist'.format(args.solution))

    if not args.system in envs:
        parser.error('Execution system {} does not exist'.format(args.system))

    pathlib.Path(args.output_dir).mkdir(parents=True, exist_ok=True)
    if not pathlib.Path(args.output_dir).is_dir():
        parser.error('Output directory {} is not a directory'.format(args.output_dir))

    solution = pathlib.Path(args.solution).resolve()
    results = pathlib.Path(args.results).resolve()
    system = envs[args.system]
    output_dir = pathlib.Path(args.output_dir).resolve()


    return argparse.Namespace(tests=tests, solution=solution, results=results, system=system, output_dir=output_dir)