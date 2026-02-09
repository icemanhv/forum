from datetime import datetime

from flask_login import UserMixin
from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, Boolean
from sqlalchemy.orm import relationship
from werkzeug.security import generate_password_hash, check_password_hash

from database import db


class User(UserMixin, db.Model):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True)
    name = Column(String(255))
    email = Column(String(50), unique=True, nullable=False)
    password_hash = Column(String(128), nullable=False)
    is_admin = Column(Boolean, default=False)
    blogs = relationship('Blog', back_populates="user")
    comments = relationship('Comment', back_populates="user")
    def __repr__(self):
        return f'{self.id, self.name, self.email, self.password_hash}'

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def set_values(self, form_data):
        self.name = form_data['name']
        self.email = form_data['email']
        self.password_hash = generate_password_hash(form_data['password_hash'])


class BlogTags(db.Model):
    __tablename__ = 'blog_tags'
    id = Column(Integer, primary_key=True)
    blog_id = Column(Integer, ForeignKey('blog.id'))
    tag_id = Column(Integer, ForeignKey('tag.id'))

    def set_values(self, form_data):
        self.blog_id = form_data['blog_id']
        self.tag_id = form_data['tag_id']


class Blog(db.Model):
    __tablename__ = 'blog'
    id = Column(Integer, primary_key=True)
    title = Column(String(80), unique=False)
    content = Column(Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.now)
    updated_at = db.Column(db.DateTime, default=datetime.now, onupdate=datetime.now)
    id_user = Column(Integer, ForeignKey('users.id'))
    user = relationship('User', back_populates='blogs')
    comments = relationship('Comment', back_populates='blog')
    # Связь многие-ко-многим через ассоциативную модель
    tags = relationship('Tag',
                        secondary=BlogTags.__table__,
                        back_populates='blogs')

    def set_values(self, form_data):
        self.title = form_data['title']
        self.content = form_data['content']
        self.created_at = datetime.strptime(form_data['created_at'], '%Y-%m-%dT%H:%M')
        self.updated_at = datetime.strptime(form_data['updated_at'], '%Y-%m-%dT%H:%M')
        self.id_user = int(form_data['id_user'])

    def __repr__(self):
        return f'{self.id, self.title, self.content, self.created_at, self.updated_at, self.id_user}'


class Comment(db.Model):
    __tablename__ = 'comments'
    id = Column(Integer, primary_key=True)
    text = Column(Text, nullable=False)
    author_id = Column(Integer, ForeignKey('users.id'))
    timestamp = Column(DateTime(), default=datetime.now)
    blog_id = Column(Integer, ForeignKey('blog.id'))
    blog = relationship('Blog', back_populates='comments')
    user = relationship('User', back_populates='comments')

    def set_values(self, form_data):
        self.author_id = form_data['author_id']
        self.text = form_data['text']
        self.timestamp = datetime.strptime(form_data['timestamp'], '%Y-%m-%dT%H:%M')
        self.blog_id = int(form_data['blog_id'])

    def __repr__(self):
        return f'{self.id, self.place, self.timestamp, self.cost, self.tour_id}'


class Tag(db.Model):
    __tablename__ = 'tag'
    id = Column(Integer, primary_key=True)
    name = Column(String(255), unique=True)

    # Обратная связь
    blogs = relationship('Blog',
                         secondary=BlogTags.__table__,
                         back_populates='tags')

    def set_values(self, form_data):
        self.name = form_data['name']

    def __repr__(self):
        return f'{self.name}'

def getModel(tablename):
    dictTables = {User.__tablename__: User,
                  Blog.__tablename__: Blog,
                  Comment.__tablename__: Comment,
                  BlogTags.__tablename__: BlogTags,
                  Tag.__tablename__: Tag}
    return dictTables[tablename]


#Первоначальное создание базы данных и таблиц прямым вызовом файла
if __name__ == '__main__':
    from flask import Flask
    from database import db

    app = Flask(__name__, static_url_path='/static')
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///blog.db'
    app.app_context().push()
    db.init_app(app)
    db.create_all()
    admin = User()
    admin.is_admin = True
    admin.name = 'Администратор'
    admin.set_password('1234')
    admin.email = ''
    db.session.add(admin)
    db.session.commit()
