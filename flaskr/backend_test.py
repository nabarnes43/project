from flaskr.backend import Backend
from .search_algo import levenshtein_distance
import unittest
from unittest.mock import MagicMock
from google.cloud import exceptions
from unittest.mock import patch
import pytest


@pytest.fixture
def blob():
    mock_blob = MagicMock()
    return mock_blob


@pytest.fixture
def bucket(blob):
    mock_bucket = MagicMock()
    mock_bucket.get_blob.return_value = blob
    return mock_bucket


@pytest.fixture
def storage_client(bucket):
    mock_client = MagicMock()
    mock_client.bucket.return_value = bucket
    return mock_client


@pytest.fixture
def backend(storage_client):
    real_backend = Backend(storage_client)
    return real_backend


def test_get_wiki_successful(blob, bucket, storage_client, backend):
    """
    Test that getting a wiki page with a valid name returns the expected content.
    """
    # Setup mock objects for the test
    content = "This is a test wiki page."
    storage_client.bucket.return_value = bucket
    bucket.get_blob.return_value = blob
    blob.open.return_value.__enter__.return_value.read.return_value = content

    # Create a backend instance and call the method being tested
    result = backend.get_wiki_page("test_wiki")

    # Check that the expected content is returned
    assert result == content


def test_get_wiki_page_blob_not_found():
    """
    Test that getting a wiki page with an invalid name returns an error message.
    """
    # Setup mock objects for the test
    storage_client = MagicMock()
    bucket = MagicMock()
    bucket.name = 'mock_bucket_name'
    blob = MagicMock()
    blob.name = 'mock_name'
    blob.open.side_effect = exceptions.NotFound('Blob not found')
    bucket.get_blob.return_value = blob
    storage_client.bucket.return_value = bucket

    # Create a backend instance and call the method being tested
    backend = Backend(storage_client)
    wiki_name = 'mock_wiki_name'
    result = backend.get_wiki_page(wiki_name)

    # Check that the expected error message is returned
    assert result == f"Error: Wiki page {wiki_name} not found."


def test_get_wiki_page_error(blob, bucket, storage_client, backend):
    """
    Test that getting a wiki page when there is a network error returns an error message.
    """
    # Setup mock objects for the test
    blob.open.side_effect = Exception("Network error")

    # Create a backend instance and call the method being tested
    page_name = "example_page"
    expected_error_message = 'Error: Network error'
    result = backend.get_wiki_page(page_name)

    # Check that the expected error message is returned
    assert result == expected_error_message


def test_get_all_page_names_success():
    """
    Test that getting all the wiki page names returns the expected list of names.
    """
    # Setup mock objects for the test
    storage_client = MagicMock()
    blob1 = MagicMock()
    blob2 = MagicMock()
    blob3 = MagicMock()
    blob1.name = "blob1"
    blob2.name = "blob2"
    blob3.name = "blob3"
    storage_client.list_blobs.return_value = [blob1, blob2, blob3]

    # Create a backend instance and call the method being tested
    backend = Backend(storage_client)
    expected_result = ["blob1", "blob2", "blob3"]
    result = backend.get_all_page_names()

    # Check that the expected list of names is returned
    assert result == expected_result


def test_get_all_page_names_not_found():
    """
    Test that getting all the wiki page names when there are no pages in the bucket returns an error message.
    """
    # Setup mock objects for the test
    storage_client = MagicMock()
    storage_client.list_blobs.return_value = []

    # Create a backend instance and call the method being tested
    backend = Backend(storage_client)
    expected_result = "Error: No pages found in bucket."
    result = backend.get_all_page_names()

    # Check that the expected error message is returned
    assert result == expected_result


# def test_get_all_page_names_error():
#     """
#     Test that getting all the wiki page names when there is a network error returns an error message.
#     """
#     # Create a mock storage client that raises an exception when listing blobs
#     storage_client = MagicMock()
#     storage_client.list_blobs.side_effect = Exception("Error")

#     # Create a backend instance with the mock storage client
#     backend = Backend(storage_client)

#     # Define the expected error message to be returned
#     expected_error_message = 'Network error: Network error'

#     # Call the get_all_page_names method and verify that it returns the expected error message
#     result = backend.get_all_page_names()
#     assert result == expected_error_message


def test_upload_existing_page():
    '''
    Test that you cannot upload a page when it already exists
    '''

    blob = MagicMock()
    blob.name = 'mock_name'
    storage_client = MagicMock()
    storage_client.list_blobs.return_value = [blob]

    backend = Backend(storage_client)
    upload_result = backend.upload('random stuff', 'mock_name')

    assert upload_result == 'Upload failed. You cannot overrite an existing page'


