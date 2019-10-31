# -*- coding: utf-8 -*-

from scripts import tabledef
from scripts import forms
from scripts import helpers
from flask import Flask, redirect, url_for, render_template, request, session, jsonify
import json
import sys
import os

import model as ml

from base64 import b64encode

import stripe


os.environ['STRIPE_PUBLISHABLE_KEY'] = 'pk_test_9qnorLWUQILDlpMbGFjx1jM300ESwEvbGe'
os.environ['STRIPE_SECRET_KEY'] = 'sk_test_AxJs3AsRcXNSw5kZ6RUr66Au00LLXE8ynD'

STRIPE_PUBLISHABLE_KEY = 'pk_test_9qnorLWUQILDlpMbGFjx1jM300ESwEvbGe'
STRIPE_SECRET_KEY = 'sk_test_AxJs3AsRcXNSw5kZ6RUr66Au00LLXE8ynD'

app = Flask(__name__)
app.secret_key = os.urandom(12)  # Generic key for dev purposes only


stripe_keys = {
  'secret_key': os.environ['STRIPE_SECRET_KEY'],
  'publishable_key': os.environ['STRIPE_PUBLISHABLE_KEY']
}

stripe.api_key = STRIPE_SECRET_KEY

# ======== Routing =========================================================== #
# -------- Login ------------------------------------------------------------- #
@app.route('/', methods=['GET', 'POST'])
def login():
    if not session.get('logged_in'):
        form = forms.LoginForm(request.form)
        if request.method == 'POST':
            username = request.form['username'].lower()
            password = request.form['password']
            if form.validate():
                if helpers.credentials_valid(username, password):
                    session['logged_in'] = True
                    session['username'] = username
                    return json.dumps({'status': 'Login successful'})
                return json.dumps({'status': 'Invalid user/pass'})
            return json.dumps({'status': 'Both fields required'})
        return render_template('login.html', form=form)
    user = helpers.get_user()
    return render_template('home.html', user=user)


# -------- Signup ---------------------------------------------------------- #
@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if not session.get('logged_in'):
        form = forms.LoginForm(request.form)
        if request.method == 'POST':
            username = request.form['username'].lower()
            password = helpers.hash_password(request.form['password'])
            email = request.form['email']
            if form.validate():
                if not helpers.username_taken(username):
                    helpers.add_user(username, password, email)
                    session['logged_in'] = True
                    session['username'] = username
                    return json.dumps({'status': 'Signup successful'})
                return json.dumps({'status': 'Username taken'})
            return json.dumps({'status': 'User/Pass required'})
        return render_template('login.html', form=form)
    return redirect(url_for('login'))


# -------- Settings ---------------------------------------------------------- #
@app.route('/settings', methods=['GET', 'POST'])
def settings():
    if session.get('logged_in'):
        if request.method == 'POST':
            password = request.form['password']
            if password != "":
                password = helpers.hash_password(password)
            email = request.form['email']
            helpers.change_user(password=password, email=email)
            return json.dumps({'status': 'Saved'})
        user = helpers.get_user()
        return render_template('settings.html', user=user)
    return redirect(url_for('login'))

# -------- Charge ---------------------------------------------------------- #
@app.route('/charge', methods=['POST'])
def charge():
    if session.get('logged_in'):
        user = helpers.get_user()
        try:
            amount = 1000   # amount in cents
            customer = stripe.Customer.create(
                email= user.email,
                source=request.form['stripeToken']
            )
            stripe.Charge.create(
                customer=customer.id,
                amount=amount,
                currency='usd',
                description='Discount Optimizer Charge'
            )
            #helpers.change_user(payment=helpers.payment_token())
            user.active = True
            return render_template('home.html', user=user)
        except stripe.error.StripeError:
            return render_template('error.html')

@app.route('/analyze', methods=['POST'])
def analyze():
    img_data = request.files.get('imfile', '')
    img = img_data.read()
    prediction = ml.classify(img)
    disp_im = b64encode(img).decode("utf-8")
    return render_template("predictor.html", result=prediction, file=disp_im)

@app.route("/logout")
def logout():
    session['logged_in'] = False
    return redirect(url_for('login'))

# ======== Main ============================================================== #
if __name__ == "__main__":
    app.run(debug=True, use_reloader=True)
