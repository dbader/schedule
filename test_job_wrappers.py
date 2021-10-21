import pytest

def test_job_wrappers(script_runner):
    ret = script_runner.run('examples/scheduler_check.py')
    assert ret.success
    assert 'good' in ret.stdout
    assert 'bad' in ret.stdout
    assert ret.stderr == ''
