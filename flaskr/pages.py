# GRADED - Samuel Davidson - March 21, 2023 
# ---- YOUR APP STARTS HERE ----
# -- Import section --
from flask import Flask, redirect, url_for, flash
from flask import render_template
from flask_login import login_user, current_user, logout_user, login_required
from flask import request
from .backend import Backend
from .user import User
from .form import LoginForm
from base64 import b64encode


def make_endpoints(app, login_manager):

    @app.route("/")
    def home():
        """
        Renders the home page.

        Args:
            None

        Returns:
            If the user is authenticated, renders the main page with the user's name.
            Otherwise, renders the main page.
        """
        if current_user.is_authenticated:
            return render_template("main.html", name=current_user.name)
        return render_template("main.html")

    @app.route("/login", methods=['GET', 'POST'])
    def sign_in():
        backend = Backend()

        form = LoginForm()
        if form.validate_on_submit():
            user = User(form.username.data)
            username = form.username.data
            status = backend.sign_in(form.username.data, form.password.data)
            if status:
                login_user(user, remember=True)
                return render_template('main.html', name=current_user.name)
            elif status == False:
                flash("An incorrect password was entered")
            else:
                flash("The username is incorrect")
        return render_template('login.html', form=form, user=current_user)

    @login_manager.user_loader
    def load_user(user_id):
        return User(user_id)

    @app.route("/logout", methods=['POST', 'GET'])
    @login_required
    def logout():
        logout_user()
        return redirect(url_for('home'))

    @app.route("/about")
    def about():
        """Renders the about page with headshots of the team members.

        Returns:
            The rendered about page with headshot images of the team members.
        """
        backend = Backend()
        nasir_img = backend.get_image("Nasir.Barnes.Headshot.JPG")
        elei_img = backend.get_image("Mary.Elei.Nkata.jpeg")
        dimitri_img = backend.get_image("Dimitri.Pierre-Louis.JPG")

        return render_template("about.html", nasir_img=nasir_img, elei_img=elei_img, dimitri_img=dimitri_img)

    @app.route("/signup")
    def signup():
        """
        Renders the signup page for the user to enter their information.

        Returns:
            A rendered HTML template for the signup page.
        """
        return render_template("signup.html")

    @app.route("/createaccount",  methods=['GET', 'POST'])
    def createaccount():
        """Handles user account creation requests.

        Returns:
            If the request is GET, the rendered create account page is returned.
            If the request is POST, a new user account is created and the user is redirected to the create account confirmation page.
            If there is an error, an error message is displayed.
        """
        backend = Backend()

        if request.method != 'POST':
            return "Please go back and use the form!"

        username = str(request.form['Username'])
        password = str(request.form['Password'])

        if username == '' or password == '':
            return "Please enter a username and password."

        try:
            backend.sign_up(username, password)
            return render_template("createaccount.html", username=username)

        except Exception as e:
            return f"Account creation failed: {e}"

    @app.route("/pages", methods=['GET'])
    def pages():
        '''
        Displayes a list of all the pages in the wiki.
        '''
        backend = Backend()
        all_pages = backend.get_all_page_names()

        return render_template('pages.html', page_titles=all_pages)

    @app.route("/pages/<page_title>", methods=['GET'])
    def page_details(page_title):
        '''
        displays the details of the specific wiki page selected.
        '''
        backend = Backend()
        page = backend.get_wiki_page(page_title)

        return render_template('pages.html', page=page)

    @app.route("/upload", methods=['GET', 'POST'])
    def uploads():
        '''
        Renders the upload page where form is displayed to enable users to upload a page. 

        Returns:
            If method is GET: The page to fill out the form specifying what you want to upload
            If method is POST: The status message stating if the upload was successful or not. If the upload was unsuccessful, it states the reason why.

        '''

        if request.method == 'POST':
            backend = Backend()
            destination_blob = str(request.form['destination_blob'])
            data_file = request.files['data_file']

            data = data_file.read()
            upload_status = backend.upload(data, destination_blob)

            return render_template('upload_result.html', upload_status = upload_status)

        return render_template('upload.html')
