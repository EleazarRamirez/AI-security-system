from app.cameras.camera_worker import CameraWorker


class CameraRegistry:

    def __init__(self):

        self.cameras = {}

    def add_camera(
        self,
        camera_id,
        name,
        rtsp_url
    ):

        if camera_id in self.cameras:
            return

        worker = CameraWorker(
            camera_id,
            name,
            rtsp_url
        )

        worker.start()

        self.cameras[camera_id] = worker

    def remove_camera(self, camera_id):

        if camera_id not in self.cameras:
            return

        self.cameras[camera_id].stop()

        del self.cameras[camera_id]

    def get_camera(self, camera_id):

        return self.cameras.get(camera_id)

    def list_cameras(self):

        return list(self.cameras.keys())


camera_registry = CameraRegistry()