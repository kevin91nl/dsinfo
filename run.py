import importlib
import logging
import multiprocessing
import subprocess
import os
import yaml

from argparse import ArgumentParser

from utilities.jobs import StreamingJob, SignalJob


def run_job(job_module, job_class_name, **used_kwargs):
    class_ = getattr(job_module, job_class_name)
    class_(**used_kwargs).__call__()


def create_job(job_module, job_class_name, job_config, global_config):
    if 'kwargs' in job_config:
        kwargs = job_config['kwargs']
    else:
        kwargs = {}
    if 'path' in kwargs:
        kwargs['path'] = os.path.join(global_config.path, kwargs['path'])
    logger.info(kwargs)
    class_ = getattr(job_module, job_class_name)
    if class_.is_streaming():
        stream_process = multiprocessing.Process(target=class_(**kwargs).__call__)
        out_job = StreamingJob(
            target=stream_process
        )
        out_job.start()
    else:
        out_job = SignalJob(
            target=run_job,
            args=(job_module, job_class_name),
            kwargs=kwargs
        )
        out_job.start()
    return out_job


if __name__ == '__main__':
    parser = ArgumentParser('The DSInfo (DataScience Info) Engine.')
    parser.add_argument('--path', help='The path to use for storage.', type=str, default='data')
    parsed_args = parser.parse_args()

    logger = logging.getLogger()
    logging.basicConfig(
        format='%(asctime)16s %(threadName)12s %(levelname)8s: %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S',
        level=logging.INFO
    )
    logger.info('Starting jobs...')

    with open('config.yaml', 'r') as in_file:
        config = yaml.load(in_file)

    assert 'sources' in config and type(config['sources']) == list
    parsers = config['sources']

    # Initialize the path when it does not exist
    if not os.path.exists(parsed_args.path):
        os.makedirs(parsed_args.path)

    # First, start the Flask server
    logger.info('Starting webserver...')
    process = subprocess.Popen(['python3', os.path.join('webapp', 'webserver.py')])

    # Then, start the analyser
    logger.info('Starting analyser...')
    process_analyser = subprocess.Popen(['python3', 'analyse.py', '--path', parsed_args.path])

    # Create processes for the jobs
    jobs = []
    for parser in parsers:
        assert '.' in parser['parser']
        module_name = '.'.join(parser['parser'].split('.')[:-1])
        class_name = parser['parser'].split('.')[-1]
        logger.info('Loading module {}...'.format(module_name))
        module = importlib.import_module(module_name)
        logger.info('Loading class {} from module {}...'.format(class_name, module_name))
        job = create_job(module, class_name, parser, parsed_args)
        jobs.append(job)

    try:
        while True:
            # Wait until keyboard interrupt
            continue
    except KeyboardInterrupt:
        logger.info('Interrupted!')
        logger.info('Signaling thread pool for termination...')
        for job in jobs:
            job.stop()
        logger.info('Terminating webserver...')
        process.terminate()
        logger.info('Terminating analyser...')
        process_analyser.terminate()
        logger.info('Waiting for jobs...')
        for job in jobs:
            while job.is_alive():
                # Wait for all threads to terminate
                continue
        logger.info('Finished!')
