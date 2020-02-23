from app import app, db, forms
from app.models import User, Product
from datetime import datetime
from flask import render_template, flash, redirect, request, url_for
from flask_login import current_user, login_user, login_required, logout_user
from werkzeug.urls import url_parse

people = []
food_list = []


@app.before_request
def before_request():
    if current_user.is_authenticated:
        current_user.last_seen = datetime.utcnow()
        db.session.commit()


@app.route("/")
@app.route("/index")
@login_required
def index():
    return render_template('index.html')


@app.route('/registration', methods=['GET', 'POST'])
def registration():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = forms.RegistrationForm()
    if form.validate_on_submit():
        user = User(username=form.username.data, email=form.email.data)
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        flash('Вы были успешно зарегестрированы.')
        return redirect(url_for('index'))
    return render_template('registration.html', form=form)


@app.route("/login", methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = forms.LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user is None or not user.check_password(form.password.data):
            flash('Неверный логин или пароль')
            return redirect(url_for('login'))
        login_user(user, remember=form.remember_me.data)
        next_page = request.args.get('next')
        if not next_page or url_parse(next_page).netloc != '':
            next_page = url_for('index')
        return redirect(next_page)
    return render_template('login.html', form=form)


@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('index'))


@app.route("/user/<username>")
@login_required
def user(username):
    user = User.query.filter_by(username=username).first_or_404()
    products = Product.query.all()
    return render_template('user.html', user=user, products=products)


@app.route('/edit_profile', methods=['GET', 'POST'])
@login_required
def edit_profile():
    form = forms.EditProfileForm(current_user.username)
    if form.validate_on_submit():
        current_user.username = form.username.data
        current_user.status = form.status.data
        db.session.commit()
        flash('Изменения сохранены.')
        return redirect(url_for('user', username=current_user.username))
    elif request.method == 'GET':
        form.username.data = current_user.username
        form.status.data = current_user.status
    return render_template('edit_profile.html', form=form)


@app.route("/new_person", methods=['GET', 'POST'])
def new_person():
    form = forms.NameForm()
    if form.validate_on_submit():
        flash('Добавлен новый человек ({})'.format(form.name.data))
        return redirect(url_for('index'))
    return render_template('new_person.html', form=form)


@app.route('/add_product', methods=['GET', 'POST'])
@login_required
def add_product():
    form = forms.AddProductForm()
    if form.validate_on_submit():
        product = Product(product_name=form.product_name.data, count=int(form.count.data),
                          price=int(form.price.data), user_id=current_user.id)
        db.session.add(product)
        db.session.commit()
        flash('Продукт успешно добавлен.')
        return redirect(url_for('index'))
    return render_template('add_product.html', form=form)


@app.route('/add_person', methods=['POST'])
def add_person():
    data = request.json
    name = data['person']
    people.append(name)
    print('Person %s added.' % name)
    return {'ok': True}


@app.route('/add_food', methods=['POST'])
def add_food():
    data = request.json
    food_name = data['food_name'].capitalize()
    price = int(data['price'])
    count = int(data['count'])
    cost = price * count
    food_list.append({'food_name': food_name,
                      'price': price,
                      'count': count,
                      'cost': cost})
    print(food_list)
    print('Food %s added.' % food_name)
    return {'ok': True}


@app.route('/change_food', methods=['POST'])
def change_food():
    data = request.json
    number = data['number']
    new_food_name = data['food_name']
    food_list[number]['food_name'] = new_food_name
    return {'ok': True}


@app.route('/food_list')
def get_food_list():
    total_cost = 0
    for food in food_list:
        total_cost += food['cost']
    return render_template('food_list.html', food_list=food_list, total_cost=total_cost)


@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404


if __name__ == '__main__':
    app.run(debug=True)
