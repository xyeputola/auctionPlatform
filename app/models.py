from datetime import datetime, timezone
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from app.extensions import db


def utc_now():
    return datetime.now(timezone.utc)

class User(UserMixin, db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), nullable=False, unique=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(120), nullable=False)
    role=db.Column(db.String(20), default='user', nullable=False)
    created_at = db.Column(db.DateTime(timezone = True), default=utc_now)

    auctions = db.relationship("Auction", back_populates="seller")
    bids = db.relationship("Bid", back_populates="user")
    favorites = db.relationship("Favorite", back_populates="user")

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

class Category(db.Model):
    __tablename__ = 'categories'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), nullable=False, unique=True)

    auctions = db.relationship("Auction", back_populates="category")

class Auction(db.Model):
    __tablename__ = "auctions"
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(120), nullable=False)
    description = db.Column(db.Text, nullable=False)

    starting_price = db.Column(db.Integer, nullable=False)
    current_price = db.Column(db.Integer, nullable=False)

    photo_filename = db.Column(db.String(255), nullable=False)

    status = db.Column(db.String(20), default="Active", nullable=False)
    created_at = db.Column(db.DateTime(timezone = True), default=utc_now)
    ends_at = db.Column(db.DateTime(timezone = True), nullable=False)

    seller_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    category_id = db.Column(db.Integer, db.ForeignKey('categories.id'), nullable=False)

    seller = db.relationship("User", back_populates="auctions")
    category = db.relationship("Category", back_populates="auctions")
    bids = db.relationship("Bid", back_populates="auction", cascade="all, delete-orphan")
    favorites = db.relationship("Favorite", back_populates="auction", cascade="all, delete-orphan")

class Bid(db.Model):
    __tablename__ = "bids"

    id = db.Column(db.Integer, primary_key=True)
    amount = db.Column(db.Integer, nullable=False)
    created_at = db.Column(db.DateTime(timezone = True), default=utc_now)

    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    auction_id = db.Column(db.Integer, db.ForeignKey('auctions.id'), nullable=False)

    user = db.relationship("User", back_populates="bids")
    auction = db.relationship("Auction", back_populates="bids")

class Favorite(db.Model):
    __tablename__ = "favorites"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    auction_id = db.Column(db.Integer, db.ForeignKey('auctions.id'), nullable=False)

    __table_args__ = (db.UniqueConstraint('user_id', 'auction_id', name="unique_favorite"),)

    user = db.relationship("User", back_populates="favorites")
    auction = db.relationship("Auction", back_populates="favorites")