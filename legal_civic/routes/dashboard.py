from flask import Blueprint, render_template
from flask_login import login_required, current_user
from models.user import ChatHistory, SavedGuide, GovService

dashboard = Blueprint('dashboard', __name__)


@dashboard.route('/dashboard')
@login_required
def home():
    recent_chats  = ChatHistory.query.filter_by(user_id=current_user.id)\
                        .order_by(ChatHistory.created_at.desc()).limit(5).all()
    saved_guides  = SavedGuide.query.filter_by(user_id=current_user.id).all()
    chat_count    = ChatHistory.query.filter_by(user_id=current_user.id).count()
    popular       = GovService.query.filter_by(status='Active').limit(5).all()

    return render_template(
        'dashboard.html',
        recent_chats=recent_chats,
        saved_guides=saved_guides,
        chat_count=chat_count,
        saved_count=len(saved_guides),
        popular=popular
    )
