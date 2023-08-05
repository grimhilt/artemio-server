from flask import Blueprint, request, Response, jsonify
from flask_cors import cross_origin
from ..models import Playlist, PlaylistFile, File
from .. import db
from datetime import datetime
from sqlalchemy.sql import func
from ..dao.Playlist import PlaylistDao
from flask_login import login_required, current_user
from ..abl.PlaylistAbl import PlaylistAbl
from screen.ScreenManager import ScreenManager
from ..permissions import Perm, permissions

playlist = Blueprint('playlist', __name__)

@playlist.route('/', methods=['POST'])
@login_required
@permissions.require([Perm.CREATE_PLAYLIST])
def create():
    return PlaylistAbl.create(request.get_json())

@playlist.route('/', methods=["GET"])
def list():
    playlists = db.session.query(Playlist).all()

    res = []
    for playlist in playlists:
        p = playlist.as_dict()
        p['last_modified'] = p['last_modified'].isoformat()
        res.append(p)

    return jsonify(res)

@playlist.route('/<int:playlist_id>', methods=["GET"])
def get_playlist(playlist_id):
    (query, files) = PlaylistDao.get_playlist(playlist_id)
    return jsonify({'id': query.id, 'name': query.name, 'files': files})

@playlist.route('/<int:playlist_id>', methods=["POST"])
def add_file(playlist_id):
    data = request.get_json()
    new_playlist_file = PlaylistFile( \
            playlist_id=playlist_id, \
            file_id=data['file_id'], \
            position=data['position'], \
            seconds=data['seconds'] \
            )

    db.session.add(new_playlist_file)
    db.session.flush()
    db.session.commit()

    return jsonify(success=True)
    
@playlist.route('/<int:playlist_id>/order', methods=["POST"])
def change_order(playlist_id):
    data = request.get_json()
    db.session.query(PlaylistFile) \
            .filter(PlaylistFile.file_id == data['file_id']) \
            .filter(PlaylistFile.playlist_id == playlist_id) \
            .update({'position': data['position']})
    db.session.commit()

    return jsonify(success=True)

@playlist.route('/<int:playlist_id>/seconds', methods=["POST"])
def change_seconds(playlist_id):
    data = request.get_json()
    db.session.query(PlaylistFile) \
            .filter(PlaylistFile.file_id == data['file_id']) \
            .filter(PlaylistFile.playlist_id == playlist_id) \
            .update({'seconds': data['seconds']})
    db.session.commit()

    return jsonify(success=True)

@playlist.route('/<int:playlist_id>/remove_file', methods=["POST"])
def remove_file(playlist_id):
    data = request.get_json()
    query = db.session.query(PlaylistFile) \
            .filter(PlaylistFile.file_id == data['file_id']) \
            .filter(PlaylistFile.playlist_id == playlist_id) \
            .first()
    db.session.delete(query)
    db.session.commit()
    return jsonify(success=True)

@playlist.route('/<int:playlist_id>/update', methods=["PUT"])
def update(playlist_id):
    data = request.get_json()
    db.session.query(Playlist) \
            .filter(Playlist.id == playlist_id) \
            .update({'name': data['name']})
    db.session.commit()

    return jsonify(success=True)

@playlist.route('/<int:playlist_id>/activate', methods=["POST"])
def activate(playlist_id):
    screen_manager = ScreenManager.getInstance() 
    screen_manager.activate_playlist(playlist_id)
    return jsonify(success=True)

@playlist.route('/<int:playlist_id>/disactivate', methods=["POST"])
def disactivate(playlist_id):
    screen_manager = ScreenManager.getInstance() 
    screen_manager.disactivate_playlist()
    return jsonify(success=True)