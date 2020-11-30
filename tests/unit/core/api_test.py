# Copyright (c) 2020 Termius Corporation.
import pytest
from mock import Mock, patch

from termius.core.api import API
from termius.core.exceptions import OutdatedVersion


@pytest.fixture()
def patched_api():
    api = API()
    api.logger = Mock()

    return api


@patch('termius.core.api.requests')
def test_outdated_version_login_response(requests_mock, patched_api):
    requests_mock.post.return_value = Mock(status_code=490)

    with pytest.raises(OutdatedVersion):
        patched_api.login('user@example.com', 'pwd')
    assert patched_api.logger.warning.called_once_with('Can not login!')
    assert patched_api.auth is None


@patch('termius.core.api.requests')
def test_outdated_version_get_response(requests_mock, patched_api):
    requests_mock.get.return_value = Mock(status_code=490)

    with pytest.raises(OutdatedVersion):
        patched_api.get('endpoint')


@patch('termius.core.api.requests')
def test_outdated_version_post_response(requests_mock, patched_api):
    requests_mock.post.return_value = Mock(status_code=490)

    with pytest.raises(OutdatedVersion):
        patched_api.post('endpoint', '{"var": "val"}')


@patch('termius.core.api.requests')
def test_outdated_version_put_response(requests_mock, patched_api):
    requests_mock.put.return_value = Mock(status_code=490)

    with pytest.raises(OutdatedVersion):
        patched_api.put('endpoint', '{"var": "val"}')


@patch('termius.core.api.requests')
def test_outdated_version_delete_response(requests_mock, patched_api):
    requests_mock.delete.return_value = Mock(status_code=490)

    with pytest.raises(OutdatedVersion):
        patched_api.delete('endpoint')


@patch('termius.core.api.requests')
def test_failed_login_response(requests_mock, patched_api):
    requests_mock.post.return_value = Mock(status_code=400)

    with pytest.raises(AssertionError):
        patched_api.login('user@example.com', 'pwd')
    assert patched_api.logger.warning.called_once_with('Can not login!')
    assert patched_api.auth is None


@patch('termius.core.api.requests')
def test_failed_get_response(requests_mock, patched_api):
    requests_mock.get.return_value = Mock(status_code=400)

    with pytest.raises(AssertionError):
        patched_api.get('endpoint')


@patch('termius.core.api.requests')
def test_failed_post_response(requests_mock, patched_api):
    requests_mock.post.return_value = Mock(status_code=400)

    with pytest.raises(AssertionError):
        patched_api.post('endpoint', '{"var": "val"}')


@patch('termius.core.api.requests')
def test_failed_put_response(requests_mock, patched_api):
    requests_mock.put.return_value = Mock(status_code=400)

    with pytest.raises(AssertionError):
        patched_api.put('endpoint', '{"var": "val"}')


@patch('termius.core.api.requests')
def test_failed_delete_response(requests_mock, patched_api):
    requests_mock.delete.return_value = Mock(status_code=400)

    with pytest.raises(AssertionError):
        patched_api.delete('endpoint')


@patch('termius.core.api.requests')
def test_success_login_response(requests_mock, patched_api):
    payload = {'token': 'apikey'}
    requests_mock.post.return_value = Mock(
        status_code=200,
        json=Mock(return_value=payload),
        text='{"token": "apikey"}'
    )

    result = patched_api.login('user@example.com', 'pwd')

    assert result is payload
    assert patched_api.auth is not None


@patch('termius.core.api.requests')
def test_success_get_response(requests_mock, patched_api):
    payload = object()
    requests_mock.get.return_value = Mock(
        status_code=200,
        json=Mock(return_value=payload),
        text='response text'
    )

    result = patched_api.get('endpoint')

    assert result is payload


@patch('termius.core.api.requests')
def test_success_post_response(requests_mock, patched_api):
    payload = object()
    requests_mock.post.return_value = Mock(
        status_code=201,
        json=Mock(return_value=payload),
        text='response text'
    )

    result = patched_api.post('endpoint', '{"var": "val"}')

    assert result is payload


@patch('termius.core.api.requests')
def test_success_put_response(requests_mock, patched_api):
    payload = object()
    requests_mock.put.return_value = Mock(
        status_code=200,
        json=Mock(return_value=payload),
        text='response text'
    )

    result = patched_api.put('endpoint', '{"var": "val"}')

    assert result is payload


@patch('termius.core.api.requests')
def test_success_delete_response(requests_mock, patched_api):
    payload = object()
    requests_mock.delete.return_value = Mock(
        status_code=204,
        json=Mock(return_value=payload),
        text='response text'
    )

    result = patched_api.delete('endpoint')

    assert result is payload
