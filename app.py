from flask import (Flask, g, render_template, flash, redirect, url_for,
                  abort)
from flask.ext.bcrypt import check_password_hash
from flask.ext.login import (LoginManager, login_user, logout_user,
                             login_required, current_user)
import forms
import models

#These are used at the very bottom in the "if __name___= '__main__' "
DEBUG = True
PORT = 8000
HOST = '0.0.0.0'

app = Flask(__name__)
app.secret_key = 'auoesh.bouoastuh.43,uoausoehuosth3ououea.auoub!'

#create an instance of LoginManager(), LoginManager handles user authentication
login_manager = LoginManager()
login_manager.init_app(app)
#if they are not logged in, it redirects them to the view function 'login'. 
login_manager.login_view = 'login'

#this is a view function that is called when the program is looking to load the
# user. 
@login_manager.user_loader
def load_user(userid):
    """this will get the row in the table User where the id matches the userid.
    # If there is none then it excepts a DoesNotExist"""
    try:
        return models.User.get(models.User.id == userid)
    except models.DoesNotExist:
        return None

#If another view is called, this will run first and then the other view will 
#run. 
@app.before_request
def before_request():
    """Connect to the database before each request."""
    #g is global, meaning we can use it in all the view functions without 
    #passing it in the argument. "models.DATABASE" means import from our 
    #file models "DATABASE".
    g.db = models.DATABASE
    g.db.connect()
    #this is our global user. 'current_user' was imported above to use as a 
    #flask extension.
    g.user = current_user

#if another view is called, this will run after the other view is run.
@app.after_request
def after_request(response):
    """Close the database connection after each request."""
    g.db.close()
    return response


@app.route('/register', methods=('GET', 'POST'))
def register():
    """processes the register form"""
    #takes in the name, email, password that was filled out
    form = forms.RegisterForm()
    #if the info passes validation run this
    if form.validate_on_submit():
        flash("Yay, you registered!", "success")
        #runs the create_user method which will encrypt the password before 
        #saving it to the database. 
        models.User.create_user(
            username=form.username.data,
            email=form.email.data,
            password=form.password.data
        )
        #if the there was data in the form and they passed validation then open 
        #the home page.
        return redirect(url_for('login'))
    #if there was not data in the form or it didn't pass validation open the 
    #register page. 
    return render_template('register.html', form=form)


@app.route('/login', methods=('GET', 'POST'))
def login():
    """processes the login page"""
    logout_user()
    form = forms.LoginForm()
    if form.validate_on_submit():
        try:
            user = models.User.get(models.User.email == form.email.data)
        except models.DoesNotExist:
            flash("Your email or password doesn't match!", "error")
        else:
            if check_password_hash(user.password, form.password.data):
                #'login_user' is a function to log a user in and set the 
                #appropriate cookie so they'll be considered authenticated by 
                #Flask-Login
                login_user(user)
                flash("You've been logged in!", "success")
                return redirect(url_for('index'))
            else:
                flash("Your email or password doesn't match!", "error")
    return render_template('login.html', form=form)


@app.route('/logout')
@login_required
@login_required
def logout():
    """processes the logout page"""
    #logout_user is a method to remove a user's session and sign them out.
    logout_user()
    flash("You've been logged out! Come back soon!", "success")
    return redirect(url_for('index'))


@app.route('/new_post', methods=('GET', 'POST'))
@login_required
@login_required
def post():
    """creates a new post"""
    form = forms.PostForm()
    if form.validate_on_submit():
        #erases the spaces from the tags to properly store them
        my_tags = form.tags.data.split(",")
        my_tags = [y.strip(' ') for y in my_tags]
        my_tags = ",".join(my_tags)

        #erases the spaces from resources to remember to properly store them
        resources_to_rem = form.resources_to_remember.data.split(",")
        resources_to_rem = [y.strip(' ') for y in resources_to_rem]
        resources_to_rem = ",".join(resources_to_rem)
        models.Post.create(timestamp = form.timestamp.data,
                            user=g.user.id,
                            title=form.title.data.strip(),
                           content=form.content.data.strip(),
                resources_to_remember = resources_to_rem,
                           time_spent = form.time_spent.data.strip(),
                           tags = my_tags)
        flash("Entry posted! Thanks!", "success")
        return redirect(url_for('index'))
    return render_template('new.html', form=form)


@app.route('/edit/<int:post_id>/<post_title>', methods=('GET', 'POST'))
@login_required
def edit(post_id, post_title):
    """edits a post from the database"""
    form = forms.PostForm() 
    if form.validate_on_submit():
        current_user.update_post(form, post_id)
        flash("Entry updated! Thanks!", "success")
        return redirect(url_for('index'))
    return render_template('edit.html', form=form)


@app.route('/delete/<int:post_id>/<int:yesOrNo>/<post_title>')
@login_required
def delete(post_id, yesOrNo, post_title):
    """deletes a post from the database"""
    if yesOrNo == 4:
        return render_template('delete.html', post_id=post_id, 
            post_title=post_title)
    elif yesOrNo == 1:
        posts = current_user.delete_inst(post_id)
        flash("Deletion complete.", "success")
        return redirect(url_for('index'))
    flash("Deletion cancelled", "success")
    return redirect(url_for('view_post', post_id=post_id, post_title=post_title))


@app.route('/entries')
@app.route('/')
@login_required
def index():
    """go to the database and get the first 100 entries.
     Is also the home page."""
    stream = current_user.get_stream().limit(100)
    return render_template('index.html', stream=stream, user=current_user)


@app.route('/entry/<int:post_id>/<post_title>')
@app.route('/details/<int:post_id>/<post_title>')
@app.route('/post/<int:post_id>/<post_title>')
@login_required
def view_post(post_id, post_title):
    """views a specific single post"""
    posts =  current_user.get_one_post(post_id)
    if posts.count() == 0:
        #abort() - Function to immediately end a request with a specified 
        #status code.
        abort(404)
    return render_template('detail.html', stream=posts, user=current_user)


@app.route('/tags/<tagName>')
@login_required
def tags(tagName):
    """gets all the posts with a specific tag"""
    template = 'index.html'
    stream = current_user.get_tags(tagName).limit(100)
    user = current_user
    flash("Tags for: {}".format(tagName), "success")
    return render_template(template, stream=stream, user=user)

#errorhandler() - Decorator that marks a function as handling a certain status 
#code.
@app.errorhandler(404)
@login_required
def not_found(error):
    #return render_template('template.html'), 404 - The 404 on the end specifies
    # the status code for the response.
    return render_template('404.html'), 404


if __name__ == '__main__': 
    models.initialize()
    app.run(debug=DEBUG, host=HOST, port=PORT)