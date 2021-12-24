from flask import Flask, make_response
from flask_restful import Api, Resource, abort
from yt_dlp import YoutubeDL

app = Flask(__name__)
api = Api(app)


def invalid_video_response(video_id):
    message = {"success": False, "id": video_id, "message": "Video doesn't exit"}
    return make_response(message, 404)


def get_video_data(video_info):
    video_data = {}
    video_data["title"] = video_info["title"]
    video_data["description"] = video_info["description"]
    video_data["dur"] = video_info["duration"]
    formats = video_info["formats"]
    video_formats = []
    f1440 = False
    f2160 = False
    for _format in formats:
        fid = _format["format_id"]
        flist = {
            "139": None,
            "249": None,
            "160": "144p",
            "133": "240p",
            "134": "360p",
            "135": "480p",
            "136": "720p",
            "299": "1080p",
            "400": "1440p",
            "401": "2160p",
            "278": "144p",
            "242": "240p",
            "243": "360p",
            "244": "480p",
            "247": "720p",
            "303": "1080p",
            "271": "1440p",
            "308": "1440p",
            "313": "2160p",
            "315": "2160p",
            "17": "144p",
            "18": "360p",
            "22": "720p",
        }
        if fid not in flist:
            continue
        if fid in ["271", "308"]:
            if f1440:
                continue
            else:
                f1440 = True
        if fid in ["313", "315"]:
            if f2160:
                continue
            else:
                f2160 = True

        video_format = {
            "id": fid,
            "ext": _format["ext"],
            "size": _format["filesize"],
            "quality": flist[fid],
            "url": _format["url"],
        }
        video_formats.append(video_format)
    video_data["formats"] = video_formats
    return video_data


class YoutubeVideo(Resource):
    def get(self, video_id):
        ytdl = YoutubeDL()
        try:
            video_info = ytdl.extract_info(video_id, download=False)
        except:
            message = {
                "success": False,
                "id": video_id,
                "message": "Video doesn't exist.",
            }
            abort(404, message=message)
        video_data = get_video_data(video_info)
        video_data["thumbnail"] = f"https://i.ytimg.com/vi/{video_id}/hqdefault.jpg"
        video_response = {"success": True, "id": video_id, "data": video_data}
        return video_response


class YoutubePlaylist(Resource):
    def get(self, playlist_id):
        ytdl = YoutubeDL({"extract_flat": True})
        try:
            playlist_link = f"https://youtube.com/playlist?list={playlist_id}"
            playlist_info = ytdl.extract_info(playlist_link)
        except:
            message = {
                "success": False,
                "id": playlist_id,
                "message": "Playlist doesn't exist.",
            }
            abort(404, message=message)
        
        print(playlist_info)
        if not playlist_info["thumbnails"]:
            message = {
                "success": False,
                "id": playlist_id,
                "message": "Playlist doesn't exist.",
            }
            abort(404, message=message)

        playlist_data = {}
        playlist_data["title"]= playlist_info["title"]
        playlist_data["channel"]= playlist_info["channel"]
        playlist_data["description"]= playlist_info["description"]
        videos = []
        for entry in playlist_info["entries"]:
            video = {}
            video["id"], video["title"], video["url"], video["dur"] = entry["id"], entry["title"], entry["url"], entry["duration"] 
            video["thumbnail"] = f"https://i.ytimg.com/vi/{video['id']}/hqdefault.jpg"
            videos.append(video)
        playlist_data["videos"] = videos
        playlist_data["totalVideos"] = len(videos)
        playlist_response = {"success": True, "id": playlist_id, "data": playlist_data}
        return playlist_response


api.add_resource(YoutubeVideo, "/youtube/video/<string:video_id>")
api.add_resource(YoutubePlaylist, "/youtube/playlist/<string:playlist_id>")


if __name__ == "__main__":
    app.run()
