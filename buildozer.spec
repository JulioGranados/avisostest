[app]
title = Avisos Ecológicos
package.name = avisos_ecologicos
package.domain = org.example
source.dir = .
source.include_exts = py,kv,json
version = 0.1
orientation = portrait
requirements = python3,kivy
android.permissions = WRITE_EXTERNAL_STORAGE,READ_EXTERNAL_STORAGE

[buildozer]
log_level = 2
warn_on_root = 1

# Usa API 33 (coincide con SDK instalado en workflow)
android.api = 33

# Fuerza build-tools 33.0.2 para evitar conflictos con 36
android.build_tools = 33.0.2

# NDK 23b compatible con SDK 33 y build-tools 33.0.2
android.ndk = 23b

# Acepta licencias automáticamente
android.accept_sdk_license = True

# No declares android.sdk para evitar confusión
# android.sdk = 33

# Rutas SDK y NDK externas para evitar SDK interno
android.sdk_path = /home/runner/Android
android.ndk_path = /home/runner/Android/ndk/23.1.7779620
