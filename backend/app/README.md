# Camera AI API — Guía de uso

## Arrancar el servidor
```bash
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

---

## Endpoints

### Probar conectividad (sin guardar)
```http
POST /cameras/test
Content-Type: application/json

{ "rtsp_url": "http://192.168.1.100:8080/video" }
```

### Agregar cámara
```http
POST /cameras
Content-Type: application/json

{ "name": "Entrada", "rtsp_url": "http://192.168.1.100:8080/video" }
```

### Ver stream en vivo
Abre en el navegador:
```
http://localhost:8000/cameras/1/stream
```
O en HTML:
```html
<img src="http://localhost:8000/cameras/1/stream" />
```

### Listar eventos detectados
```
GET /events?limit=20&camera_name=Entrada
```

---

## Cámaras WiFi / IP para pruebas

### Opción 1 — IP Webcam (Android, gratis)
1. Instala **IP Webcam** desde Google Play.
2. Toca **Iniciar servidor** (abre en `http://192.168.x.x:8080`).
3. La URL de video es: `http://192.168.x.x:8080/video`

```json
{ "name": "Móvil Android", "rtsp_url": "http://192.168.x.x:8080/video" }
```

### Opción 2 — DroidCam (Android/iOS, gratis)
1. Instala **DroidCam** en el móvil.
2. La URL de video es: `http://192.168.x.x:4747/video`

```json
{ "name": "DroidCam", "rtsp_url": "http://192.168.x.x:4747/video" }
```

### Opción 3 — Cámara RTSP (routers, NVR, Tapo, etc.)
```json
{ "name": "Tapo C200", "rtsp_url": "rtsp://admin:password@192.168.1.50/stream1" }
```

### Opción 4 — Webcam local
```json
{ "name": "Webcam", "rtsp_url": "0" }
```

---

## Problemas comunes

| Síntoma | Causa | Solución |
|---|---|---|
| Stream congela | YOLO corre en cada frame | Ya corregido: IA cada 500ms |
| `CAP_DSHOW` lento en arranque | Normal en Windows | Espera 2-3s al inicio |
| Cámara WiFi no conecta | Misma red WiFi requerida | PC y móvil en el mismo router |
| RTSP se desconecta | WiFi inestable | Se reconecta automáticamente (hasta 10 intentos) |
