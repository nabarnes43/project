from google.cloud import storage
from google.cloud import exceptions
from .search_algo import levenshtein_distance
import hashlib
import io
from flask import Flask


class Backend:

    def __init__(self, storage_client=storage.Client()):
        self.storage_client = storage_client
        self.pages_bucket = self.storage_client.bucket('sdswiki_contents')
        self.users_bucket = self.storage_client.bucket('sdsusers_passwords')
        self.images_bucket = self.storage_client.bucket('sdsimages')
        self.pages_blobs = self.storage_client.list_blobs('sdswiki_contents')
        self.users_blobs = self.storage_client.list_blobs('sdsusers_passwords')

    def get_wiki_page(self, name):
        """Gets the contents of the specified wiki page.

        Args:
            name: The name of the wiki page.

        Returns:
            The contents of the wiki page.

        Raises:
            exceptions.NotFound: If the specified wiki page is not found.
            Exception: If there is a network error.
        """
        try:
            blob = self.pages_bucket.get_blob(name)
            with blob.open() as f:
                content = f.read()
            return content

        except exceptions.NotFound:
            return f"Error: Wiki page {name} not found."

        except Exception as e:
            return f"Error: {e}"

    def get_all_page_names(self):
        """Gets the names of all wiki pages.

        Returns:
            A list of the names of all wiki pages.

        Raises:
            Exception: If there is a network error.
        """
        try:
            pages_names_list = []
            blobs = self.storage_client.list_blobs('')

            if not self.pages_blobs:
                return "Error: No pages found in bucket."

            for blob in self.pages_blobs:
                pages_names_list.append(blob.name)

            return pages_names_list

        except Exception as e:
            return f"Error: {e}"

    def upload(self, data, destination_blob_name):
        '''
        Uploads page to Wiki server

        Args:
            destination_blob_name = name of page to be uploaded
            data = the information to be displayed on the page

        returns:
            A response message stating if your upload was successful or not.
            If the upload was unsuccessulf, the reason why would be displayed.
        '''
        if data == b'':
            return 'Please upload a file.'
        if destination_blob_name == '':
            return 'Please provide the name of the page.'

        for blob in self.pages_blobs:
            if destination_blob_name == blob.name:
                return 'Upload failed. You cannot overrite an existing page'

        blob = self.pages_bucket.get_blob(destination_blob_name)
        blob.upload_from_string(data)

        return f"{destination_blob_name} uploaded to Wiki."

    def sign_up(self, name, password):
        '''
        Allows a person to create an account on the wiki if they are using it for th efirst time.

        Args:
            name = This acts as the username of the person
            password = The password associated with the account for the wiki

        Returns:
            A message letting you know if your account was successfully created,
            or if it was unsuccessful because the user already exists.
        '''

        for blob in self.users_blobs:
            if blob.name == name:
                return f"user {name} already exists in the database. Please sign in."

        blob = self.users_bucket.blob(name)
        with blob.open("w") as user:
            salty_password = f"{name}{password}".encode()
            secure_password = hashlib.sha3_256(salty_password).hexdigest()
            user.write(secure_password)

        return f"user {name} successfully created."

    #Checks the buckets to ensure correct info is being used for logins
    def sign_in(self, username, password):
        '''
        Allows a person to sign into their wiki account.

        Args:
            username = This acts as the username of the person
            password = The password associated with the account for the wiki

        Returns:
            A message letting you know if login was successful or not.
        '''
        salty_password = f"{username}{password}".encode()
        hashed = hashlib.sha3_256(salty_password).hexdigest()
        stored = False

        for blob in self.users_blobs:
            if username == blob.name:
                with blob.open("r") as username:
                    secure_password = username.read()
                stored = True
        if not stored:
            return False

        if hashed == secure_password:
            return True
        return False

    def get_image(self, name):
        '''
        Allows images to be pulled from the bucket and sent to the html pages. 

        Args:
            name = The name of the picture

        Returns:
            Binary form of the image reqested.
        '''
        blob = self.images_bucket.get_blob(name)

        if blob == None:
            return None

        with blob.open("rb") as f:
            img = f.read()

        return img

    def delete_page(self, name):
        '''
        Allows pages to be deleted from the wiki. 

        Args:
            name = The name of the page to delete

        Returns:
            True upon successful delete, false otherwise
        '''
        #Deleting the page's blob
        for blob in self.pages_blobs:
            if blob.name == name:
                blob.delete()
                return True
        #Return false if it was never found
        return False

    def search_pages(self,
                     search_content,
                     max_relevance_score,
                     wiki_searcher=None):
        """
        Searches the wiki for pages that match the search_content and returns
        a list of page titles sorted by relevance.

        Args:
            search_content (str): The search term.
            max_relevance_score (float): The maximum relevance score for a page to be considered a match.
            wiki_searcher (WikiSearcher): The object used to search for wiki pages.

        Returns:
            List[str]: The list of page titles sorted by relevance.

        """

        if wiki_searcher is None:
            wiki_searcher = self

        if len(search_content) < 1:
            return []

        # Adjust max_relevance_score based on length of search_content
        max_relevance_score = max_relevance_score / len(search_content)

        search_results = []

        all_pages = wiki_searcher.get_all_page_names()

        for page_title in all_pages:
            page_content = wiki_searcher.get_wiki_page(page_title)

            # Calculate title and content distances
            title_distance = levenshtein_distance(search_content, page_title)
            content_similarity = levenshtein_distance(search_content,
                                                      page_content)

            # Combine title and content distances to get relevance score
            relevance_score = 0.7 * content_similarity + 0.3 * title_distance

            # Scale relevance score by length of search
            relevance_score /= len(search_content)

            # Add page to search_results if relevance score is below max_relevance_score
            if relevance_score <= max_relevance_score:
                search_results.append((page_title, relevance_score))

        # Sort search_results by relevance score
        search_results.sort(key=lambda x: x[1])

        # Extract page titles from search_results and return them
        page_titles = [result[0] for result in search_results]

        return page_titles
