import grpc
from concurrent import futures
import time
import requests
import daztl_service_pb2
import daztl_service_pb2_grpc

API_BASE_URL = "http://localhost:8000/api"

class MusicServiceServicer(daztl_service_pb2_grpc.MusicServiceServicer):
    def RegisterUser(self, request, context):
        payload = {
            "username": request.username,
            "password": request.password,
            "email": request.email
        }
        try:
            res = requests.post(f"{API_BASE_URL}/register/", json=payload, timeout=60)
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

    def LoginUser(self, request, context):
        payload = {
            "username": request.username,
            "password": request.password
        }

        try:
            res = requests.post(f"{API_BASE_URL}/login/", json=payload, timeout=60)
            print("Status Code:", res.status_code)
            print("Response Text:", res.text)

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

    def UpdateProfile(self, request, context):
        headers = {"Authorization": f"Bearer {request.token}"}
        payload = {
            "email": request.email,
            "first_name": request.first_name,
            "last_name": request.last_name
        }
        try:
            res = requests.put(f"{API_BASE_URL}/profile/", headers=headers, json=payload, timeout=60)
            if res.status_code == 200:
                return daztl_service_pb2.GenericResponse(status="success", message="Profile updated successfully")
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
                        artist=song.get("artist"),
                        file_url=song.get("file")
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
            
        except (requests.exceptions.RequestException, ValueError) as e:
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details(f"Backend error: {str(e)}")
            return daztl_service_pb2.SongListResponse()

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
