from app.infrastructure.database import db

class Community(db.Model):
    __tablename__ = "pool_group"
    
    idCommunity = db.Column('id_group', db.Integer, primary_key=True, autoincrement=True)
    name = db.Column('name', db.String(100), nullable=False)
    invitationCode = db.Column('invitation_code', db.String(50), unique=True)
    
    maxMembers      = db.Column('max_members',      db.Integer,      nullable=True)
    favoriteTeam    = db.Column('favorite_team',    db.String(100),  nullable=True)
    favoritePlayers = db.Column('favorite_players', db.String(300),  nullable=True)
    description     = db.Column('description',      db.String(500),  nullable=True)
    icon            = db.Column('icon',             db.Text,         nullable=True)
    banner          = db.Column('banner',           db.Text,         nullable=True)

    users = db.relationship('User', secondary='user_group', backref='communities')

user_community = db.Table('user_group',
    db.Column('id_user', db.Integer, db.ForeignKey('USER.iduser'), primary_key=True),
    db.Column('id_group', db.Integer, db.ForeignKey('pool_group.id_group'), primary_key=True),
    db.Column('is_admin', db.Boolean, default=False)
)