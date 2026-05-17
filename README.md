# AI Voice Assistant

Asistente de voz universal para Linux. Se activa con un atajo de teclado, graba el microfono, transcribe con Whisper, consulta a opencode y reproduce la respuesta por voz.

## Compatibilidad

Funciona en **cualquier distro** y **cualquier entorno de escritorio**:

| Distro | Entorno | Funciona |
|---|---|---|
| Arch Linux | KDE Plasma, GNOME, bspwm, Sway, Hyprland, XFCE, i3 | Si |
| Debian/Ubuntu | KDE Plasma, GNOME, XFCE, MATE, Cinnamon | Si |
| Fedora | KDE Plasma, GNOME, Sway | Si |
| Cualquier otra | Cualquiera con X11 o Wayland | Si |

## Requisitos

- **Python 3.10+**
- **`opencode`** instalado y en el PATH
- **Micrófono** funcionando
- **Internet** (para edge-tts)
- **PulseAudio o PipeWire** (presente en cualquier distro moderna)
- **Una herramienta de captura** (instala al menos una):

| Herramienta | Entorno | Debian | Arch |
|---|---|---|---|
| `spectacle` | KDE | `sudo apt install spectacle` | `sudo pacman -S spectacle` |
| `gnome-screenshot` | GNOME | `sudo apt install gnome-screenshot` | `sudo pacman -S gnome-screenshot` |
| `scrot` | X11 (universal) | `sudo apt install scrot` | `sudo pacman -S scrot` |
| `grim` | Wayland (Sway/Hyprland) | `sudo apt install grim` | `sudo pacman -S grim` |
| `import` (ImageMagick) | X11 | `sudo apt install imagemagick` | `sudo pacman -S imagemagick` |

El asistente detecta automaticamente cual esta instalada y es compatible con tu entorno.

## Instalacion

### Instalacion automatica (recomendada)

```bash
git clone https://github.com/TU_USUARIO/ai-voice-assistant.git
cd ai-voice-assistant
chmod +x install.sh
sudo ./install.sh
```

Esto:
1. Copia el proyecto a `~/.local/share/ai-voice-assistant`
2. Crea el entorno virtual e instala dependencias
3. Instala un servicio systemd de sistema (arranca con el SO)
4. Habilita el servicio para inicio automatico

### Instalacion manual

```bash
git clone https://github.com/TU_USUARIO/ai-voice-assistant.git
cd ai-voice-assistant
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python main.py
```

## Uso

### Servicio systemd

```bash
# Iniciar
sudo systemctl start ai-voice-assistant

# Parar
sudo systemctl stop ai-voice-assistant

# Reiniciar (util si se queda bloqueado)
sudo systemctl restart ai-voice-assistant

# Ver estado
sudo systemctl status ai-voice-assistant

# Ver logs en vivo
sudo journalctl -u ai-voice-assistant -f

# Iniciar automatico al encender
sudo systemctl enable ai-voice-assistant

# Desactivar inicio automatico
sudo systemctl disable ai-voice-assistant
```

### Manual (sin servicio)

```bash
python main.py
```

### Configurar atajo de teclado

El asistente usa un archivo trigger (`/tmp/ai_voice_trigger`) que funciona en **cualquier entorno** (X11 y Wayland). Configura un atajo de teclado en tu DE/WM apuntando a `trigger.sh`:

**KDE Plasma:**
1. `Configuracion del sistema` → `Atajos` → `Atajos personalizados`
2. `Editar` → `Nuevo` → `Nuevo grupo` ("AI Voice Assistant")
3. Click derecho → `Nuevo` → `Accion global` → `Comando/URL`
4. Trigger: tu atajo preferido (ej: `ALT+Z`)
5. Comando: `~/.local/share/ai-voice-assistant/trigger.sh`
6. Aplicar

**GNOME:**
1. `Settings` → `Keyboard` → `View and Customize Shortcuts` → `Custom Shortcuts`
2. Add: Name="AI Voice Assistant", Command=`~/.local/share/ai-voice-assistant/trigger.sh`, Shortcut=`ALT+Z`

**bspwm** (con sxhkd):
```bash
# En ~/.config/sxhkd/sxhkdrc
alt + z
    ~/.local/share/ai-voice-assistant/trigger.sh
```

**Sway:**
```
# En ~/.config/sway/config
bindsym Mod4+z exec ~/.local/share/ai-voice-assistant/trigger.sh
```

**Hyprland:**
```
# En ~/.config/hypr/hyprland.conf
bind = ALT, Z, exec, ~/.local/share/ai-voice-assistant/trigger.sh
```

**XFCE:**
`Settings` → `Keyboard` → `Application Shortcuts` → Add → Command: `~/.local/share/ai-voice-assistant/trigger.sh`, Shortcut: `ALT+Z`

**i3:**
```
# En ~/.config/i3/config
bindsym Mod4+z exec ~/.local/share/ai-voice-assistant/trigger.sh
```

## Flujo del programa

