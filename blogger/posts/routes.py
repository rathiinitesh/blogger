from flask import Blueprint, flash, url_for, render_template, redirect, request, abort
from flask_login import login_required, current_user

from blogger import db
from blogger.models import Post
from blogger.posts.forms import PostForm

posts = Blueprint('posts', __name__)


@posts.route('/post/new', methods=['POST', 'GET'])
@login_required
def new_post():
    form = PostForm()
    if form.validate_on_submit():
        post = Post(title=form.title.data, content=form.content.data, author=current_user)
        db.session.add(post)
        db.session.commit()
        flash('Your post has been created!!!', 'success')
        return redirect(url_for('main.home'))
    return render_template('create_post.html', title='New Post', form=form, legend='Create Post')


@posts.route('/post/<int:idx>', methods=['POST', 'GET'])
@login_required
def view_post(idx):
    post = Post.query.get_or_404(idx)
    return render_template('post.html', title=post.title, post=post)


@posts.route('/post/<int:idx>/update', methods=['POST', 'GET'])
@login_required
def update_post(idx):
    post = Post.query.get_or_404(idx)
    if post.author.id != current_user.id:
        abort(403)
    form = PostForm()
    if form.validate_on_submit():
        post.title = form.title.data
        post.content = form.content.data
        db.session.commit()
        flash('Your post has been updated!!!', 'success')
        return redirect(url_for('main.home'))
    elif request.method == 'GET':
        form.title.data = post.title
        form.content.data = post.content
    return render_template('create_post.html', title='Update Post', form=form, legend='Update Post')


@posts.route('/post/<int:idx>/delete', methods=['POST', 'GET'])
@login_required
def delete_post(idx):
    post = Post.query.get_or_404(idx)
    if post.author.id != current_user.id:
        abort(403)
    db.session.delete(post)
    db.session.commit()
    flash('Your post has been deleted!!!', 'success')
    return redirect(url_for('main.home'))