def test_upload_no_page_name():
    '''
    Test error message displayed if no page name is provided.
    '''
    backend = Backend()
    upload_result = backend.upload('random stuff', '')
    assert upload_result == 'Please provide the name of the page.'


def test_upload_no_file():
    '''
    Test error message displayed if no data for the page is provided.
    '''
    backend = Backend()
    upload_result = backend.upload(b'', 'mock_name')
    assert upload_result == 'Please upload a file.'


def test_successful_upload():
    '''
    Test successful upload.
    '''
    storage_client = MagicMock()
    blob = MagicMock()
    storage_client.list_blobs.return_value = [blob]

    backend = Backend(storage_client)
    upload_result = backend.upload('random stuff', 'mock_name')
    assert 'uploaded to Wiki.' in upload_result


def test_upload_to_empty_database():
    '''
    Test that uploads are still possible even if database was previously empty.
    '''
    storage_client = MagicMock()
    storage_client.list_blobs.return_value = []

    backend = Backend(storage_client)
    upload_result = backend.upload('random stuff', 'mock_name')
    assert 'uploaded to Wiki.' in upload_result


def test_successful_sign_up():
    '''
    Test that sign up is successful if it is a new user
    '''
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
    '''
    Test that sign up is unsuccessful if it is not a new user
    '''
    blob1 = MagicMock()
    blob2 = MagicMock()
    blob1.name = 'Mary'
    blob2.name = 'Nkata'
    storage_client = MagicMock()
    storage_client.list_blobs.return_value = [blob1, blob2]

    backend = Backend(storage_client)
    sign_up_result = backend.sign_up('Mary', 'no password')

    assert 'already exists in the database' in sign_up_result


#Testing that wrong usernames are found and that "Username not found" is returned
def test_no_username_sign_in():
    blob1 = MagicMock()
    blob1.name = 'randomuser3456'
    storage_client = MagicMock()
    storage_client.list_blobs.return_value = [blob1]

    backend = Backend(storage_client)
    result = backend.sign_in('Mary', 'no_password')

    assert result == False


#Testing that wrong passwords are found and that "incorrect password" is returned
def test_wrong_password_sign_in():
    blob1 = MagicMock()
    blob1.name = 'randomuser3456'
    storage_client = MagicMock()
    storage_client.list_blobs.return_value = [blob1]
    blob1.open.return_value.__enter__.return_value.read.return_value = 'test'

    backend = Backend(storage_client)
    result = backend.sign_in('randomuser3456', 'no_password')

    assert result == False


#Testing that successful sign ins are happening
def test_successful_sign_in():
    blob1 = MagicMock()
    blob1.name = 'dimitripl5'
    storage_client = MagicMock()
    storage_client.list_blobs.return_value = [blob1]
    expected = '44753b854331dc6fbaf617deec25f1aee7d8a25133ca585c70aba5884ef9a1dd'
    blob1.open.return_value.__enter__.return_value.read.return_value = expected

    backend = Backend(storage_client)
    result = backend.sign_in("dimitripl5", "testing123")

    assert result == True


#Testing that the get image function is properly returning
def test_get_image_successful():
    storage_client = MagicMock()
    bucket = MagicMock()
    blob = MagicMock()

    # set up mock objects
    content = "Test image"
    storage_client.bucket.return_value = bucket
    bucket.get_blob.return_value = blob
    blob.name = 'Dimitri.jpg'
    blob.open.return_value.__enter__.return_value.read.return_value = content

    # call the function
    backend = Backend(storage_client)
    result = backend.get_image("Dimitri.jpg")

    # assert the result
    assert result == content


#Testing that pages are properly being deleted
def test_delete_page():
    '''
    Test that pages are properly deleted
    '''
    #Setting up mock objects
    blob1 = MagicMock()
    blob1.name = 'testPage'
    storage_client = MagicMock()
    storage_client.list_blobs.return_value = [blob1]

    #Deleting the testPage
    backend = Backend(storage_client)
    result = backend.delete_page('testPage')

    #Asserting that the page was deleted
    assert result == True

    #Trying to delete a page that doesn't exist
    result2 = backend.delete_page('randompage565')

    #Asserting that false was returned ("Page not found")
    assert result2 == False


