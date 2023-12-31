from . import db
from flask_login import UserMixin
from sqlalchemy.sql import func

class PlaylistFile(db.Model):
    __tablename__ = 'PlaylistFile'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    playlist_id = db.Column(db.Integer, db.ForeignKey('playlist.id'))
    file_id = db.Column(db.Integer, db.ForeignKey('file.id'))
    position = db.Column(db.Integer)
    seconds = db.Column(db.Integer, default=10)
    playlist = db.relationship('Playlist', back_populates='playlist_files')
    file = db.relationship('File', back_populates='playlist_files')

    def as_dict(self):
       return {c.name: getattr(self, c.name) for c in self.__table__.columns}

class File(db.Model):
    id = db.Column(db.Integer, primary_key = True, autoincrement=True)
    name = db.Column(db.String(150))
    type = db.Column(db.String(255)) # maximum length of mimetype
    playlist_files = db.relationship('PlaylistFile', back_populates='file')

    def as_dict(self):
       return {c.name: getattr(self, c.name) for c in self.__table__.columns}

class PlaylistView(db.Model):
    __tablename__ = 'PlaylistView'
    playlist_id = db.Column(db.Integer, db.ForeignKey('playlist.id'), primary_key=True)
    role_id = db.Column(db.Integer, db.ForeignKey('role.id'), primary_key=True)

class PlaylistEdit(db.Model):
    __tablename__ = 'PlaylistEdit'
    playlist_id = db.Column(db.Integer, db.ForeignKey('playlist.id'), primary_key=True)
    role_id = db.Column(db.Integer, db.ForeignKey('role.id'), primary_key=True)

class Playlist(db.Model):
    id = db.Column(db.Integer, primary_key = True, autoincrement=True)
    name = db.Column(db.String(150))
    owner_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    last_modified = db.Column(db.DateTime(timezone=True), default=func.now())
    view = db.relationship('Role', secondary='PlaylistView', back_populates='playlists_view')
    edit = db.relationship('Role', secondary='PlaylistEdit', back_populates='playlists_edit')
    playlist_files = db.relationship('PlaylistFile', order_by='PlaylistFile.position', back_populates='playlist')

    def as_dict_with_roles(self):
        res = self.as_dict()
        res['view'] = [role.as_dict() for role in self.view]
        res['edit'] = [role.as_dict() for role in self.edit]
        return res


    def as_dict(self):
       return {c.name: getattr(self, c.name) for c in self.__table__.columns}

class UserRole(db.Model):
    __tablename__ = 'UserRole'
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), primary_key=True)
    role_id = db.Column(db.Integer, db.ForeignKey('role.id'), primary_key=True)

class ParentRole(db.Model):
    __tablename__ = 'ParentRole'
    parent_id = db.Column(db.Integer, db.ForeignKey('role.id'), primary_key=True)
    child_id = db.Column(db.Integer, db.ForeignKey('role.id'), primary_key=True)

    def as_dict(self):
       return {c.name: getattr(self, c.name) for c in self.__table__.columns}


class Role(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), default=None)
    permissions = db.Column(db.Integer, default=0)
    parent_id = db.Column(db.Integer, db.ForeignKey('role.id'), default=None)
    children = db.relationship('Role', secondary="ParentRole",
                            primaryjoin=id == ParentRole.parent_id,
                            secondaryjoin=id == ParentRole.child_id,
                            backref='parents')
    
    users = db.relationship('User', secondary='UserRole', back_populates='roles')
    playlists_view = db.relationship('Playlist', secondary='PlaylistView', back_populates='view')
    playlists_edit = db.relationship('Playlist', secondary='PlaylistEdit', back_populates='edit')

    def as_full_dict(self):
        res = self.as_dict()
        res['parents'] = [parent.as_dict() for parent in self.parents]
        res['children'] = [child.as_dict() for child in self.children]
        return res

    def as_dict(self):
        return {c.name: getattr(self, c.name) for c in self.__table__.columns}

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key = True, autoincrement=True)
    login = db.Column(db.String(150))
    password = db.Column(db.String(150))
    roles = db.relationship('Role', secondary='UserRole', back_populates='users')

    def as_dict(self):
        res = self.as_dict_unsafe()
        res['roles'] = [role.as_full_dict() for role in self.roles]
        del res['password']
        return res

    def as_dict_unsafe(self):
       return {c.name: getattr(self, c.name) for c in self.__table__.columns}

