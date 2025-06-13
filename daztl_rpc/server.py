import grpc
from concurrent import futures
import time
import requests
import proto.daztl_service_pb2 as daztl_service_pb2
import proto.daztl_service_pb2_grpc as daztl_service_pb2_grpc


API_BASE_URL = "http://localhost:8000/api"

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
            "last_name": request.last_name
        }
        try:
            res = requests.put(f"{API_BASE_URL}/profile/", headers=headers, json=payload)
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
