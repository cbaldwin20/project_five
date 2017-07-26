import datetime

from flask.ext.bcrypt import generate_password_hash
from flask.ext.login import UserMixin
from peewee import *

DATABASE = SqliteDatabase('social.db')

#sets up our table rows in peewee
#adding the UserMixin makes it so we can use "is_authenticated", "is_active", 
#"is_anonymous", "get_id()". "UserMixin" is a small class that doesn't override 
#the main inheretor class "Model".
class User(UserMixin, Model):
    """creates a table for each user and their password"""
    username = CharField(unique=True)
    email = CharField(unique=True)
    password = CharField(max_length=100)
    joined_at = DateTimeField(default=datetime.datetime.now)
    is_admin = BooleanField(default=False)
    
    class Meta:
        database = DATABASE
        order_by = ('-joined_at',)
        
    def get_one_post(self, post_id):
        """gets a specific post"""
        return Post.select().where((Post.user == self) & (Post.id == post_id))
    
    def get_stream(self):
        """gets multiple posts from the logged in user"""
        return Post.select().where(
            (Post.user == self)
        )
        
    def get_tags(self, the_tag):
        """gets posts from the logged in user that has a specific tag"""
        return Post.select().where(
            (Post.user == self) &
            (Post.tags.contains(the_tag))
            )

    def update_post(self, form, post_id):
        """updated a post after its been edited"""
        my_tags = form.tags.data.split(",")
        my_tags = [y.strip(' ') for y in my_tags]
        my_tags = ",".join(my_tags)
        q = Post.update(content=form.content.data.strip(), 
                        title=form.title.data.strip(), 
                        timestamp=form.timestamp.data, 
                resources_to_remember=form.resources_to_remember.data.strip(),
                        time_spent=form.time_spent.data.strip(),
                tags=my_tags).where((Post.id == post_id) & (Post.user == self))
        q.execute()
        return None 

    def delete_inst(self, post_id):
        x = Post.select().where((Post.user == self) & (Post.id == post_id)).get()
        x.delete_instance()

    @classmethod
    def create_user(cls, username, email, password, admin=False):
        """creates a user with a password in the database. 
        Hashes the password."""
        try:
            with DATABASE.transaction():
                cls.create(
                    username=username,
                    email=email,
                    password=generate_password_hash(password),
                    is_admin=admin)
        except IntegrityError:
            raise ValueError("User already exists")
            
            
class Post(Model):
    """a table in the database with the posts that have been created"""
    timestamp = DateField(default=datetime.date.today)
    user = ForeignKeyField(
        rel_model=User,
        related_name='posts'
    )
    title = TextField()

    content = TextField()

    resources_to_remember = TextField()

    time_spent = TextField()

    tags = TextField() 
    
    class Meta:
        database = DATABASE
        order_by = ('-timestamp',)


def initialize():
    DATABASE.get_conn()
    DATABASE.create_tables([User, Post], safe=True)
    DATABASE.close()