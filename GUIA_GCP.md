# Guía: SoftMarket en Google Cloud (paso a paso)

Todo se hace en **Cloud Shell**. Copia **un bloque a la vez** y espera a que termine.
Las líneas que empiezan con `#` son comentarios: explican, no se ejecutan.

| Servicio | Para qué lo usa SoftMarket |
|---|---|
| Cloud Run | Ejecuta la aplicación web y le da una URL pública |
| Cloud Build | Construye la imagen del contenedor a partir del código |
| Artifact Registry | Guarda cada versión de la imagen |
| Firestore | Base de datos donde quedan guardadas las facturas |
| Pub/Sub | Recibe un mensaje cada vez que se emite una factura |
| Secret Manager | Guarda la clave de acceso, fuera del código |
| IAM | Cuenta de servicio con solo los permisos necesarios |
| Facturación | Presupuesto con alertas y limpieza al final |

---

## 0. Antes de empezar (en la consola, no en la terminal)

1. Activa la prueba gratuita y crea o elige un proyecto.
2. **Crea una alerta de presupuesto:** Menú → Facturación → Presupuestos y alertas →
   Crear presupuesto. Monto: 5 USD. Alertas: 50 %, 90 % y 100 %.
   Recuerda: el presupuesto **avisa**, no apaga nada.
3. Abre Cloud Shell (ícono `>_` arriba a la derecha).

## 1. Traer el proyecto y los cambios

```bash
cd ~
git clone https://github.com/Sofi-777-learning/softmarket-facturacion
cd softmarket-facturacion
git checkout develop
git checkout -b feature/SM-42-softmarket-en-google-cloud
```

Sube `cambios_gcp.zip` a Cloud Shell (menú ⋮ de la terminal → Subir) y luego:

```bash
unzip -o ~/cambios_gcp.zip -d ~/softmarket-facturacion
ls app
```

## 2. Probar primero sin la nube (modo memoria)

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt pytest pytest-cov
python3 -m pytest -v
```

Deben pasar **16 pruebas**. Luego levanta la web:

```bash
MODO=memoria CLAVE_ADMIN=prueba PYTHONPATH=src:app python3 app/main.py
```

Vista previa web (ícono del ojo/pantalla) → **Vista previa en el puerto 8080**.
Emite una factura con la clave `prueba`. Para detener: `Ctrl + C`.

## 3. Variables que usaremos

```bash
PROYECTO=$(gcloud config get-value project)
REGION=us-central1
CUENTA=softmarket-run@$PROYECTO.iam.gserviceaccount.com
echo $PROYECTO
```

> Si abres otra pestaña o se reinicia Cloud Shell, vuelve a ejecutar este bloque.

## 4. Activar los servicios

```bash
gcloud services enable run.googleapis.com cloudbuild.googleapis.com \
  artifactregistry.googleapis.com firestore.googleapis.com \
  pubsub.googleapis.com secretmanager.googleapis.com
```

## 5. Firestore (base de datos)

```bash
gcloud firestore databases create --location=$REGION
```

## 6. Pub/Sub (tema y suscripción)

```bash
gcloud pubsub topics create facturas-emitidas
gcloud pubsub subscriptions create facturas-sub --topic=facturas-emitidas
```

## 7. Secret Manager (la clave de acceso)

`read -s` pide la clave **sin mostrarla** y sin dejarla en el historial.

```bash
read -s -p "Escribe la clave de acceso: " CLAVE; echo
printf "%s" "$CLAVE" | gcloud secrets create clave-admin --data-file=-
unset CLAVE
```

## 8. IAM: cuenta de servicio con mínimo privilegio

```bash
gcloud iam service-accounts create softmarket-run \
  --display-name="SoftMarket en Cloud Run"

# Leer y escribir en Firestore
gcloud projects add-iam-policy-binding $PROYECTO \
  --member=serviceAccount:$CUENTA --role=roles/datastore.user

# Publicar solo en el tema de facturas
gcloud pubsub topics add-iam-policy-binding facturas-emitidas \
  --member=serviceAccount:$CUENTA --role=roles/pubsub.publisher

# Leer solo el secreto clave-admin
gcloud secrets add-iam-policy-binding clave-admin \
  --member=serviceAccount:$CUENTA --role=roles/secretmanager.secretAccessor
```

## 9. Probar contra la nube desde Cloud Shell (opcional)

```bash
MODO=nube PROYECTO=$PROYECTO CLAVE_ADMIN=prueba PYTHONPATH=src:app python3 app/main.py
```

Emite una factura en la vista previa y revísala en Menú → Firestore. `Ctrl + C` para salir.

## 10. Desplegar en Cloud Run

Este único comando usa **Cloud Build** (construye con el `Dockerfile`),
**Artifact Registry** (guarda la imagen) y **Cloud Run** (la ejecuta).

```bash
gcloud run deploy softmarket --source . --region=$REGION \
  --service-account=$CUENTA \
  --set-env-vars=MODO=nube,PROYECTO=$PROYECTO \
  --set-secrets=CLAVE_ADMIN=clave-admin:latest \
  --allow-unauthenticated
```

Si pregunta si crea el repositorio de Artifact Registry, responde `Y`.
Al final muestra una **Service URL**: ábrela y emite una factura con tu clave.

## 11. Comprobar cada servicio (para el video)

```bash
# Mensajes que llegaron a Pub/Sub
gcloud pubsub subscriptions pull facturas-sub --auto-ack --limit=5

# Versiones (revisiones) de Cloud Run
gcloud run revisions list --service=softmarket --region=$REGION

# Construcciones de Cloud Build
gcloud builds list --limit=3
```

En la consola: **Firestore** → colección `facturas` · **Artifact Registry** →
`cloud-run-source-deploy` · **Secret Manager** → `clave-admin` (no muestra el valor) ·
**IAM** → `softmarket-run` con sus roles.

## 12. Guardar en Git

```bash
git add .
git status
git commit -m "feat(gcp): desplegar SoftMarket en Cloud Run con Firestore, Pub/Sub y Secret Manager"
git push -u origin feature/SM-42-softmarket-en-google-cloud
```

Revisa con `git status` que **no** se suba `.venv`. Luego PR hacia `develop`.

## 13. Limpiar al terminar (para que no cobre)

```bash
gcloud run services delete softmarket --region=$REGION
gcloud artifacts repositories delete cloud-run-source-deploy --location=$REGION
gcloud pubsub subscriptions delete facturas-sub
gcloud pubsub topics delete facturas-emitidas
gcloud secrets delete clave-admin
gcloud firestore databases delete --database="(default)"
```

O, lo más seguro: Menú → IAM y administración → Configuración → **Cerrar proyecto**.

---

## Si algo falla

| Mensaje | Qué hacer |
|---|---|
| `PERMISSION_DENIED` durante el build de `gcloud run deploy` | Dar el rol de constructor a la cuenta de Compute: `gcloud projects add-iam-policy-binding $PROYECTO --member=serviceAccount:$(gcloud projects describe $PROYECTO --format='value(projectNumber)')-compute@developer.gserviceaccount.com --role=roles/run.builder` y repetir el deploy |
| `externally-managed-environment` en pip | Activa el entorno: `source .venv/bin/activate` |
| `No module named facturacion` | Falta `PYTHONPATH=src:app` antes del comando |
| La web dice "Clave incorrecta" | Usa la clave que guardaste en el paso 7 |
| `$PROYECTO` sale vacío | Repite el paso 3 |
| Página 500 en Cloud Run | Menú → Cloud Run → softmarket → **Registros** y busca el error |
