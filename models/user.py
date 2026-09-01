from extensions import db, login_manager
from flask_login import UserMixin
from datetime import datetime

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


class User(db.Model, UserMixin):
    __tablename__ = 'users'
    id                  = db.Column(db.Integer, primary_key=True)
    fullname            = db.Column(db.String(120), nullable=False)
    email               = db.Column(db.String(120), unique=True, nullable=False)
    mobile              = db.Column(db.String(20))
    nic                 = db.Column(db.String(20), unique=True)
    password            = db.Column(db.String(256), nullable=False)
    preferred_language  = db.Column(db.Enum('English', 'Tamil', 'Sinhala'), default='English')
    role                = db.Column(db.Enum('user', 'admin'), default='user')
    created_at          = db.Column(db.DateTime, default=datetime.utcnow)

    chats        = db.relationship('ChatHistory', backref='user', lazy=True)
    saved        = db.relationship('SavedGuide',  backref='user', lazy=True)
    applications = db.relationship('Application', backref='user', lazy=True)


class GovService(db.Model):
    __tablename__ = 'gov_services'
    id            = db.Column(db.Integer, primary_key=True)
    name          = db.Column(db.String(150), nullable=False)
    category      = db.Column(db.String(80))
    icon          = db.Column(db.String(10))
    description   = db.Column(db.Text)
    official_link = db.Column(db.String(300))
    status        = db.Column(db.Enum('Active', 'Inactive'), default='Active')
    created_at    = db.Column(db.DateTime, default=datetime.utcnow)

    steps     = db.relationship('ServiceStep', backref='service', lazy=True, cascade="all, delete-orphan")
    documents = db.relationship('RequiredDocument', backref='service', lazy=True, cascade="all, delete-orphan")


class ServiceStep(db.Model):
    __tablename__ = 'service_steps'
    id          = db.Column(db.Integer, primary_key=True)
    service_id  = db.Column(db.Integer, db.ForeignKey('gov_services.id'), nullable=False)
    step_number = db.Column(db.Integer, nullable=False)
    title       = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)


class RequiredDocument(db.Model):
    __tablename__ = 'required_documents'
    id            = db.Column(db.Integer, primary_key=True)
    service_id    = db.Column(db.Integer, db.ForeignKey('gov_services.id'), nullable=False)
    document_name = db.Column(db.String(200), nullable=False)
    is_mandatory  = db.Column(db.Boolean, default=True)


class ChatHistory(db.Model):
    __tablename__ = 'chat_history'
    id         = db.Column(db.Integer, primary_key=True)
    user_id    = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    question   = db.Column(db.Text, nullable=False)
    response   = db.Column(db.Text, nullable=False)
    language   = db.Column(db.String(20), default='English')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)


class SavedGuide(db.Model):
    __tablename__ = 'saved_guides'
    id         = db.Column(db.Integer, primary_key=True)
    user_id    = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    service_id = db.Column(db.Integer, db.ForeignKey('gov_services.id'), nullable=False)
    saved_at   = db.Column(db.DateTime, default=datetime.utcnow)

    service = db.relationship('GovService')


class OfficialLink(db.Model):
    __tablename__ = 'official_links'
    id         = db.Column(db.Integer, primary_key=True)
    title      = db.Column(db.String(150), nullable=False)
    url        = db.Column(db.String(300), nullable=False)
    department = db.Column(db.String(150))
    icon       = db.Column(db.String(10))


class Application(db.Model):
    """
    Tracks a user's actual application for a government service
    (e.g. New Passport, NIC Renewal) — separate from SavedGuide
    (which is just a bookmark) and ChatHistory (AI conversation log).
    Created by the Form Assistant wizard; status is updated by Admin.
    """
    __tablename__ = 'applications'
    id            = db.Column(db.Integer, primary_key=True)
    application_no = db.Column(db.String(20), unique=True, nullable=False)  # e.g. APP12345
    user_id       = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    service_id    = db.Column(db.Integer, db.ForeignKey('gov_services.id'), nullable=False)
    application_type = db.Column(db.String(100))   # e.g. "New Passport", "NIC Renewal"
    form_data     = db.Column(db.Text)              # JSON string of submitted form fields
    status        = db.Column(db.Enum('In Progress', 'Completed', 'Rejected'), default='In Progress')
    submitted_at  = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at    = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    service = db.relationship('GovService')

class Division(db.Model):
    __tablename__ = 'divisions'
    id         = db.Column(db.Integer, primary_key=True)
    service    = db.Column(db.String(100), nullable=False)
    district   = db.Column(db.String(100), nullable=False)
    office_name = db.Column(db.String(200), nullable=False)
    address    = db.Column(db.String(300), nullable=False)
    phone      = db.Column(db.String(50))
    lat        = db.Column(db.Float, nullable=False)
    lng        = db.Column(db.Float, nullable=False)