import html
from datetime import datetime

from flask import Flask, render_template, redirect, url_for, request, flash
from flask_login import LoginManager, current_user, login_user, logout_user, login_required

from database import db, get_model_fields, get_tables_name
from models import User, getModel, Blog, Tag, Comment

app = Flask(__name__, static_url_path='/static')
app.config['SECRET_KEY'] = '12345'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///blog.db'
app.app_context().push()
db.init_app(app)

login = LoginManager(app)

@login.user_loader
def load_user(user_id):
    return db.session.get(User, int(user_id))

@app.template_filter('nl2br')
def nl2br_filter(value):
    """Преобразует переносы строк в <br> теги"""
    if not value:
        return ''
    return html.escape(value).replace('\n', '<br>\n')

@app.template_filter('striptags')
def striptags_filter(value):
    """Удаляет HTML теги из текста"""
    if not value:
        return ''
    import re
    return re.sub(r'<[^>]*>', '', value)

@app.route('/')
def index():
    """Главная страница со всеми статьями"""
    page = request.args.get('page', 1, type=int)
    blogs = Blog.query.order_by(Blog.created_at.desc()).paginate(
        page=page, per_page=5, error_out=False
    )
    return render_template('index.html',
                           blogs=blogs)

@app.route('/blog_detail/<int:blog_id>')
def blog_detail(blog_id):
    """Страница отдельной статьи"""
    blog = Blog.query.get_or_404(blog_id)
    return render_template('blog.html', blog=blog)

@app.route('/add_comment/<int:blog_id>', methods=['POST'])
def add_comment(blog_id):
    """Страница отдельной статьи"""
    comment = Comment()
    comment.blog_id = blog_id
    comment.author_id = current_user.id
    comment.text = request.form['content']

    db.session.add(comment)
    db.session.commit()
    return redirect(url_for('blog_detail', blog_id=blog_id))

@app.route('/tag/<string:tag_name>')
def blogs_by_tag(tag_name):
    """Фильтрация статей по тегу"""
    tag = Tag.query.filter_by(name=tag_name).first_or_404()

    page = request.args.get('page', 1, type=int)

    tag = Tag.query.filter_by(name=tag_name).first()
    if tag:
        blogs = Blog.query \
            .filter(Blog.tags.any(id=tag.id)) \
            .order_by(Blog.created_at.desc()) \
            .paginate(page=page, per_page=5, error_out=False)

    return render_template('index.html',
                           blogs=blogs)

@app.route('/auth/register/', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('index', username=current_user.name))
    if request.method == 'POST':
        form_name = request.form['name']
        form_email = request.form['email']
        form_password = request.form['password']
        if User.query.filter_by(email=form_email).first():
            flash('Такой пользователь уже существует')
        user = User()
        user.name = form_name
        user.email = form_email
        user.set_password(form_password)

        db.session.add(user)
        db.session.commit()
        return redirect(url_for('/auth/login'))
    return render_template('/auth/register.html')


@app.route('/auth/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        print("already auth")
        return redirect(url_for('index'))
    if request.method == 'POST':
        form_email = request.form['email']
        form_password = request.form['password']
        user = User.query.filter_by(email=form_email).first()
        if user and user.check_password(form_password):
            print("login accept")
            login_user(user)
            return redirect(url_for('index'))
        flash("Неверно введенные данные", 'danger')
    return render_template('/auth/login.html')


@app.route('/auth/logout')
@login_required
def logout():
    logout_user()
    return redirect('/auth/login')


@app.route('/admin')
@login_required
def admin():
    tables = get_tables_name()
    return render_template('/admin/main.html', tables=tables)


@app.route('/admin/tables/<name>', methods=['GET', 'POST'])
@login_required
def admin_tables(name):
    if request.method == 'POST':
        model = getModel(name)()
        model.set_values(request.form)
        db.session.add(model)
        db.session.commit()
    tables = get_tables_name()
    fields = get_model_fields(getModel(name))
    fkdict = dict()
    for field in fields:
        if field['foreign_key']:
            col = list(field['foreign_key'])[0].column
            res = db.session.query(col.table).all()
            fkdict[field['name']] = res
    fields_data = getModel(name).query.all()
    print(fields)
    return render_template('/admin/basicTable.html',
                           tables=tables,
                           tablename=name,
                           fields=fields,
                           data=fields_data,
                           fkdict=fkdict,
                           now=datetime.now())


if __name__ == '__main__':
    app.run(debug=True)
