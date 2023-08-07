from flask import jsonify, request
from ..models import Playlist, PlaylistFile, File
from .. import db
from datetime import datetime
from ..dao.Playlist import PlaylistDao
from flask_login import current_user
from screen.ScreenManager import ScreenManager

class PlaylistAbl:
    @staticmethod
    def create(data):
        new_playlist = Playlist(name=data['name'], owner_id=current_user.as_dict()['id'])
        db.session.add(new_playlist)
        db.session.flush()
        db.session.commit()

        res = new_playlist.as_dict()
        res['last_modified'] = res['last_modified'].isoformat()
        return jsonify(res)

    @staticmethod
    def update(playlist_id, data):
        db.session.query(Playlist) \
                .filter(Playlist.id == playlist_id) \
                .update({'name': data['name']})
        db.session.commit()
        return jsonify(success=True)

    @staticmethod
    def get_playlist(playlist_id):
        (query, files) = PlaylistDao.get_playlist(playlist_id)
        return jsonify({'id': query.id, 'name': query.name, 'owner_id': query.owner_id, 'files': files})

    @staticmethod
    def list():
        playlists = db.session.query(Playlist).all()
        res = []
        for playlist in playlists:
            p = playlist.as_dict()
            p['last_modified'] = p['last_modified'].isoformat()
            res.append(p)

        return jsonify(res)


    # EDIT PLAYLIST CONTENT
    @staticmethod
    def add_file(playlist_id, data):
        data = request.get_json()
        new_playlist_file = PlaylistFile( \
                playlist_id=playlist_id, \
                file_id=data['file_id'], \
                position=data['position'], \
                seconds=data['seconds'] \
                )

        db.session.add(new_playlist_file)
        db.session.commit()
        return jsonify(success=True)

    @staticmethod
    def change_order(playlist_id, data):
        db.session.query(PlaylistFile) \
                .filter(PlaylistFile.file_id == data['file_id']) \
                .filter(PlaylistFile.playlist_id == playlist_id) \
                .update({'position': data['position']})
        db.session.commit()
        return jsonify(success=True)

    @staticmethod
    def change_seconds(playlist_id, data):
        db.session.query(PlaylistFile) \
                .filter(PlaylistFile.file_id == data['file_id']) \
                .filter(PlaylistFile.playlist_id == playlist_id) \
                .update({'seconds': data['seconds']})
        db.session.commit()
        return jsonify(success=True)

    @staticmethod
    def remove_file(playlist_id, data):
        data = request.get_json()
        query = db.session.query(PlaylistFile) \
                .filter(PlaylistFile.file_id == data['file_id']) \
                .filter(PlaylistFile.playlist_id == playlist_id) \
                .first()
        db.session.delete(query)
        db.session.commit()
        return jsonify(success=True)
