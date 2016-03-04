from selenium import webdriver
from pytest import fixture
import logging
import json

# By convention these tests won't run by the py.test's default test discovery,
# as the file doesn't start with 'test_'. This is intentional to separate
# the functional from the unit tests. This test expects PhantomJS and a
# running server listening on localhost:8000. PhantomJS comes default on
# Travis-CI. For the other details in running see .travis.yml.

logger = logging.getLogger(__name__)


@fixture(scope='session')
def browser(request):
    driver = webdriver.PhantomJS()
    driver.set_window_size(1120, 550)

    def fin():
        driver.close()
    request.addfinalizer(fin)
    return driver


def test_basic_site(browser):
    """
    Check that our home page is able to fetch all of the statics, along with
    some basic angular functionality checks.
    """
    browser.get('http://localhost:8000/')

    # check that our page's h1 is also the title, which ensures our basic
    # angular functionality is working.
    assert "Identity.UW enables you to..." == browser.title

    # get_log('har') on PhantomJS will get the browser's network traffic.
    log_entries = json.loads(
        browser.get_log('har')[0]['message'])['log']['entries']

    # Check that all of our requests are internal. If we go back and forth
    # between pulling from other CDNs this should come out.
    assert all(['http://localhost' in entry['request']['url']
                for entry in log_entries])

    log_errors = [entry
                  for entry in log_entries
                  if entry['response']['status'] != 200]

    [logger.info('log error: {}'.format(err)) for err in log_errors]
    # Check that none of our errors were 404s (non-200s come in as None so we
    # have to match the text)
    assert all(['Not Found' not in err['response']['statusText']
                for err in log_errors])
    # we should get a not authorized on loginstatus, and it should be our
    # only error
    assert log_errors and all(['/api/loginstatus' in err['request']['url']
                               for err in log_errors])
