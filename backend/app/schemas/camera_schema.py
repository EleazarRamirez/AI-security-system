from pydantic import BaseModel, field_validator


class CameraCreate(BaseModel):
    name: str
    rtsp_url: str

    @field_validator("rtsp_url")
    @classmethod
    def validate_url(cls, v: str) -> str:
        """Acepta: '0' (webcam local), http://, rtsp://"""
        if v == "0":
            return v
        if v.startswith(("http://", "https://", "rtsp://")):
            return v
        raise ValueError(
            "rtsp_url debe ser '0' (webcam local), "
            "una URL http:// o rtsp://"
        )


class CameraTest(BaseModel):
    """Body para el endpoint /cameras/test"""
    rtsp_url: str
