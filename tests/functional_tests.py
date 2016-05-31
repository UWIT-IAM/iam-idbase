"""
Functional tests using phantom and firefox.

to run:
pip install selenium
py.test tests/functional_tests.py

By convention these tests won't run by the py.test's default test discovery,
as the file doesn't start with 'test_'. This is intentional to separate
the functional from the unit tests. This test expects PhantomJS and a
running server listening on localhost:8000. PhantomJS comes default on
Travis-CI. For the other details in running see .travis.yml.
"""

from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from django.test import override_settings
from pytest import fixture, mark
import logging
import json

logger = logging.getLogger('idbase.' + __name__)


@fixture
def site_root(request, live_server):
    # django live_server always sets DEBUG to False. Override that for test.
    settings_context = override_settings(DEBUG=True)
    settings_context.__enter__()

    def fin():
        settings_context.__exit__(None, None, None)
    request.addfinalizer(fin)
    return live_server.url


@mark.skip(reason='phantomjs is < 2.0 on travis '
                  'and angular 1.5+ doesn\'t seem to work')
def test_basic_site(phantom_browser, site_root):
    """
    Check that our home page is able to fetch all of the statics, along with
    some basic angular functionality checks.
    """
    browser = phantom_browser
    browser.get(site_root)

    # check that our page's h1 is also the title, which ensures our basic
    # angular functionality is working.
    wait_for_title(browser)

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


def test_error_message(firefox_browser, site_root):
    """
    Check that the error box shows when activated.
    """
    browser = firefox_browser
    browser.get(site_root)
    wait_for_title(browser)
    body = browser.find_element_by_xpath('/html/body').text
    assert "We are experiencing technical issues" not in body
    browser.find_element_by_id('badButton').click()
    body = browser.find_element_by_xpath('/html/body').text
    assert "We are experiencing technical issues" in body


def test_login_status(firefox_browser, site_root):
    """
    Check that a login action shows the user their status.
    """
    browser = firefox_browser
    browser.get(site_root + '/logout')
    wait_for_title(browser)
    body = browser.find_element_by_xpath('/html/body').text
    assert "javerage" not in body
    browser.find_element_by_id('loginLink').click()
    body = browser.find_element_by_xpath('/html/body').text
    assert "javerage" in body


def test_login_non_uw(firefox_browser, site_root, settings):
    settings.MOCK_LOGIN_USER = 'joe@example.com'
    browser = firefox_browser
    browser.get(site_root + '/logout')
    wait_for_title(browser)
    browser.get(site_root + '/secure')
    wait_for_title(browser,
                   title_substring="You're still logged in as a non-UW user.")


def test_login_no_remote_user(firefox_browser, site_root, settings):
    settings.MOCK_LOGIN_USER = ''
    browser = firefox_browser
    browser.get(site_root + '/logout')
    wait_for_title(browser)
    browser.get(site_root + '/secure')
    wait_for_title(browser,
                   title_substring="Error logging in.")
    body = browser.find_element_by_xpath('/html/body').text
    assert "We are experiencing technical issues" in body


def wait_for_title(browser, title_substring="Identity.UW enables you to..."):
    try:
        WebDriverWait(browser, 5).until(EC.title_contains(title_substring))
    finally:
        logger.debug('Your title was: {}'.format(browser.title))


@fixture(scope='session')
def phantom_browser(request):
    driver = webdriver.PhantomJS()
    driver.set_window_size(1120, 550)

    def fin():
        driver.close()
    request.addfinalizer(fin)
    return driver


@fixture(scope='session')
def firefox_browser(request):
    driver = webdriver.Firefox()
    driver.set_window_size(1120, 550)

    def fin():
        driver.close()
    request.addfinalizer(fin)
    return driver
