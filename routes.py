from flask import Flask, request, render_template, redirect, url_for, flash
from models import db, User, FavoriteMeal
from app import app
from forms import RegistrationForm, LoginForm, FavoriteMealForm
from flask_login import login_user, logout_user, login_required, current_user
import random
import requests

API_URL = "https://www.themealdb.com/api/json/v1/1/search.php?s="

def get_meals():
    response = requests.get(API_URL)
    if response.status_code == 200:
        data = response.json()
        return data.get('meals', [])
    return []

@app.route('/')
def home():
    return render_template('home.html', current_user=current_user)

@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegistrationForm()
    if form.validate_on_submit():
        existing_user = User.query.filter_by(username=form.username.data).first()
        if existing_user is None:
            new_user = User(username=form.username.data, email=form.email.data)
            new_user.set_password(form.password.data)
            db.session.add(new_user)
            db.session.commit()
            flash("Congratulations! You are now a proud user of FoodPrepR!")
            return redirect(url_for('home'))
        else:
            flash("Username already exists. Please choose a different username.")
    return render_template('register.html', form=form, current_user=current_user)

@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user and user.check_password(form.password.data):
            login_user(user)
            flash("Login Successful!")
            return redirect(url_for('meals'))
        else:
            flash("Login Unsuccessful. Please check username and password")
    return render_template('login.html', form=form, current_user=current_user)

@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash("You have been logged out")
    return redirect(url_for('home'))

@app.route('/meals', methods=['GET', 'POST'])
@login_required
def meals():
    form = FavoriteMealForm()
    meals = get_meals()

    form.meal.choices = [(meal['idMeal'], meal['strMeal']) for meal in meals]

    if form.validate_on_submit():
        selected_meal = form.meal.data
        meal_name = next((meal['strMeal'] for meal in meals if meal['idMeal'] == selected_meal))

        if FavoriteMeal.query.filter_by(user_id=current_user.id, meal_id=selected_meal).first():
            flash(f"{meal_name} is already in your favorites")
        else:
            new_fav = FavoriteMeal(user_id=current_user.id, meal_name=meal_name, meal_id=selected_meal)
            db.session.add(new_fav)
            db.session.commit()
            flash(f"{meal_name} has been added to your favorites")

        return redirect(url_for('meals'))

    user_favorites = FavoriteMeal.query.filter_by(user_id=current_user.id).all()
    return render_template('meals.html', form=form, user_favorites=user_favorites, current_user=current_user)

@app.route('/random_meal')
@login_required
def random_meal():
    user_favorites = FavoriteMeal.query.filter_by(user_id=current_user.id).all()
    
    if not user_favorites:
        flash("You don't have any favorite meals yet!")
        return redirect(url_for('meals'))

    chosen_meal = random.choice(user_favorites)

    response = requests.get(f"{API_URL}{chosen_meal.meal_name}")
    if response.status_code == 200:
        meal_data = response.json()['meals'][0]
    else:
        meal_data = None

    return render_template('random_meal.html', meal=chosen_meal, meal_data=meal_data, current_user=current_user)