def test_search_pages_result():
    """
    Tests that the search_pages function returns the expected page titles in the correct order.

    Uses a MagicMock object to mock the WikiSearcher and StorageClient classes and configures the
    mock object to return expected values. Then calls the search_pages function with a search term
    and relevance score, and asserts that the returned page titles match the expected page titles
    in the correct order.
    """
    # Create a MagicMock object to mock the WikiSearcher class
    wiki_searcher = MagicMock()
    storage_client = MagicMock()

    # Configure the mock object to return the expected values
    wiki_searcher.get_all_page_names.return_value = [
        'Cat', 'Dog', 'Bird', 'Fish'
    ]
    wiki_searcher.get_wiki_page.side_effect = lambda x: {
        'Cat':
            'A cat is a domesticated carnivorous mammal',
        'Dog':
            'A dog is a domesticated carnivorous mammal',
        'Bird':
            'Birds, also known as Aves, are a group of warm-blooded vertebrates',
        'Fish':
            'Fish are aquatic animals that breathe through gills'
    }.get(x)

    backend = Backend(storage_client)

    # Call the search_pages function with the mock object
    search_content = 'cat'
    relevance_score = 0.8955
    page_titles = backend.search_pages(search_content, relevance_score,
                                       wiki_searcher)

    # Assert that the expected page titles are returned in the correct order
    expected_page_titles = ['Cat']
    assert page_titles == expected_page_titles


def test_search_pages_no_result():
    """
    Test that the search_pages function returns the expected page titles for no result.
    
    This function uses a MagicMock object to mock the WikiSearcher and StorageClient classes and
    configures the mock object to return expected values. It then calls the search_pages function with
    a search term and relevance score, and asserts that the returned page titles match the expected page
    titles in the correct order.
    """
    # Create a MagicMock object to mock the WikiSearcher class.
    wiki_searcher = MagicMock()
    storage_client = MagicMock()

    # Configure the mock object to return the expected values.
    wiki_searcher.get_all_page_names.return_value = [
        'Cat', 'Dog', 'Bird', 'Fish'
    ]

    # Set up a side effect for the `get_wiki_page` method that returns a dictionary
    # of page content for the given page names.
    wiki_searcher.get_wiki_page.side_effect = lambda x: {
        'Cat':
            'A cat is a domesticated carnivorous mammal',
        'Dog':
            'A dog is a domesticated carnivorous mammal',
        'Bird':
            'Birds, also known as Aves, are a group of warm-blooded vertebrates',
        'Fish':
            'Fish are aquatic animals that breathe through gills'
    }.get(x)

    backend = Backend(storage_client)

    # Call the search_pages function with the mock object.
    search_content = 'happy'
    relevance_score = 0.8955
    page_titles = backend.search_pages(wiki_searcher, search_content,
                                       relevance_score)

    # Assert that the expected page titles are returned in the correct order.
    expected_page_titles = []

    # Check if the page titles returned by the search_pages method match the expected page titles.
    assert page_titles == expected_page_titles


def test_search_pages_result_order():
    '''
        This function tests that the search_pages function returns the expected page titles
        in the correct order. It uses a MagicMock object to mock the WikiSearcher and StorageClient 
        classes and configures the mock object to return expected values. It then calls the search_pages 
        function with a search term and relevance score, and asserts that the returned page titles 
        match the expected page titles in the correct order.
        '''
    # create a MagicMock object to mock the WikiSearcher class
    wiki_searcher = MagicMock()
    storage_client = MagicMock()

    # configure the mock object to return the expected values
    wiki_searcher.get_all_page_names.return_value = [
        'Cat11', 'Cat1', 'Cat', 'Cat111'
    ]
    wiki_searcher.get_wiki_page.side_effect = lambda x: {
        'Cat11': 'A cat is a domesticated carnivorous mammal',
        'Cat1': 'A cat is a domesticated carnivorous mammal',
        'Cat': 'A cat is a domesticated carnivorous mammal',
        'Cat111': 'A cat is a domesticated carnivorous mammal',
    }.get(x)

    backend = Backend(storage_client)

    # call the search_pages function with the mock object
    search_content = 'cat'
    relevance_score = 0.8955
    page_titles = backend.search_pages(search_content, relevance_score,
                                       wiki_searcher)

    # assert that the expected page titles are returned in the correct order
    expected_page_titles = ['Cat', 'Cat1', 'Cat11', 'Cat111']

    assert page_titles == expected_page_titles


def test_search_pages_relevance_score():
    '''
    This function tests the relevance score calculation for the search_pages function.
    configures the mock object to return expected values. It then calculates the relevance 
    score for a search term and asserts that the result matches the expected value.
    '''
    storage_client = MagicMock()

    backend = Backend(storage_client)

    search_content = 'cat'
    relevance_score = 1

    page_title = 'Cat'
    page_content = 'A cat is a domesticated carnivorous mammal'

    title_distance = levenshtein_distance(search_content, page_title)
    content_similarity = levenshtein_distance(search_content, page_content)
    relevance_score = 0.7 * content_similarity + 0.3 * title_distance

    # scale relevance score by length of search
    relevance_score /= len(search_content)

    # assert that the expected page titles are returned in the correct order
    expected_relevance_score = .25

    assert relevance_score == expected_relevance_score
