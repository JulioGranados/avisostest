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

# Usa build-tools versión 33.0.2 (coincide con workflow)
android.build_tools = 33.0.2

# Usa NDK 23b, que es compatible con las versiones anteriores
android.ndk = 23b

# Esto hace que Buildozer acepte las licencias automáticamente
android.accept_sdk_license = True

# No pongas android.sdk, para evitar confusión con android.api
# android.sdk = 33
