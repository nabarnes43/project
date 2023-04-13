from flaskr import create_app
from .backend import Backend
from unittest.mock import patch
from unittest.mock import MagicMock
from unittest import mock
import pytest
import io


# See https://flask.palletsprojects.com/en/2.2.x/testing/
# for more info on testing
@pytest.fixture
def app():
    app = create_app({
        'TESTING': True,
    })
    return app


@pytest.fixture
def client(app):
    return app.test_client()


def test_home_page(client):
    """
    Test that the home page loads successfully and contains the expected content.
    """
    resp = client.get("/")
    assert resp.status_code == 200
    assert b"<title>People To Know In Computer Science</title>" in resp.data
    assert b"This wiki is dedicated to providing information and insight into the lives and works of the most influential and notable people in the field of computer science. From pioneers of computer programming and artificial intelligence to modern-day innovators in cybersecurity and machine learning, this wiki seeks to showcase the incredible contributions made by these individuals to the world of computer science." in resp.data


def skip_test_about_page(client, monkeypatch):

    def mock_get_image(self, name):
        return b''

    monkeypatch.setattr(Backend, 'get_image', mock_get_image)

    response = client.get("/about")
    assert response.status_code == 200
    assert b"<h1>About This Wiki</h1>" in response.data
    assert b"<h3>Your Authors</h3>" in response.data
    assert b'' in response.data


def test_signup_page(client):
    """
    Test that the signup page loads successfully and contains the expected content.
    """
    resp = client.get('/signup')
    assert resp.status_code == 200
    assert b'<h1>Sign Up</h1>' in resp.data
    assert b'<input type="text" name= "Username" placeholder="Enter a username"/>' in resp.data
    assert b'<input type="text" name="Password" placeholder="Enter a password"/>' in resp.data
    assert b'<input type="submit" value="Signup"/>' in resp.data


def skip_test_create_account_succesful_page(client):
    """
    GIVEN a Flask application
    WHEN the '/createaccount' page is posted with username and password
    THEN check that the response is successful and the username is displayed
    """

    response = client.post('/createaccount',
                           data=dict(Username='testuser',
                                     Password='testpassword'))
    assert response.status_code == 200
    assert b'testuser' in response.data


def test_create_account_missing_fields(client):
    """
    GIVEN a Flask application
    WHEN the '/createaccount' page is posted with missing username or password fields
    THEN check that the response is successful and the appropriate error message is displayed
    """
    # test missing username field
    response = client.post('/createaccount',
                           data=dict(Username='', Password='testpassword'))
    assert response.status_code == 200
    assert b'Please enter a username and password.' in response.data

    # test missing password field
    response = client.post('/createaccount',
                           data=dict(Username='testuser', Password=''))
    assert response.status_code == 200
    assert b'Please enter a username and password.' in response.data

    # test missing username and password fields
    response = client.post('/createaccount',
                           data=dict(Username='', Password=''))
    assert response.status_code == 200
    assert b'Please enter a username and password.' in response.data


def test_create_account_get_page(client):
    """
    GIVEN a Flask application
    WHEN the '/createaccount' page is accessed with GET method
    THEN check that the response is successful and the appropriate error message is displayed
    """
    response = client.get('/createaccount')
    assert response.status_code == 200
    assert b'Please go back and use the form!' in response.data


def test_create_account_exception(client, monkeypatch):
    """
    GIVEN a Flask application and a monkeypatched Backend class
    WHEN the '/createaccount' page is posted with username and password
    THEN check that the response is successful and the appropriate error message is displayed
    """

    def mock_sign_up(self, username, password):
        raise Exception('Test exception')

    monkeypatch.setattr(Backend, 'sign_up', mock_sign_up)

    response = client.post('/createaccount',
                           data=dict(Username='testuser',
                                     Password='testpassword'))

    assert response.status_code == 200
    assert b'Account creation failed: Test exception' in response.data


def test_pages_list(client):
    '''
    Test that it displays all the pagas available for view on the wiki.
    '''
    resp = client.get("/pages")
    assert resp.status_code == 200
    assert b'Pages contained in this Wiki' in resp.data


def test_specific_page(client):
    '''
    Test that specific page can be called to display.
    '''
    resp = client.get("/pages/page_test")
    assert resp.status_code == 200
    assert b'page_test' in resp.data


@patch("flaskr.backend.Backend.upload", return_value=b"upload sucessful")
@patch("flask_login.utils._get_user", return_value=MagicMock())
def test_upload_page(mock_upload, mock_logged_in, client):
    '''
    Test that the upload page displays correctly when called.
    '''
    resp = client.get("/upload")

    assert resp.status_code == 200
    assert b'Upload a doc to the Wiki' in resp.data


#Testing that users are seeing the correct login page
def test_login_page(client):
    resp = client.get('/login')
    assert resp.status_code == 200
    assert b'<h1>Sign In</h1>' in resp.data
    assert b'Username' in resp.data
    assert b'Password' in resp.data
    assert b'value="Submit"' in resp.data


#Testing that users see the correct page when wrong username is entered
def test_login_wrong_username(client, monkeypatch):

    def mock_sign_in(self, username, password):
        return "Username not found"

    monkeypatch.setattr(Backend, 'sign_in', mock_sign_in)
    resp = client.post('/login',
                       data={
                           'username': 'sdf',
                           'password': 'testing123',
                       })
    assert resp.status_code == 200
    assert b'The username is incorrect' in resp.data


#Testing that users are sent to the right page when the wrong password is entered
def test_login_wrong_password(client, monkeypatch):

    def mock_sign_in(self, username, password):
        return 'Incorrect Password'

    monkeypatch.setattr(Backend, 'sign_in', mock_sign_in)
    resp = client.post('/login',
                       data={
                           'username': 'Dimitripl5',
                           'password': 'testing76576',
                       })
    assert resp.status_code == 200
    assert b'An incorrect password was entered' in resp.data


#Testing that users are able to login and logout successfully
def test_login_and_logout_successful(client, monkeypatch):

    def mock_sign_in(self, username, password):
        return 'Sign In Successful'

    monkeypatch.setattr(Backend, 'sign_in', mock_sign_in)
    resp = client.post('/login',
                       data=dict(
                           username='Dimitripl5',
                           password='testing123',
                       ))
    assert resp.status_code == 200
    assert b'Welcome Dimitripl5' in resp.data
    assert b'Log Out' in resp.data
    #Test logout
    resp = client.get("/logout")
    assert b'Log In' in resp.data


# Test that page contents in editable text box is displayed when edit is clicked
@patch("flaskr.backend.Backend.get_wiki_page",
       return_value=b"sample page content")
@patch("flask_login.utils._get_user", return_value=MagicMock())
def test_edit(mock_get_wiki_page, mock_logged_in, client):
    # Test edit page
    resp = client.get('/edit/sample page title')
    assert resp.status_code == 200
    assert b'Make your edits' in resp.data
    assert b'sample page title' in resp.data
    assert b'sample page content' in resp.data


# Test edit is saved
@patch("flaskr.backend.Backend.upload", return_value=b"upload sucessful")
@patch("flask_login.utils._get_user", return_value=MagicMock())
def test_save_edit(mock_upload, mock_logged_in, client):
    resp = client.post('/save_edit/sample page',
                       data={'content': 'random data'})
    assert b'Result for editing' in resp.data
    assert b'sample page' in resp.data
