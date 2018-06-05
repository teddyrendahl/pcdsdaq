import time
import logging

import pytest
from bluesky.plans import scan
from bluesky.plan_stubs import (trigger_and_read,
                                create, read, save, null)
from bluesky.preprocessors import run_decorator, run_wrapper

from pcdsdaq.plans import (daq_wrapper, daq_decorator, calib_cycle,
                           calib_at_step)

logger = logging.getLogger(__name__)


def test_daq_fixtures(daq, RE):
    """
    Verify that the test setup looks correct
    """
    logger.debug('test_daq_fixtures')
    assert daq._RE == RE


@pytest.mark.timeout(10)
def test_flyer_scan(daq, RE, sig):
    """
    We expect that the daq object is usable in a bluesky plan with the
    decorator
    """
    logger.debug('test_flyer_scan')

    @daq_decorator()
    @run_decorator()
    def plan(reader):
        yield from null()
        for i in range(10):
            assert daq.state == 'Running'
            yield from trigger_and_read([reader])
        assert daq.state == 'Running'
        yield from null()

    RE(plan(sig))
    assert daq.state == 'Configured'


@pytest.mark.timeout(10)
def test_post_daq_RE(daq, RE, sig):
    """
    We expect that the RE will be clean after running with the daq
    """
    logger.debug('test_post_daq_RE')

    @run_decorator()
    def plan(reader, expected):
        for i in range(10):
            yield from create()
            assert daq.state == expected
            yield from read(reader)
            yield from save()

    RE(daq_wrapper(plan(sig, 'Running')))
    RE(plan(sig, 'Configured'))
    assert daq.state == 'Configured'
