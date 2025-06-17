import grpc
from concurrent import futures
import time
import requests
import json
import base64
import proto.daztl_service_pb2 as daztl_service_pb2
import proto.daztl_service_pb2_grpc as daztl_service_pb2_grpc

API_BASE_URL = "http://localhost:8000/api"

def make_auth_header(token):
    return {"Authorization": f"Bearer {token}"}

class MusicServiceServicer(daztl_service_pb2_grpc.MusicServiceServicer):
    def RegisterUser(self, request, context):
        payload = {
            "username": request.username,
            "password": request.password,
            "email": request.email,
            "first_name": request.first_name,
            "last_name": request.last_name
        }
        try:
            res = requests.post(f"{API_BASE_URL}/register/", json=payload, timeout=60)
            if res.status_code == 201:
                return daztl_service_pb2.GenericResponse(status="success", message="User registered successfully")
            else:
                return daztl_service_pb2.GenericResponse(status="error", message=res.text)
        except requests.exceptions.Timeout:
            context.set_code(grpc.StatusCode.DEADLINE_EXCEEDED)
            context.set_details("Backend API timeout")
            return daztl_service_pb2.GenericResponse()
            
        except requests.exceptions.ConnectionError:
            context.set_code(grpc.StatusCode.UNAVAILABLE)
            context.set_details("Backend API unreachable")
            return daztl_service_pb2.GenericResponse()
            
        except requests.exceptions.RequestException as e:
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details(f"Backend API error: {str(e)}")
            return daztl_service_pb2.GenericResponse()
        except Exception as e:
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details(f"Backend API error: {str(e)}")
            return daztl_service_pb2.GenericResponse()
        
    def RegisterArtist(self, request, context):
        payload = {
            "username": request.username,
            "password": request.password,
            "email": request.email,
            "first_name": request.first_name,
            "last_name": request.last_name,
            "bio": request.bio
        }
        try:
            res = requests.post(f"{API_BASE_URL}/auth/register-artist/", json=payload, timeout=60)
            if res.status_code == 201:
                return daztl_service_pb2.GenericResponse(status="success", message="User registered successfully")
            else:
                context.set_code(grpc.StatusCode.FAILED_PRECONDITION)
                context.set_details(f"Backend error: {res.text}")
                return daztl_service_pb2.GenericResponse(status="error", message=res.text)
        except requests.exceptions.Timeout:
            context.set_code(grpc.StatusCode.DEADLINE_EXCEEDED)
            context.set_details("Backend API timeout")
            return daztl_service_pb2.GenericResponse()
            
        except requests.exceptions.ConnectionError:
            context.set_code(grpc.StatusCode.UNAVAILABLE)
            context.set_details("Backend API unreachable")
            return daztl_service_pb2.GenericResponse()
            
        except requests.exceptions.RequestException as e:
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details(f"Backend API error: {str(e)}")
            return daztl_service_pb2.GenericResponse()
        except Exception as e:
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details(f"Backend API error: {str(e)}")
            return daztl_service_pb2.GenericResponse()

    def LoginUser(self, request, context):
        payload = {
            "username": request.username,
            "password": request.password
        }

        try:
            res = requests.post(f"{API_BASE_URL}/login/", json=payload, timeout=60)
            if res.status_code == 200:
                tokens = res.json()
                user_info = tokens.get("user_info", {})
                return daztl_service_pb2.LoginResponse(
                    access_token=tokens.get("token"), 
                    refresh_token=tokens.get("refresh"),
                    role=user_info.get("role"),
                    is_artist=user_info.get("is_artist"),
                    user_id=user_info.get("id"),
                    username=user_info.get("username"),
                    artist_id=user_info.get("artist_profile_id")
                )
            else:
                context.set_code(grpc.StatusCode.UNAUTHENTICATED)
                context.set_details("Invalid username or password")
                return daztl_service_pb2.LoginResponse()
        except requests.exceptions.Timeout:
            context.set_code(grpc.StatusCode.DEADLINE_EXCEEDED)
            context.set_details("Backend API timeout")
            return daztl_service_pb2.LoginResponse()
            
        except requests.exceptions.ConnectionError:
            context.set_code(grpc.StatusCode.UNAVAILABLE)
            context.set_details("Backend API unreachable")
            return daztl_service_pb2.LoginResponse()
            
        except requests.exceptions.RequestException as e:
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details(f"Backend API error: {str(e)}")
            return daztl_service_pb2.LoginResponse()
        except Exception as e:
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details(f"Backend API error: {str(e)}")
            return daztl_service_pb2.LoginResponse()

    def UpdateProfile(self, request, context):
        headers = make_auth_header(request.token)
        payload = {}
        
        if request.email:
            payload["email"] = request.email
        if request.first_name:
            payload["first_name"] = request.first_name
        if request.last_name:
            payload["last_name"] = request.last_name
        if request.username:
            payload["username"] = request.username
        if request.password:
            payload["password"] = request.password
        try:
            res = requests.put(f"{API_BASE_URL}/profile/edit", headers=headers, json=payload, timeout=60)
            if res.status_code == 200:
                return daztl_service_pb2.GenericResponse(status="success", message="Profile updated successfully")
            else:
                return daztl_service_pb2.GenericResponse(status="error", message=res.text)
        except requests.exceptions.Timeout:
            context.set_code(grpc.StatusCode.DEADLINE_EXCEEDED)
            context.set_details("Backend API timeout")
            return daztl_service_pb2.GenericResponse()
            
        except requests.exceptions.ConnectionError:
            context.set_code(grpc.StatusCode.UNAVAILABLE)
            context.set_details("Backend API unreachable")
            return daztl_service_pb2.GenericResponse()
            
        except requests.exceptions.RequestException as e:
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details(f"Backend API error: {str(e)}")
            return daztl_service_pb2.GenericResponse()
        except Exception as e:
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details(f"Backend API error: {str(e)}")
            return daztl_service_pb2.GenericResponse()

    def UpdateArtistProfile(self, request, context):
        headers = make_auth_header(request.token)
        payload = {}
        if request.username:
            payload["username"] = request.username
        if request.password:
            payload["password"] = request.password
        if request.bio:
            payload["bio"] = request.bio
        try:
            res = requests.put(f"{API_BASE_URL}/artist/update/", headers=headers, json=payload, timeout=60)
            if res.status_code == 200:
                return daztl_service_pb2.GenericResponse(status="success", message="Artist profile updated successfully")
            else:
                return daztl_service_pb2.GenericResponse(status="error", message=res.text)
        except requests.exceptions.Timeout:
            context.set_code(grpc.StatusCode.DEADLINE_EXCEEDED)
            context.set_details("Backend API timeout")
            return daztl_service_pb2.GenericResponse()
            
        except requests.exceptions.ConnectionError:
            context.set_code(grpc.StatusCode.UNAVAILABLE)
            context.set_details("Backend API unreachable")
            return daztl_service_pb2.GenericResponse()
            
        except requests.exceptions.RequestException as e:
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details(f"Backend API error: {str(e)}")
            return daztl_service_pb2.GenericResponse()
        except Exception as e:
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details(f"Backend API error: {str(e)}")
            return daztl_service_pb2.GenericResponse()
        
    def UploadProfileImage(self, request, context):
        headers = make_auth_header(request.token)
        
        import base64
        image_base64 = base64.b64encode(request.image_data).decode('utf-8')
        
        payload = {
            "image_data": image_base64,
            "filename": request.filename
        }
        
        try:
            res = requests.post(f"{API_BASE_URL}/upload-profile-image-grpc/", 
                            headers=headers, 
                            json=payload, 
                            timeout=60)
            
            if res.status_code == 200:
                response_data = res.json()
                return daztl_service_pb2.UploadProfileImageResponse(
                    status="success",
                    message=response_data.get('message', 'Imagen subida'),
                    image_url=response_data.get('image_url', '')
                )
            else:
                return daztl_service_pb2.UploadProfileImageResponse(
                    status="error",
                    message=res.text
                )
        except Exception as e:
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details(f"Error: {str(e)}")
            return daztl_service_pb2.UploadProfileImageResponse()


    def ListSongs(self, request, context):
        try:
            res = requests.get(f"{API_BASE_URL}/songs/", timeout=60)
            if res.status_code == 200:
                songs_data = res.json()
                songs = []
                for song in songs_data:
                    songs.append(daztl_service_pb2.SongResponse(
                        id=song.get("id"),
                        title=song.get("title"),
                        artist=song.get("artist") or song.get("artist_name", ""),
                        audio_url=song.get("audio_url"),
                        cover_url=song.get("cover_url"),
                        release_date=song.get("release_date", "")
                    ))
                return daztl_service_pb2.SongListResponse(songs=songs)
            else:
                context.set_code(grpc.StatusCode.INTERNAL)
                context.set_details("Failed to fetch songs")
                return daztl_service_pb2.SongListResponse()
        except requests.exceptions.Timeout:
            context.set_code(grpc.StatusCode.DEADLINE_EXCEEDED)
            context.set_details("Backend API timeout")
            return daztl_service_pb2.SongListResponse()
            
        except requests.exceptions.ConnectionError:
            context.set_code(grpc.StatusCode.UNAVAILABLE)
            context.set_details("Backend API unreachable")
            return daztl_service_pb2.SongListResponse()
            
        except requests.exceptions.RequestException as e:
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details(f"Backend API error: {str(e)}")
            return daztl_service_pb2.SongListResponse()
        except Exception as e:
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details(f"Backend API error: {str(e)}")
            return daztl_service_pb2.SongListResponse()

    def GetSong(self, request, context):
        try:
            res = requests.get(f"{API_BASE_URL}/songs/{request.id}/")
            if res.status_code == 200:
                song = res.json()
                return daztl_service_pb2.SongResponse(
                    id=song['id'],
                    title=song['title'],
                    artist=song.get('artist') or song.get('artist_name', ""),
                    audio_url=song['audio_url'],
                    cover_url=song.get('cover_url', ''),
                    release_date=song.get('release_date', '')
                )
            else:
                context.set_code(grpc.StatusCode.NOT_FOUND)
                context.set_details("Song not found")
                return daztl_service_pb2.SongResponse()
        except requests.exceptions.Timeout:
            context.set_code(grpc.StatusCode.DEADLINE_EXCEEDED)
            context.set_details("Backend API timeout")
            return daztl_service_pb2.SongResponse()
            
        except requests.exceptions.ConnectionError:
            context.set_code(grpc.StatusCode.UNAVAILABLE)
            context.set_details("Backend API unreachable")
            return daztl_service_pb2.SongResponse()
            
        except requests.exceptions.RequestException as e:
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details(f"Backend API error: {str(e)}")
            return daztl_service_pb2.SongResponse()
        except Exception as e:
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details(f"Backend API error: {str(e)}")
            return daztl_service_pb2.SongResponse()

    def RefreshToken(self, request, context):
        try:
            payload = {"refresh": request.refresh_token}
            res = requests.post(f"{API_BASE_URL}/refresh/", json=payload, timeout=60)
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
        except requests.exceptions.Timeout:
            context.set_code(grpc.StatusCode.DEADLINE_EXCEEDED)
            context.set_details("Backend API timeout")
            return daztl_service_pb2.LoginResponse()
            
        except requests.exceptions.ConnectionError:
            context.set_code(grpc.StatusCode.UNAVAILABLE)
            context.set_details("Backend API unreachable")
            return daztl_service_pb2.LoginResponse()
            
        except requests.exceptions.RequestException as e:
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details(f"Backend API error: {str(e)}")
            return daztl_service_pb2.LoginResponse()
        except Exception as e:
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details(f"Backend API error: {str(e)}")
            return daztl_service_pb2.LoginResponse()

    def GetProfile(self, request, context):
        metadata = dict(context.invocation_metadata())
        auth_header = metadata.get("authorization")

        if not auth_header:
            context.abort(grpc.StatusCode.UNAUTHENTICATED, "Missing authorization header")

        headers = {"Authorization": auth_header}
        response = requests.get(f"{API_BASE_URL}/profile/", headers=headers)

        if response.status_code == 200:
            data = response.json()
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
    
    def GetArtistProfile(self, request, context):
        metadata = dict(context.invocation_metadata())
        auth_header = metadata.get("authorization")

        if not auth_header:
            context.abort(grpc.StatusCode.UNAUTHENTICATED, "Missing authorization header")

        headers = {"Authorization": auth_header}
        response = requests.get(f"{API_BASE_URL}/artist/profile/", headers=headers)

        if response.status_code == 200:
            data = response.json()
            return daztl_service_pb2.ArtistProfileResponse(
                username=data["username"],
                email=data["email"],
                first_name=data["first_name"],
                last_name=data["last_name"],
                profile_image_url=data.get("profile_image_url", ""),
                bio=data.get("bio", ""),
                artist_profile_id=data.get("artist_profile_id", 0)
            )
        elif response.status_code == 401:
            context.abort(grpc.StatusCode.UNAUTHENTICATED, "Token inválido o expirado")
        else:
            context.abort(grpc.StatusCode.INTERNAL, "Error al consultar el perfil de artista")


    def CreatePlaylist(self, request, context):
        headers = make_auth_header(request.token)
        payload = {"name": request.name}
        try:
            res = requests.post(f"{API_BASE_URL}/playlists/create/", headers=headers, json=payload, timeout=60)
            if res.status_code == 201:
                data = res.json()
                playlist_id = data.get("id", -1)

                if request.cover_url:
                    image_data = base64.b64decode(request.cover_url)
                    files = {'cover': ('cover.jpg', image_data, 'image/jpeg')}
                    res_upload = requests.post(
                        f"{API_BASE_URL}/playlists/{playlist_id}/upload_cover/",
                        headers=headers,
                        files=files,
                        timeout=60
                    )
                    if res_upload.status_code != 200:
                        return daztl_service_pb2.GenericResponse(
                            status="error",
                            message=f"Playlist creada pero fallo al subir imagen: {res_upload.text}"
                        )

                message = json.dumps({"id": playlist_id, "message": "Playlist creada exitosamente"})
                return daztl_service_pb2.GenericResponse(status="success", message=message)

            else:
                return daztl_service_pb2.GenericResponse(status="error", message=res.text)

        except requests.exceptions.Timeout:
            context.set_code(grpc.StatusCode.DEADLINE_EXCEEDED)
            context.set_details("Backend API timeout")
            return daztl_service_pb2.GenericResponse()

        except requests.exceptions.ConnectionError:
            context.set_code(grpc.StatusCode.UNAVAILABLE)
            context.set_details("Backend API unreachable")
            return daztl_service_pb2.GenericResponse()

        except requests.exceptions.RequestException as e:
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details(f"Backend API error: {str(e)}")
            return daztl_service_pb2.GenericResponse()

        except Exception as e:
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details(f"Backend API error: {str(e)}")
            return daztl_service_pb2.GenericResponse()


    def GetPlaylist(self, request, context):
        try:
            # Obtener el token de los metadatos
            token = self.get_token_from_metadata(context)
            
            headers = {
                "Authorization": f"Bearer {token}"
            }
            
            response = requests.get(
                f"{API_BASE_URL}/playlists/{request.id}/",
                headers=headers,
                timeout=60
            )
            
            if response.status_code != 200:
                context.set_code(grpc.StatusCode.PERMISSION_DENIED if response.status_code == 401 
                            else grpc.StatusCode.INTERNAL)
                return daztl_service_pb2.PlaylistResponse(id=0, name="Error", songs=[])
                
            data = response.json()
            songs = [
                daztl_service_pb2.SongResponse(
                    id=s["id"],
                    title=s["title"],
                    artist=s.get("artist") or s.get("artist_name", ""),
                    audio_url=s["audio_url"],
                    cover_url=s["cover_url"],
                    release_date=s["release_date"]
                ) for s in data["songs"]
            ]
            return daztl_service_pb2.PlaylistResponse(
                id=data["id"],
                name=data["name"],
                songs=songs
            )
        except Exception as e:
            context.set_code(grpc.StatusCode.INTERNAL)
            return daztl_service_pb2.PlaylistResponse(id=0, name=str(e), songs=[])

    def AddSongToPlaylist(self, request, context):
        headers = make_auth_header(request.token)
        data = {"song_id": request.song_id}
        try:
            response = requests.post(
                f"{API_BASE_URL}/playlists/{request.playlist_id}/add_song/",
                json=data,
                headers=headers,
                timeout=60
            )
            if response.status_code == 200:
                return daztl_service_pb2.GenericResponse(status="success", message="Canción agregada a la playlist")
            return daztl_service_pb2.GenericResponse(status="error", message=response.text)
        except requests.exceptions.Timeout:
            context.set_code(grpc.StatusCode.DEADLINE_EXCEEDED)
            context.set_details("Backend API timeout")
            return daztl_service_pb2.GenericResponse()
            
        except requests.exceptions.ConnectionError:
            context.set_code(grpc.StatusCode.UNAVAILABLE)
            context.set_details("Backend API unreachable")
            return daztl_service_pb2.GenericResponse()
            
        except requests.exceptions.RequestException as e:
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details(f"Backend API error: {str(e)}")
            return daztl_service_pb2.GenericResponse()
        
        except Exception as e:
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details(f"Backend API error: {str(e)}")
            return daztl_service_pb2.GenericResponse()

    def GetPlaylistDetail(self, request, context):
        headers = make_auth_header(request.token)
        try:
            response = requests.get(f"{API_BASE_URL}/playlists/{request.playlist_id}/", headers=headers, timeout=60)
            if response.status_code == 200:
                data = response.json()
                songs = [
                    daztl_service_pb2.SongResponse(
                        id=s["id"],
                        title=s["title"],
                        artist=s.get("artist_name", ""),
                        audio_url=s.get("audio_url", ""),
                        cover_url=s.get("cover_url", ""),
                        release_date=s.get("release_date", "")
                    ) for s in data.get("songs", [])
                ]
                return daztl_service_pb2.PlaylistDetailResponse(
                    id=data["id"],
                    name=data["name"],
                    songs=songs,
                    status="success",
                    message="Playlist cargada correctamente"
                )
            else:
                return daztl_service_pb2.PlaylistDetailResponse(
                    status="error",
                    message=f"Error al obtener playlist: {response.text}"
                )
        except requests.exceptions.Timeout:
            context.set_code(grpc.StatusCode.DEADLINE_EXCEEDED)
            context.set_details("Backend API timeout")
            return daztl_service_pb2.PlaylistDetailResponse()
            
        except requests.exceptions.ConnectionError:
            context.set_code(grpc.StatusCode.UNAVAILABLE)
            context.set_details("Backend API unreachable")
            return daztl_service_pb2.PlaylistDetailResponse()
            
        except requests.exceptions.RequestException as e:
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details(f"Backend API error: {str(e)}")
            return daztl_service_pb2.PlaylistDetailResponse()
        
        except Exception as e:
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details(f"Backend API error: {str(e)}")
            return daztl_service_pb2.PlaylistDetailResponse()
        
    def ListPlaylists(self, request, context):
        try:
            token = request.token
            headers = {"Authorization": f"Bearer {token}"}
            
            response = requests.get("http://localhost:8000/api/playlists/", headers=headers, timeout=60)

            if response.status_code == 200:
                data = response.json()
                playlist_messages = []

                for playlist in data:
                    cover_url = playlist.get("cover") or ""
                    songs = []
                    
                    if 'songs' in playlist:
                        for song in playlist['songs']:
                            song_msg = daztl_service_pb2.SongResponse(
                                id=song['id'],
                                title=song['title'],
                                artist=song['artist_name'],
                                audio_url=song['audio_url'] or "",
                                cover_url=song['cover_url'] or "",
                                release_date=song['release_date'] or ""
                            )
                            songs.append(song_msg)
                    
                    playlist_msg = daztl_service_pb2.PlaylistResponse(
                        id=playlist["id"],
                        name=playlist["name"],
                        cover_url=cover_url,
                        songs=songs  # Añadir las canciones aquí
                    )
                    playlist_messages.append(playlist_msg)

                return daztl_service_pb2.PlaylistListResponse(playlists=playlist_messages)

            else:
                print(response)
                context.set_code(grpc.StatusCode.UNAUTHENTICATED)
                context.set_details("No autorizado para obtener playlists")
                return daztl_service_pb2.PlaylistListResponse()

        except requests.exceptions.Timeout:
            context.set_code(grpc.StatusCode.DEADLINE_EXCEEDED)
            context.set_details("Backend API timeout")
            return daztl_service_pb2.PlaylistListResponse()
            
        except requests.exceptions.ConnectionError:
            context.set_code(grpc.StatusCode.UNAVAILABLE)
            context.set_details("Backend API unreachable")
            return daztl_service_pb2.PlaylistListResponse()
            
        except requests.exceptions.RequestException as e:
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details(f"Backend API error: {str(e)}")
            return daztl_service_pb2.PlaylistListResponse()
        
        except Exception as e:
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details(f"Backend API error: {str(e)}")
            return daztl_service_pb2.PlaylistListResponse()
    @staticmethod
    def get_token_from_metadata(context):
        for key, value in context.invocation_metadata():
            if key == 'authorization':
                return value.replace('Bearer ', '')
        return None

    def SearchSongs(self, request, context):
        query = request.query
        token = self.get_token_from_metadata(context)
        try:
            response = requests.get(
                f"{API_BASE_URL}/songs/",
                headers={"Authorization": f"Bearer {token}"},
                params={"q": query}
            )
            if response.status_code == 200:
                songs_data = response.json()
                songs = [
                    daztl_service_pb2.SongResponse(
                        id=s["id"],
                        title=s["title"],
                        artist=s.get("artist_name", ""),
                        audio_url=s["audio_url"],
                        cover_url=s["cover_url"],
                        release_date=s["release_date"]
                    ) for s in songs_data
                ]
                return daztl_service_pb2.SongListResponse(songs=songs)
            else:
                context.abort(grpc.StatusCode.INTERNAL, "Error al buscar canciones en el backend")
        except Exception as e:
            context.abort(grpc.StatusCode.INTERNAL, f"Excepción: {str(e)}")


    def GlobalSearch(self, request, context):
        query = request.query
        token = self.get_token_from_metadata(context)

        try:
            response = requests.get(
                f"{API_BASE_URL}/search/",
                headers={"Authorization": f"Bearer {token}"},
                params={"q": query}
            )

            if response.status_code != 200:
                context.abort(grpc.StatusCode.INTERNAL, "Error al buscar contenido en el backend")

            data = response.json()

            songs = [
                daztl_service_pb2.SongResponse(
                    id=s["id"],
                    title=s["title"],
                    artist=s.get("artist_name", ""),
                    audio_url=s["audio_url"],
                    cover_url=s["cover_url"],
                    release_date=s["release_date"]
                ) for s in data.get("songs", [])
            ]

            albums = [
                daztl_service_pb2.AlbumResponse(
                    id=a["id"],
                    title=a["title"]
                ) for a in data.get("albums", [])
            ]

            artists = [
                daztl_service_pb2.ArtistResponse(
                    id=ar["id"],
                    name=ar["user"]["username"]
                ) for ar in data.get("artists", [])
            ]

            playlists = [
                daztl_service_pb2.PlaylistResponse(
                    id=p["id"],
                    name=p["name"],
                    songs=[
                        daztl_service_pb2.SongResponse(
                            id=s["id"],
                            title=s["title"],
                            artist=s.get("artist", ""),
                            audio_url=s["audio_url"],
                            cover_url=s["cover_url"],
                            release_date=s["release_date"]
                        ) for s in p.get("songs", [])
                    ]
                ) for p in data.get("playlists", [])
            ]

            return daztl_service_pb2.GlobalSearchResponse(
                songs=songs,
                albums=albums,
                artists=artists,
                playlists=playlists
            )

        except Exception as e:
            context.abort(grpc.StatusCode.INTERNAL, f"Excepción: {str(e)}")

    def ListAlbums(self, request, context):
        try:
            response = requests.get("http://localhost:8000/api/albums/", timeout=60)

            if response.status_code == 200:
                data = response.json()
                album_messages = []

                for album in data:
                    cover_url = album.get("cover_image") or ""
                    artist_name = album.get("artist_name") or ""

                    album_msg = daztl_service_pb2.AlbumResponse(
                        id=album.get("id"),
                        title=album.get("title"),
                        artist_name=artist_name,
                        cover_url=cover_url
                    )
                    album_messages.append(album_msg)

                return daztl_service_pb2.AlbumListResponse(albums=album_messages)

            else:
                context.set_code(grpc.StatusCode.INTERNAL)
                context.set_details("Failed to fetch albums")
                return daztl_service_pb2.AlbumListResponse()

        except requests.exceptions.Timeout:
            context.set_code(grpc.StatusCode.DEADLINE_EXCEEDED)
            context.set_details("Backend API timeout")
            return daztl_service_pb2.AlbumListResponse()

        except requests.exceptions.ConnectionError:
            context.set_code(grpc.StatusCode.UNAVAILABLE)
            context.set_details("Backend API unreachable")
            return daztl_service_pb2.AlbumListResponse()

        except requests.exceptions.RequestException as e:
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details(f"Backend API error: {str(e)}")
            return daztl_service_pb2.AlbumListResponse()

        except Exception as e:
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details(f"Backend API error: {str(e)}")
            return daztl_service_pb2.AlbumListResponse()

    def ListArtists(self, request, context):
        try:
            response = requests.get("http://localhost:8000/api/artists/", timeout=60)

            if response.status_code == 200:
                data = response.json()
                artist_messages = []

                for artist in data:
                    artist_messages.append(daztl_service_pb2.ArtistResponse(
                        id=artist.get("id"),
                        name=artist.get("user", {}).get("username", ""),
                        profile_picture=artist.get("profile_picture", "")
                    ))

                return daztl_service_pb2.ArtistListResponse(artists=artist_messages)

            else:
                context.set_code(grpc.StatusCode.INTERNAL)
                context.set_details("Failed to fetch artists")
                return daztl_service_pb2.ArtistListResponse()

        except requests.exceptions.Timeout:
            context.set_code(grpc.StatusCode.DEADLINE_EXCEEDED)
            context.set_details("Backend API timeout")
            return daztl_service_pb2.ArtistListResponse()

        except requests.exceptions.ConnectionError:
            context.set_code(grpc.StatusCode.UNAVAILABLE)
            context.set_details("Backend API unreachable")
            return daztl_service_pb2.ArtistListResponse()

        except requests.exceptions.RequestException as e:
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details(f"Backend API error: {str(e)}")
            return daztl_service_pb2.ArtistListResponse()

        except Exception as e:
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details(f"Backend API error: {str(e)}")
            return daztl_service_pb2.ArtistListResponse()

    def LikeArtist(self, request, context):
        try:
            headers = make_auth_header(request.token)
            artist_id = request.artist_id
            
            # Primero verificamos si ya existe el like
            res = requests.get(
                f"{API_BASE_URL}/artists/{artist_id}/like/status/",
                headers=headers,
                timeout=60
            )
            
            if res.status_code == 200:
                is_liked = res.json().get("liked", False)
                
                if is_liked:
                    # Si ya está liked, hacemos unlike
                    res = requests.delete(
                        f"{API_BASE_URL}/artists/{artist_id}/like/",
                        headers=headers,
                        timeout=60
                    )
                else:
                    # Si no está liked, hacemos like
                    res = requests.post(
                        f"{API_BASE_URL}/artists/{artist_id}/like/",
                        headers=headers,
                        timeout=60
                    )
                
                if res.status_code in (200, 201):
                    return daztl_service_pb2.GenericResponse(
                        status="success",
                        message="Like status updated successfully"
                    )
                else:
                    context.set_code(grpc.StatusCode.INTERNAL)
                    context.set_details(f"Error updating like: {res.text}")
                    return daztl_service_pb2.GenericResponse()
                    
            else:
                context.set_code(grpc.StatusCode.INTERNAL)
                context.set_details("Failed to check like status")
                return daztl_service_pb2.GenericResponse()
                
        except requests.exceptions.Timeout:
            context.set_code(grpc.StatusCode.DEADLINE_EXCEEDED)
            context.set_details("Backend API timeout")
            return daztl_service_pb2.GenericResponse()
            
        except requests.exceptions.ConnectionError:
            context.set_code(grpc.StatusCode.UNAVAILABLE)
            context.set_details("Backend API unreachable")
            return daztl_service_pb2.GenericResponse()
            
        except requests.exceptions.RequestException as e:
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details(f"Backend API error: {str(e)}")
            return daztl_service_pb2.GenericResponse()
        
        except Exception as e:
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details(f"Backend API error: {str(e)}")
            return daztl_service_pb2.GenericResponse()

    def IsArtistLiked(self, request, context):
        try:
            headers = make_auth_header(request.token)
            artist_id = request.artist_id
            
            res = requests.get(
                f"{API_BASE_URL}/artists/{artist_id}/like/status/",
                headers=headers,
                timeout=60
            )
            
            if res.status_code == 200:
                is_liked = res.json().get("liked", False)
                return daztl_service_pb2.LikeStatusResponse(is_liked=is_liked)
            else:
                context.set_code(grpc.StatusCode.INTERNAL)
                context.set_details("Failed to get like status")
                return daztl_service_pb2.LikeStatusResponse()
                
        except requests.exceptions.Timeout:
            context.set_code(grpc.StatusCode.DEADLINE_EXCEEDED)
            context.set_details("Backend API timeout")
            return daztl_service_pb2.LikeStatusResponse()
            
        except requests.exceptions.ConnectionError:
            context.set_code(grpc.StatusCode.UNAVAILABLE)
            context.set_details("Backend API unreachable")
            return daztl_service_pb2.LikeStatusResponse()
            
        except requests.exceptions.RequestException as e:
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details(f"Backend API error: {str(e)}")
            return daztl_service_pb2.LikeStatusResponse()
        
        except Exception as e:
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details(f"Backend API error: {str(e)}")
            return daztl_service_pb2.LikeStatusResponse()

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
