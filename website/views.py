from flask import Blueprint, render_template, request, flash, redirect, url_for
from flask_login import login_required, current_user
from functools import cmp_to_key
from .models import User, Post, Current_Post
from . import db
import json

views = Blueprint('views', __name__)

@views.route('/', methods=['GET', 'POST'])
@login_required
def home():
    return render_template('home.html', user=current_user)

@views.route('/blog', methods=['GET', 'POST'])
@login_required
def blog():
    # lấy toàn bộ post hiện tại có
    posts = Post.query.all()

    if request.method == 'POST':
        type = request.form.get('sort-type')

        if type == 'dec':
            posts = Post.query.all().sort(key=cmp_to_key(lambda x, y: x.id - y.id))

    print(posts)

    return render_template('blog.html', user=current_user, posts=posts)

@views.route('/create', methods=['GET', 'POST'])
def create():
    if request.method == 'POST':
        title = request.form.get('title')
        content = request.form.get('content')
        tags = request.form.get('tags')

        #mỗi lần preview thì cập nhật lại current_posts[0]
        #em để one-many, tức lưu nhiều current_posts để sau có thể nâng cấp lên kiểu.. lưu nhiều bài chưa hoàn thiện
        try:
            db.session.delete(current_user.current_posts[0])
        except:
            pass
        current_post = Current_Post(title=title, content=content, tags=tags, user_id=current_user.id)
        db.session.add(current_post)
        db.session.commit()

        return redirect(url_for('views.preview'))

    try:
        current_post = current_user.current_posts[0]
        title = current_post.title
        content = current_post.content
        tags = current_post.tags
    except:
        title = ""
        content = ""
        tags = ""
    return render_template('create.html', user=current_user, title=title, content=content, tags=tags)

# để xoá một post thì gởi request API với nội dung là id của post muốn xoá
# em đã tạo sẵn một hàm deletePost ở file base.html
# khi bấm xoá post thì gọi hàm deletePost và truyền tham số là id của post
@views.route('/<int:id>/delete', methods=['GET', 'POST'])
def delete(id):
    post = Post.query.get(id)
    id = post.id
    title = post.title
    content = post.content
    tags = post.tags
    date = post.date

    if request.method == 'POST':
        db.session.delete(post)
        db.session.commit()
        return redirect(url_for('views.blog'))

    return render_template("delete.html", user=current_user, title=title, content=content, tags=tags, date=date)

# để edit một post thì anh gọi đến hàm này với <int:id> là id của post muốn edit
# một cách dễ là tạo 1 thẻ a với href="{{ url_for('views.edit', id=post['id']) }}
@views.route('/<int:id>/edit', methods=['GET', 'POST'])
def edit(id):
    post = Post.query.get(id)
    title = post.title
    content = post.content
    tags = post.tags

    if request.method == 'POST':
        post.title = request.form.get('title')
        post.content = request.form.get('content')
        post.tags = request.form.get('tags')
        db.session.commit()
        return redirect(url_for('views.blog'))

    return render_template("edit.html", user=current_user, title=title, content=content, tags=tags)
    

@views.route('/preview', methods=['GET', 'POST'])
def preview():
    current_post = current_user.current_posts[0]
    title = current_post.title
    content = current_post.content
    tags = current_post.tags
    author = current_user.user_name

    if request.method == 'POST':
        if request.form['btn'] == 'post':
            current_post = current_user.current_posts[0]
            title = current_post.title
            content = current_post.content
            tags = current_post.tags

            new_post = Post(title=title, content=content, tags=tags, user_id=current_user.id, author=author)
            db.session.add(new_post)
            db.session.commit()

            return redirect(url_for('views.blog'))

    return render_template('preview.html', user=current_user, title=title, content=content, tags=tags, author=author)

@views.route('/<int:id>/view', methods=['GET', 'POST'])
def view(id):
    post = Post.query.get(id)
    id = post.id
    title = post.title
    content = post.content
    tags = post.tags
    date = post.date
    author = post.author
    return render_template('view.html', user=current_user, id=id, title=title, content=content, tags=tags, date=date, author=author)