```
Atajo (1ª vez)
    |
    +-- Aparece ventana terminal (oculta hasta ahora)
    +-- Carga historial de conversaciones anteriores
    +-- Empieza a grabar audio del microfono
         |
         | (hablas)
         |
         v
Atajo (2ª vez)
    |
    +-- Para la grabacion
    +-- Transcribe audio → texto (Whisper local)
    +-- Analiza si la pregunta es visual
    |   +-- Si → captura pantalla y adjunta imagen
    |   +-- No → consulta sin imagen (ahorra tokens)
    +-- Envia pregunta a opencode
    +-- Muestra respuesta en la terminal
    +-- Lee la respuesta en voz alta (edge-tts)
    +-- Al terminar de hablar → ventana se oculta
         |
         v
Atajo (mientras habla)
    |
    +-- Corta la respuesta inmediatamente y oculta la ventana
         |
         v
Atajo (siguiente vez)
    |
    +-- Mismo flujo, pero la ventana muestra
       todo el historial acumulado
```

### Captura de pantalla inteligente

Solo se envia captura cuando la pregunta implica algo visual:
- "que ves", "describe la pantalla", "que tengo abierto"
- "que color es", "que aplicacion es esa"
- "mira esto", "observa"

Las preguntas normales ("que hora es", "explica Python") **no** envian captura, ahorrando tokens.

### Captura por monitor

En sistemas con multiples monitores, captura solo el monitor donde esta el cursor del raton.

## Configuracion

### Modelo Whisper (`src/transcriber.py`)

```python
self.transcriber = Transcriber(model_size="base")
```

| Modelo | Tamaño | Velocidad | Precision |
|---|---|---|---|
| `tiny` | ~75MB | Muy rapido | Baja |
| `base` | ~140MB | Rapido | Media (default) |
| `small` | ~460MB | Medio | Alta |
| `medium` | ~1.5GB | Lento | Muy alta |
| `large` | ~3GB | Muy lento | Maxima |

### Voz TTS (`src/tts.py`)

```python
self.tts = TextToSpeech()  # default: es-ES-AlvaroNeural
```

Voces disponibles:
- `es-ES-AlvaroNeural` - Masculina Espana
- `es-ES-ElviraNeural` - Femenina Espana
- `es-MX-JorgeNeural` - Masculina Mexico
- `es-MX-DaliaNeural` - Femenina Mexico
- `es-AR-TomasNeural` - Masculina Argentina
- `es-CO-SalomeNeural` - Femenina Colombia

### Modelo opencode

Por defecto usa el modelo configurado en opencode. Para cambiarlo, edita `~/.config/opencode/opencode.jsonc`:

```jsonc
{
  "$schema": "https://opencode.ai/config.json",
  "model": "opencode-go/qwen3.6-plus-free"
}
```

## Estructura

```
ai-voice-assistant/
├── main.py                     # Punto de entrada
├── requirements.txt            # Dependencias Python
├── trigger.sh                  # Script para atajo de teclado
├── install.sh                  # Script de instalacion
├── uninstall.sh                # Script de desinstalacion
├── ai-voice-assistant.service  # Plantilla servicio systemd
├── .gitignore
├── README.md
├── src/
│   ├── __init__.py
│   ├── audio_recorder.py       # Grabacion con parecord (PulseAudio/PipeWire)
│   ├── transcriber.py          # Transcripcion con Whisper
│   ├── tts.py                  # Texto a voz con edge-tts + ffplay
│   ├── opencode_client.py      # Cliente de opencode con captura inteligente
│   ├── screen_capture.py       # Captura universal (detecta herramienta disponible)
│   ├── terminal_window.py      # Ventana tipo terminal PyQt6
│   └── hotkey_manager.py       # Hotkey via archivo trigger (X11/Wayland)
└── temp_audio/                 # Archivos temporales (audio, capturas)
```

## Solucion de problemas

**La ventana no aparece al pulsar el atajo:**
- Verifica que el atajo este bien configurado en tu DE
- Comprueba que `trigger.sh` sea ejecutable: `chmod +x trigger.sh`
- Ejecuta manualmente: `touch /tmp/ai_voice_trigger`
- Reinicia el servicio: `sudo systemctl restart ai-voice-assistant`

**El servicio se queda bloqueado:**
- Reinicialo: `sudo systemctl restart ai-voice-assistant`
- Revisa los logs: `sudo journalctl -u ai-voice-assistant --no-pager -n 50`

**No graba audio:**
- Verifica que PulseAudio o PipeWire esten corriendo: `pulseaudio --check` o `systemctl --user status pipewire`
- Prueba: `parecord test.wav` (habla, Ctrl+C, reproduce con `ffplay test.wav`)

**La captura sale negra:**
- En Wayland, `scrot` no funciona. El asistente detecta Wayland y usa `spectacle` o `gnome-screenshot` automaticamente
- En KDE Wayland, `spectacle` funciona correctamente
- En GNOME Wayland, instala `gnome-screenshot`

**opencode no responde:**
- Verifica: `opencode run "di hola"`
- El timeout es de 5 minutos por consulta
- Asegurate de que opencode esta en el PATH del usuario

## Desinstalacion

```bash
cd ai-voice-assistant
chmod +x uninstall.sh
sudo ./uninstall.sh
```
