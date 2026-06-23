<template>
  <div style="display:flex; height:100vh; background:#050505; color:white; font-family:sans-serif; overflow:hidden;">

    <!-- SIDEBAR -->
    <div style="width:56px; background:#0a0a0a; border-right:1px solid rgba(255,255,255,0.05); display:flex; flex-direction:column; align-items:center; padding:24px 0; flex-shrink:0;">
      <div style="width:36px; height:36px; background:#2563eb; border-radius:10px; display:flex; align-items:center; justify-content:center; font-weight:bold; font-size:11px; margin-bottom:32px;">AI</div>
      <i class="pi pi-video" style="color:#3b82f6; font-size:18px; margin-bottom:24px;"></i>
      <i class="pi pi-history" style="color:#4b5563; font-size:18px;"></i>
    </div>

    <!-- MAIN: 4 cámaras en grid 2x2 -->
    <div style="flex:1; min-width:0; padding:16px; display:flex; flex-direction:column; gap:12px; overflow:hidden;">

      <!-- Header -->
      <div style="display:flex; justify-content:space-between; align-items:center; flex-shrink:0;">
        <h1 style="margin:0; font-size:18px; font-weight:700;">Monitor de Seguridad</h1>
        <div style="display:flex; align-items:center; gap:8px; background:rgba(34,197,94,0.1); padding:4px 12px; border-radius:999px; border:1px solid rgba(34,197,94,0.2);">
          <div style="width:8px; height:8px; background:#22c55e; border-radius:50%;"></div>
          <span style="font-size:11px; color:#22c55e; font-weight:600; text-transform:uppercase;">Sistema Activo</span>
        </div>
      </div>

      <!-- GRID 2x2 — ocupa todo el espacio restante -->
      <div style="flex:1; min-height:0; display:grid; grid-template-columns:1fr 1fr; grid-template-rows:1fr 1fr; gap:10px;">

        <div v-for="n in 4" :key="n"
          style="position:relative; border-radius:16px; overflow:hidden; background:#111; border:1px solid rgba(255,255,255,0.06);">

          <img v-if="cameras[n-1]"
            :src="`${API_BASE}/cameras/${cameras[n-1].id}/stream`"
            style="width:100%; height:100%; object-fit:cover; display:block;"
            @error="onStreamError(cameras[n-1].id)"
          />

          <div v-if="cameras[n-1]"
            style="position:absolute; top:8px; left:8px; background:rgba(0,0,0,0.5); backdrop-filter:blur(4px); padding:2px 8px; border-radius:6px; font-size:10px; font-weight:600; text-transform:uppercase; letter-spacing:0.05em;">
            {{ cameras[n-1].name }}
          </div>
          <div v-if="cameras[n-1]"
            style="position:absolute; top:10px; right:10px; width:8px; height:8px; background:#4ade80; border-radius:50%; box-shadow:0 0 6px #4ade80;">
          </div>

          <!-- Slot vacío -->
          <div v-if="!cameras[n-1]"
            style="width:100%; height:100%; display:flex; flex-direction:column; align-items:center; justify-content:center; gap:8px; color:#374151;">
            <i class="pi pi-video" style="font-size:24px;"></i>
            <span style="font-size:11px;">CAM {{ n }}</span>
          </div>

        </div>

      </div>

    </div>

    <!-- PANEL DERECHO: snapshots miniatura — ancho fijo angosto -->
    <div style="width:220px; flex-shrink:0; background:#0a0a0a; border-left:1px solid rgba(255,255,255,0.05); display:flex; flex-direction:column; padding:12px;">

      <p style="margin:0 0 10px 0; font-size:10px; font-weight:700; color:#6b7280; text-transform:uppercase; letter-spacing:0.08em; flex-shrink:0;">
        ⚡ Actividad
      </p>

      <p v-if="events.length === 0" style="color:#374151; font-size:11px; text-align:center; margin-top:32px;">
        Sin eventos
      </p>

      <div style="flex:1; min-height:0; overflow-y:auto; display:flex; flex-direction:column; gap:6px;">

        <div v-for="(event, index) in events" :key="index"
          style="display:flex; align-items:center; gap:8px; padding:6px; border-radius:10px; background:#111; border:1px solid rgba(255,255,255,0.05);">

          <!-- Miniatura 52x37px -->
          <div style="width:52px; height:37px; border-radius:6px; overflow:hidden; background:#000; flex-shrink:0;">
            <img
              :src="snapshotUrl(event.image_path)"
              style="width:100%; height:100%; object-fit:cover; display:block;"
              @error="(e) => e.target.style.display='none'"
            />
          </div>

          <!-- Texto -->
          <div style="flex:1; min-width:0;">
            <p style="margin:0; font-size:8px; font-weight:700; color:#60a5fa; text-transform:uppercase; letter-spacing:0.05em;">{{ event.event_type }}</p>
            <p style="margin:2px 0 0; font-size:10px; font-weight:600; white-space:nowrap; overflow:hidden; text-overflow:ellipsis;">{{ event.camera_name }}</p>
            <p style="margin:1px 0 0; font-size:8px; color:#4b5563;">{{ event.created_at?.slice(11,19) }}</p>
          </div>

        </div>

      </div>

    </div>

  </div>
</template>

<script setup>
import { ref, onMounted } from "vue"
import { connectWebSocket } from "../stores/events"

const API_BASE = "http://127.0.0.1:8000"
const events   = ref([])
const cameras  = ref([])

function snapshotUrl(imagePath) {
  if (!imagePath) return ""
  const normalized = imagePath.replace(/\\/g, "/")
  const idx = normalized.indexOf("storage/")
  return idx !== -1 ? `${API_BASE}/${normalized.slice(idx)}` : `${API_BASE}/${normalized}`
}

function onStreamError(cameraId) {
  console.warn(`Stream cámara ${cameraId} no disponible`)
}

async function loadCameras() {
  try {
    const res = await fetch(`${API_BASE}/cameras`)
    cameras.value = await res.json()
    console.log("Cámaras:", cameras.value)
  } catch (e) {
    console.error("Error cargando cámaras:", e)
  }
}

async function loadEvents() {
  try {
    const res = await fetch(`${API_BASE}/events?limit=100`)
    events.value = await res.json()
  } catch (e) {
    console.error("Error cargando eventos:", e)
  }
}

onMounted(async () => {
  await loadCameras()
  await loadEvents()
  connectWebSocket((event) => {
    events.value.unshift(event)
    if (events.value.length > 100) events.value.pop()
  })
})
</script>