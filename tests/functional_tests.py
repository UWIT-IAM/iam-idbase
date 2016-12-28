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
from selenium.webdriver.common.by import By
from django.test import override_settings
from pytest import fixture
import logging
import json
import os

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


def test_basic_site(browser, site_root):
    """
    Check that our home page is able to fetch all of the statics, along with
    some basic angular functionality checks.
    """
    browser.get(site_root)

    # check that our page's h1 is also the title, which ensures our basic
    # angular functionality is working.
    wait_for_title(browser)

    # get_log('har') on PhantomJS will get the browser's network traffic.
    log_entries = json.loads(
        browser.get_log('har')[0]['message'])['log']['entries']

    # check that all of our requests are internal are internal except fonts
    requested_urls = [entry['request']['url'] for entry in log_entries]

    def url_not_allowed(url):
        allowed_urls = ('http://localhost',
                        'https://fonts.googleapis.com',
                        'https://fonts.gstatic.com')
        return not any(allowed_url in url for allowed_url in allowed_urls)

    assert not [url for url in requested_urls if url_not_allowed(url)]

    # check for any unexpected errors
    def is_unexpected_error(entry):
        return (entry['response']['status'] != 200 and
                not entry['request']['url'].endswith('/api/loginstatus'))

    unexpected_errors = [entry['response']['statusText']
                         for entry in log_entries
                         if is_unexpected_error(entry)]
    assert not unexpected_errors


def test_error_message(browser, site_root):
    """
    Check that the error box shows when activated.
    """
    browser.get(site_root)
    wait_for_title(browser)
    body = browser.find_element_by_xpath('/html/body').text
    assert "We are experiencing technical issues" not in body
    browser.find_element_by_id('badButton').click()
    body = browser.find_element_by_xpath('/html/body').text
    assert "We are experiencing technical issues" in body


def test_login_status(browser, site_root):
    """
    Check that a login action shows the user their status.
    """
    browser.get(site_root + '/logout/?next=/')
    wait_for_title(browser)
    body = browser.find_element_by_xpath('/html/body').text
    assert "javerage" not in body
    browser.find_element_by_id('loginLink').click()
    WebDriverWait(browser, 5).until(EC.text_to_be_present_in_element(
        (By.CLASS_NAME, 'netid-navbar'), 'UW NetID: javerage'))
    body = browser.find_element_by_xpath('/html/body').text
    assert "javerage" in body


def test_login_non_uw(browser, site_root, settings):
    settings.MOCK_LOGIN_USER = 'joe@example.com'
    browser.get(site_root + '/logout/?next=/')
    wait_for_title(browser)
    browser.get(site_root + '/secure')
    wait_for_title(browser,
                   title_substring="You're still logged in as a non-UW user.")


def test_login_no_remote_user(browser, site_root, settings):
    settings.MOCK_LOGIN_USER = ''
    browser.get(site_root + '/logout/?next=/')
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
def browser(request):
    phantom_path = os.environ.get('PHANTOMJS_PATH', None)
    kwargs = dict(executable_path=phantom_path) if phantom_path else {}

    driver = webdriver.PhantomJS(**kwargs)
    driver.set_window_size(1120, 550)

    def fin():
        driver.close()
    request.addfinalizer(fin)
    return driver
