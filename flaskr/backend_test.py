from flaskr.backend import Backend
import unittest 
from unittest.mock import MagicMock
from google.cloud import exceptions
from unittest.mock import patch

# TODO(Project 1): Write tests for Backend methods.
def test_get_wiki_successful():
    storage_client = MagicMock()
    bucket = MagicMock()
    blob = MagicMock()

    # set up mock objects
    content = "This is a test wiki page."
    storage_client.bucket.return_value = bucket
    bucket.blob.return_value = blob
    blob.open.return_value.__enter__.return_value.read.return_value = content

    # call the function
    backend = Backend(storage_client)
    result = backend.get_wiki_page("test_wiki")

    # assert the result
    assert result == content

def test_get_wiki_page_blob_not_found():
    storage_client = MagicMock()
    bucket = MagicMock()
    bucket.name = 'mock_bucket_name'
    blob = MagicMock()
    blob.name = 'mock_name'
    blob.open.side_effect = exceptions.NotFound('Blob not found')
    bucket.blob.return_value = blob
    storage_client.bucket.return_value = bucket

    backend = Backend(storage_client)
    wiki_name = 'mock_wiki_name'
    result = backend.get_wiki_page(wiki_name)

    assert result == f"Error: Wiki page {wiki_name} not found."

#def network error exeption next.



def test_upload_existing_page():
    blob = MagicMock()
    blob.name = 'mock_name'
    storage_client = MagicMock()
    storage_client.list_blobs.return_value = [blob]

    backend = Backend(storage_client)
    upload_result = backend.upload('random stuff', 'mock_name')
    assert upload_result == 'Upload failed. You cannot overrite an existing page'

def test_upload_no_page_name():
    backend = Backend()
    upload_result = backend.upload('random stuff', '')
    assert upload_result == 'Please provide the name of the page.'

def test_upload_no_file():
    backend = Backend()
    upload_result = backend.upload(b'', 'mock_name')
    assert upload_result == 'Please upload a file.'


def test_successful_upload():
    storage_client = MagicMock()
    blob = MagicMock()
    storage_client.list_blobs.return_value = [blob]
    
    backend = Backend(storage_client)
    upload_result = backend.upload('random stuff', 'mock_name')
    assert 'uploaded to Wiki.' in upload_result

def test_upload_to_empty_database():
    storage_client = MagicMock()
    storage_client.list_blobs.return_value = []

    backend = Backend(storage_client)
    upload_result = backend.upload('random stuff', 'mock_name')
    assert 'uploaded to Wiki.' in upload_result

def test_successful_sign_up():
    blob1 = MagicMock()
    blob2 = MagicMock()
    blob1.name = 'Mary'
    blob2.name = 'Nkata'
    storage_client = MagicMock()
    storage_client.list_blobs.return_value = [blob1, blob2]

    backend = Backend(storage_client)
    sign_up_result = backend.sign_up('Test user', 'no password')

    assert 'successfully created.' in sign_up_result

def test_unsuccessful_sign_up():
    blob1 = MagicMock()
    blob2 = MagicMock()
    blob1.name = 'Mary'
    blob2.name = 'Nkata'
    storage_client = MagicMock()
    storage_client.list_blobs.return_value = [blob1, blob2]

    backend = Backend(storage_client)
    sign_up_result = backend.sign_up('Mary', 'no password')

    assert 'already exists in the database' in sign_up_result
