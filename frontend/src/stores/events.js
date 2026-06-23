let socket = null

export function connectWebSocket(onMessage) {

    // Evitar múltiples conexiones
    if (socket) {
        return
    }

    socket = new WebSocket(
        "ws://127.0.0.1:8000/ws/events"
    )

    socket.onopen = () => {

        console.log("WS CONNECTED")
    }

    socket.onmessage = (event) => {

        const data = JSON.parse(event.data)

        console.log("EVENT:", data)

        if (onMessage) {
            onMessage(data)
        }
    }

    socket.onerror = (error) => {

        console.error("WS ERROR:", error)
    }

    socket.onclose = () => {

        console.log("WS CLOSED")

        socket = null

        // Reconectar automáticamente
        setTimeout(() => {

            connectWebSocket(onMessage)

        }, 3000)
    }
}