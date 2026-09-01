from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from extensions import db

profile = Blueprint('profile', __name__)


@profile.route('/profile', methods=['GET', 'POST'])
@login_required
def my_profile():
    if request.method == 'POST':
        current_user.fullname = request.form.get('fullname')
        current_user.mobile = request.form.get('mobile')
        current_user.preferred_language = request.form.get('preferred_language')
        db.session.commit()
        flash('Profile updated successfully!', 'success')
        return redirect(url_for('profile.my_profile'))
    return render_template('profile.html')
