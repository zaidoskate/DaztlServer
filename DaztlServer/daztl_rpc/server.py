import grpc
from concurrent import futures
import time
import requests
import json
import proto.daztl_service_pb2 as daztl_service_pb2
import proto.daztl_service_pb2_grpc as daztl_service_pb2_grpc


API_BASE_URL = "http://localhost:8000/api"

#python -m grpc_tools.protoc -I./proto --python_out=. --grpc_python_out=. ./proto/daztl_service.proto
#pip install -r requirements.txt


class MusicServiceServicer(daztl_service_pb2_grpc.MusicServiceServicer):
    def RegisterUser(self, request, context):
        print (request)
        payload = {
            "username": request.username,
            "password": request.password,
            "email": request.email,
            "first_name": request.first_name,
            "last_name": request.last_name
        }
        try:
            res = requests.post(f"{API_BASE_URL}/register/", json=payload)
            if res.status_code == 201:
                return daztl_service_pb2.GenericResponse(status="success", message="User registered successfully")
            else:
                return daztl_service_pb2.GenericResponse(status="error", message=res.text)
        except AttributeError as ex:
            return daztl_service_pb2.GenericResponse(status="error", message=f"AttributeError: {str(ex)}")
        except Exception as e:
            return daztl_service_pb2.GenericResponse(status="error", message=str(e))

    def LoginUser(self, request, context):
        payload = {
            "username": request.username,
            "password": request.password
        }

        try:
            res = requests.post(f"{API_BASE_URL}/login/", json=payload)

            if res.status_code == 200:
                tokens = res.json()
                return daztl_service_pb2.LoginResponse(
                    access_token=tokens.get("token"), 
                    refresh_token=tokens.get("refresh")
                )

            else:
                print("Login failed:", res.status_code, res.text)
                context.set_code(grpc.StatusCode.UNAUTHENTICATED)
                context.set_details("Invalid username or password")
                return daztl_service_pb2.LoginResponse()
        except Exception as e:
            print("Error:", str(e))
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details(str(e))
            return daztl_service_pb2.LoginResponse()

    def UpdateProfile(self, request, context):
        headers = {"Authorization": f"Bearer {request.token}"}
        payload = {
            "email": request.email,
            "first_name": request.first_name,
            "last_name": request.last_name,
            "username": request.username,
            "password": request.password
        }
        try:
            res = requests.put(f"{API_BASE_URL}/profile/edit", headers=headers, json=payload)
            if res.status_code == 200:
                return daztl_service_pb2.GenericResponse(status="success", message="Profile updated successfully")
            else:
                return daztl_service_pb2.GenericResponse(status="error", message=res.text)
        except Exception as e:
            return daztl_service_pb2.GenericResponse(status="error", message=str(e))
    def ListSongs(self, request, context):
        try:
            res = requests.get(f"{API_BASE_URL}/songs/")
            if res.status_code == 200:
                songs_data = res.json()
                songs = []
                for song in songs_data:
                    songs.append(daztl_service_pb2.SongResponse(
                        id=song.get("id"),
                        title=song.get("title"),
                        artist=song.get("artist_name") or str(song.get("artist")), 
                        audio_url=song.get("audio_url"),
                        cover_url=song.get("cover_url"),
                        release_date=song.get("release_date", "")
                    ))
                    print(songs)
                return daztl_service_pb2.SongListResponse(songs=songs)
            else:
                context.set_code(grpc.StatusCode.INTERNAL)
                context.set_details("Failed to fetch songs")
                return daztl_service_pb2.SongListResponse()
        except Exception as e:
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details(str(e))
            return daztl_service_pb2.SongListResponse()

    def GetSong(self, request, context):
        try:
            res = requests.get(f"{API_BASE_URL}/songs/{request.id}/")
            if res.status_code == 200:
                song = res.json()
                return daztl_service_pb2.SongResponse(
                    id=song['id'],
                    title=song['title'],
                    artist=song['artist_name'],
                    audio_url=song['audio_url'],
                    cover_url=song.get('cover_url',''),
                    release_date=song.get('release_date',''),
                )
            else:
                context.set_code(grpc.StatusCode.NOT_FOUND)
                context.set_details("Song not found")
                return daztl_service_pb2.SongResponse()
        except Exception as e:
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details(str(e))
            return daztl_service_pb2.SongResponse()
        
    def RefreshToken(self, request, context):
        try:
            payload = {"refresh": request.refresh_token}
            res = requests.post(f"{API_BASE_URL}/refresh/", json=payload)

            if res.status_code == 200:
                tokens = res.json()
                return daztl_service_pb2.LoginResponse(
                    access_token=tokens.get("access") or tokens.get("token"),
                    refresh_token=tokens.get("refresh")
                )
            else:
                context.set_code(grpc.StatusCode.UNAUTHENTICATED)
                context.set_details("Invalid refresh token")
                return daztl_service_pb2.LoginResponse()
        except Exception as e:
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details(str(e))
            return daztl_service_pb2.LoginResponse()
        
    def GetProfile(self, request, context):
        metadata = dict(context.invocation_metadata())
        auth_header = metadata.get("authorization")

        if not auth_header:
            context.abort(grpc.StatusCode.UNAUTHENTICATED, "Missing authorization header")

        headers = {
            "Authorization": auth_header
        }

        response = requests.get("http://localhost:8000/api/profile/", headers=headers)

        if response.status_code == 200:
            data = response.json()
            print(data.get("profile_image_url"))
            return daztl_service_pb2.UserProfileResponse(
                username=data["username"],
                email=data["email"],
                first_name=data["first_name"],
                last_name=data["last_name"],
                profile_image_url=data.get("profile_image_url", "")
                )
        
        elif response.status_code == 401:
            context.abort(grpc.StatusCode.UNAUTHENTICATED, "Token inválido o expirado")
        else:
            context.abort(grpc.StatusCode.INTERNAL, "Error al consultar el perfil")
    def CreatePlaylist(self, request, context):
        headers = {"Authorization": f"Bearer {request.token}"}
        payload = {
            "name": request.name
        }
        try:
            res = requests.post(f"{API_BASE_URL}/playlists/create/", headers=headers, json=payload)
            if res.status_code == 201:
                data = res.json()
                playlist_id = data.get("id", -1)  # suponiendo que la API REST responde con el objeto creado
                message = json.dumps({"id": playlist_id, "message": "Playlist creada exitosamente"})
                return daztl_service_pb2.GenericResponse(
                    status="success",
                    message=message
                )
            else:
                return daztl_service_pb2.GenericResponse(
                    status="error", 
                    message=res.text
                )
        except Exception as e:
            return daztl_service_pb2.GenericResponse(
                status="error", 
                message=str(e)
            )
        except Exception as e:
            return daztl_service_pb2.GenericResponse(
                status="error",
                message=f"Error inesperado: {str(e)}"
            )
    def GetPlaylist(self, request, context):
        try:
            response = requests.get(f"{API_BASE_URL}/playlists/{request.id}/")
            if response.status_code != 200:
                return daztl_service_pb2.PlaylistResponse(id=0, name="Error", songs=[])
            data = response.json()
            songs = []
            for s in data["songs"]:
                songs.append(daztl_service_pb2.SongResponse(
                    id=s["id"],
                    title=s["title"],
                    artist=s["artist"],
                    audio_url=s["audio_url"],
                    cover_url=s["cover_url"],
                    release_date=s["release_date"]
                ))
            return daztl_service_pb2.PlaylistResponse(
                id=data["id"],
                name=data["name"],
                songs=songs
            )
        except Exception as e:
            return daztl_service_pb2.PlaylistResponse(id=0, name=str(e), songs=[])

    def AddSongToPlaylist(self, request, context):
        headers = {"Authorization": f"Bearer {request.token}"}
        data = {"song_id": request.song_id}  # CAMBIO aquí, usar 'song_id' directamente

        try:
            response = requests.post(  # CAMBIO: usar POST en vez de PATCH
                f"{API_BASE_URL}/playlists/{request.playlist_id}/add_song/",  # CAMBIO en la URL
                json=data,
                headers=headers
            )
            if response.status_code == 200:
                return daztl_service_pb2.GenericResponse(status="success", message="Canción agregada a la playlist")
            return daztl_service_pb2.GenericResponse(status="error", message=response.text)
        except Exception as e:
            return daztl_service_pb2.GenericResponse(status="error", message=str(e))

    def GetPlaylistDetail(self, request, context):
        headers = {"Authorization": f"Bearer {request.token}"}
        try:
            response = requests.get(
                f"{API_BASE_URL}/playlists/{request.playlist_id}/",
                headers=headers
            )
            if response.status_code == 200:
                data = response.json()
                playlist_id = data.get("id")
                name = data.get("name")
                songs_data = data.get("songs", [])

                songs = []
                for s in songs_data:
                    song = daztl_service_pb2.SongResponse(
                        id=s["id"],
                        title=s["title"],
                        artist=s["artist_name"],
                        audio_url=s.get("audio_url", ""),
                        cover_url=s.get("cover_url", ""),
                        release_date=s.get("release_date", "")
                    )
                    songs.append(song)

                return daztl_service_pb2.PlaylistDetailResponse(
                    id=playlist_id,
                    name=name,
                    songs=songs,
                    status="success",
                    message="Playlist cargada correctamente"
                )
            else:
                return daztl_service_pb2.PlaylistDetailResponse(
                    status="error",
                    message=f"Error al obtener playlist: {response.text}"
                )
        except Exception as e:
            return daztl_service_pb2.PlaylistDetailResponse(
                status="error",
                message=str(e)
            )
def serve():
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    daztl_service_pb2_grpc.add_MusicServiceServicer_to_server(MusicServiceServicer(), server)
    server.add_insecure_port("[::]:50051")
    server.start()
    print("gRPC server running on port 50051...")
    try:
        while True:
            time.sleep(86400)
    except KeyboardInterrupt:
        server.stop(0)

if __name__ == '__main__':
    serve()
