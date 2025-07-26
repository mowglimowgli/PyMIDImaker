# PyMIDImaker

PyMIDImaker es una pequeña aplicación web escrita en Python que permite:

* Separar archivos MP3 o WAV en "stems" utilizando [Spleeter](https://github.com/deezer/spleeter).
* Convertir cada stem en un archivo MIDI utilizando `librosa` y `pretty_midi`.

El usuario sube un archivo de audio desde la página principal y al terminar el proceso descarga un ZIP con los stems en formato WAV y sus correspondientes archivos MIDI.

## Instalación

1. Crear y activar un entorno virtual de Python.
2. Instalar las dependencias:

```bash
pip install -r requirements.txt
```

**Nota**: `spleeter` y `librosa` son librerías pesadas y pueden requerir bibliotecas de audio adicionales.

## Uso

```bash
python app.py
```

Abrir `http://localhost:5000` en el navegador, seleccionar el archivo MP3/WAV y esperar a que aparezca el enlace de descarga.

Los resultados se guardan en la carpeta `results/`.

## Crear un ejecutable (Windows)

Para generar un `.exe` se puede utilizar [PyInstaller](https://pyinstaller.org/):

```bash
pip install pyinstaller
pyinstaller --onefile app.py
```

El ejecutable se ubicará en la carpeta `dist/`.

## Generar un APK

Para compilar la aplicación para Android se recomienda usar
[Buildozer](https://github.com/kivy/buildozer). Se debe instalar en un entorno
Linux y ejecutar:

```bash
pip install buildozer
buildozer init  # crea buildozer.spec
# editar buildozer.spec según sea necesario
buildozer -v android debug
```

El archivo APK quedará en la carpeta `bin/`.
