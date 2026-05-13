from app.infrastructure.database import db

user_community = db.Table('USER_COMMUNITY',
    db.Column('USER_user_id', db.Integer, db.ForeignKey('USER.user_id'), primary_key=True),
    db.Column('COMMUNITY_community_id', db.Integer, db.ForeignKey('COMMUNITY.community_id'), primary_key=True),
    db.Column('is_admin', db.String(1), nullable=False, default='0'),
    extend_existing=True
)

class Community(db.Model):
    __tablename__ = "COMMUNITY"
    
    community_id = db.Column('community_id', db.Integer, primary_key=True, autoincrement=True)
    name = db.Column('name', db.String(200), nullable=False)
    invitation_code = db.Column('invitation_code', db.Integer, nullable=False, unique=True)
    users = db.relationship('User', secondary='USER_COMMUNITY', backref='communities')

    def save(self):
        db.session.add(self)
        db.session.commit()
        return self
