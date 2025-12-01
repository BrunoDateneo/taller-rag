# Infraestructura como Código (IaC) - Configuración de AWS Bedrock

Esta carpeta contiene los scripts necesarios para configurar la infraestructura de AWS Bedrock que se utiliza en el taller de RAG. Estos scripts automatizan la creación de los recursos necesarios en AWS.

## Requisitos previos

### 1. Crear cuenta de AWS

Antes de ejecutar estos scripts, necesitás:

1. **Crear una cuenta de AWS**: Andá a [aws.amazon.com](https://aws.amazon.com) y creá una cuenta nueva
2. **Agregar método de pago**: AWS requiere una tarjeta de crédito para crear la cuenta
   - **Importante**: No te preocupes por los costos. El uso de todos los servicios del taller completo cuesta menos de un dólar USD
   - AWS tiene un nivel gratuito generoso y los servicios que usamos tienen costos muy bajos
   - Podés eliminar todos los recursos al finalizar el taller para evitar costos adicionales

### 2. Instalar AWS CLI

AWS CLI (Command Line Interface) es una herramienta que te permite interactuar con AWS desde la terminal. Los scripts la necesitan para configurar tus credenciales.

**Instalación:**

- **Windows**: Descargá el instalador desde [aws.amazon.com/cli](https://aws.amazon.com/cli/) o usá `winget install Amazon.AWSCLI`
- **Mac**: Usá Homebrew: `brew install awscli`
- **Linux**: Seguí las instrucciones en la [documentación oficial](https://docs.aws.amazon.com/cli/latest/userguide/getting-started-install.html)

Verificá que esté instalado ejecutando:
```bash
aws --version
```

### 3. Generar credenciales de acceso

Una vez que tengas tu cuenta de AWS, necesitás crear credenciales de acceso. Para simplificar, vamos a crear un usuario con permisos de administrador:

1. Andá a la consola de AWS y buscá "IAM" (Identity and Access Management)
2. En el menú lateral, seleccioná "Usuarios" (Users)
3. Hacé clic en "Agregar usuarios" (Add users)
4. Ingresá un nombre de usuario (por ejemplo: `taller-rag-user`)
5. Seleccioná "Proporcionar acceso a la consola de administración de AWS" (Provide access to the AWS Management Console) y marcá "Contraseña de AWS IAM" (AWS IAM password)
6. En "Permisos", seleccioná "Adjuntar políticas directamente" (Attach policies directly)
7. Buscá y seleccioná la política **"AdministratorAccess"** (esto le da permisos completos)
8. Hacé clic en "Siguiente" y luego en "Crear usuario"
9. Una vez creado el usuario, volvé a la lista de usuarios y hacé clic en el usuario que creaste
10. Andá a la pestaña "Credenciales de seguridad" (Security credentials)
11. Desplazate hasta "Claves de acceso" (Access keys) y hacé clic en "Crear clave de acceso" (Create access key)
12. Seleccioná "Aplicación que se ejecuta fuera de AWS" (Application running outside AWS)
13. Hacé clic en "Siguiente" y luego en "Crear clave de acceso"
14. **IMPORTANTE**: Guardá el **Access Key ID** y el **Secret Access Key** de forma segura. No vas a poder ver el Secret Access Key de nuevo después de cerrar esta ventana.

### 4. Configurar el perfil de AWS (profile_name)

Los scripts utilizan un perfil de AWS llamado `taller-rag`. Esto es como un "alias" que guarda tus credenciales de forma segura en tu computadora.

Para configurarlo, ejecutá en tu terminal:

```bash
aws configure --profile taller-rag
```

Te va a pedir:
- **AWS Access Key ID**: La clave de acceso que generaste
- **AWS Secret Access Key**: La clave secreta que generaste
- **Default region name**: `us-west-2` (o la región que prefieras)
- **Default output format**: `json` (podés presionar Enter para usar el predeterminado)

Esto va a guardar tus credenciales en un archivo `~/.aws/credentials` (en Linux/Mac) o `C:\Users\TuUsuario\.aws\credentials` (en Windows).

**¿Por qué usar un perfil?**
- Permite tener múltiples cuentas de AWS configuradas
- Mantiene tus credenciales organizadas
- Es más seguro que hardcodear credenciales en los scripts
- Los scripts pueden cambiar fácilmente entre diferentes cuentas

## Configuración inicial

Antes de ejecutar los scripts, tenés que editar algunos valores:

### 1. Account ID

En todos los scripts, buscá la línea que dice:
```python
account_id = "111111111111" # TODO: Cambiar por el account_id de tu cuenta de AWS
```

Reemplazá `111111111111` con tu Account ID de AWS. Lo podés encontrar en la esquina superior derecha de la consola de AWS.

### 2. Bucket name (solo en 03_create_data_source.py)

En el archivo `03_create_data_source.py`, verificá que el nombre del bucket S3 sea correcto. Tiene que seguir el formato:
```
taller-rag-knowledge-base-us-west-2-{tu-account-id}
```

## Scripts disponibles

Los scripts deben ejecutarse en orden, ya que cada uno depende del anterior.

### 00_create_role.py

**¿Qué hace?**
Crea el rol IAM necesario para que la Knowledge Base de Bedrock pueda acceder a S3 y S3 Vectors. Este rol es requerido por Bedrock para leer documentos de S3 y escribir vectores en S3 Vectors.

**Conceptos clave:**
- **Rol IAM**: Un conjunto de permisos que puede ser asumido por servicios de AWS
- **Trust Policy**: Define qué servicios pueden "asumir" (usar) el rol
- **Policy**: Define qué acciones puede realizar el rol (leer S3, escribir en S3 Vectors)

**Qué crea:**
- Un rol IAM llamado `taller-rag-knowledge-base-role`
- Una política que permite leer de S3 y escribir en S3 Vectors
- El ARN del rol que se usa en el script `02_create_kb.py`

**Requisitos previos:**
- Tenés que tener configurado el perfil de AWS (`aws configure --profile taller-rag`)
- Tenés que haber editado el `account_id` en el script

**Cómo ejecutarlo:**
```bash
cd iac
python 00_create_role.py
```

**Nota**: Este script debe ejecutarse antes de `02_create_kb.py` porque la Knowledge Base necesita el rol para funcionar.

### 01_create_vector_bucket.py

**¿Qué hace?**
Crea un "Vector Bucket" en S3 Vectors. Esto es como un contenedor especializado para almacenar vectores (representaciones numéricas de texto).

**Conceptos clave:**
- **Vector Bucket**: Un almacenamiento especializado para vectores en AWS
- **Índice vectorial**: Una estructura que permite buscar vectores similares rápidamente
- **Dimensión**: El tamaño de cada vector (1024 números en nuestro caso)
- **Métrica de distancia**: Cómo medimos qué tan similares son dos vectores (usamos "euclidean")

**Qué crea:**
- Un Vector Bucket llamado `taller-rag-vector-bucket`
- Un índice vectorial llamado `taller-rag-vector-index`
- Guarda la información en `vector_bucket_info.json`

**Cómo ejecutarlo:**
```bash
cd iac
python 01_create_vector_bucket.py
```

### 02_create_kb.py

**¿Qué hace?**
Crea una Knowledge Base en Amazon Bedrock. La Knowledge Base es el componente principal que conecta tus documentos con el modelo de lenguaje.

**Conceptos clave:**
- **Knowledge Base**: Una base de conocimiento que almacena y busca información de tus documentos
- **Embedding Model**: El modelo que convierte texto en vectores (usamos Amazon Titan)
- **Rol IAM**: Permisos que permiten a Bedrock acceder a otros servicios de AWS

**Qué crea:**
- Una Knowledge Base llamada `taller-rag-kb`
- La conecta con el Vector Bucket creado anteriormente
- Guarda la información en `kb_info.json`

**Requisitos previos:**
- Tenés que haber ejecutado `00_create_role.py` primero (para crear el rol IAM)
- Tenés que haber ejecutado `01_create_vector_bucket.py` primero

**Cómo ejecutarlo:**
```bash
python 02_create_kb.py
```

### 03_create_data_source.py

**¿Qué hace?**
Crea un Data Source que le dice a la Knowledge Base dónde encontrar tus documentos. Es como decirle "busca los documentos en este bucket de S3".

**Conceptos clave:**
- **Data Source**: La fuente de datos que la Knowledge Base va a procesar
- **Bucket S3**: Un contenedor en AWS donde guardas archivos
- **Chunking**: Dividir documentos grandes en pedazos más pequeños para procesarlos
- **Overlap**: Superponer un poco los chunks para mantener el contexto

**Qué crea:**
- Un Data Source llamado `transcripciones-taller-rag`
- Configura cómo se dividen los documentos (2200 tokens por chunk, 12% de overlap)
- Actualiza `kb_info.json` con la información del Data Source

**Requisitos previos:**
- Tenés que haber ejecutado `02_create_kb.py` primero
- Tenés que tener un bucket S3 con tus documentos en la carpeta `transcripciones/`

**Cómo ejecutarlo:**
```bash
python 03_create_data_source.py
```

### 04_sync_data_source.py

**¿Qué hace?**
Inicia el proceso de sincronización. Esto toma los documentos de tu bucket S3, los convierte en vectores usando el modelo de embedding, y los guarda en el Vector Bucket.

**Conceptos clave:**
- **Sincronización**: El proceso de procesar documentos y convertirlos en vectores
- **Ingestion Job**: Un trabajo que procesa los documentos en segundo plano
- **Monitoreo**: Seguimiento del progreso del trabajo

**Qué hace:**
- Inicia un trabajo de sincronización
- Opcionalmente monitorea el progreso hasta que termine
- Actualiza `kb_info.json` con el estado del trabajo

**Requisitos previos:**
- Tenés que haber ejecutado `03_create_data_source.py` primero
- Tenés que tener documentos en tu bucket S3

**Cómo ejecutarlo:**
```bash
python 04_sync_data_source.py
```

El script te va a preguntar si querés monitorear el progreso. Esto puede tomar varios minutos dependiendo de la cantidad de documentos.

## Orden de ejecución

Ejecutá los scripts en este orden:

1. `00_create_role.py` - Creá el rol IAM necesario para la Knowledge Base
2. `01_create_vector_bucket.py` - Creá el almacenamiento de vectores
3. `02_create_kb.py` - Creá la Knowledge Base
4. `03_create_data_source.py` - Configurá la fuente de datos
5. `04_sync_data_source.py` - Procesá los documentos

## Archivos generados

Los scripts generan archivos JSON con información importante:

- `vector_bucket_info.json`: Información del Vector Bucket y su índice
- `kb_info.json`: Información de la Knowledge Base y Data Source

No eliminés estos archivos, ya que los scripts posteriores los necesitan.

## Solución de problemas

### Error: "No se encontró vector_bucket_info.json"
- Ejecutá primero `01_create_vector_bucket.py`

### Error: "No se encontró kb_info.json"
- Ejecutá primero `02_create_kb.py`

### Error: "ProfileNotFound"
- Verificá que hayas ejecutado `aws configure --profile taller-rag`
- Verificá que el nombre del perfil en los scripts sea `'taller-rag'`

### Error: "AccessDenied" o permisos
- Verificá que tu usuario de AWS tenga los permisos necesarios (debe tener AdministratorAccess)
- Asegurate de haber ejecutado `00_create_role.py` para crear el rol IAM necesario para la Knowledge Base
- Si el error ocurre al crear la Knowledge Base, verificá que el rol `taller-rag-knowledge-base-role` exista

### El recurso ya existe
- Los scripts están diseñados para ser idempotentes (podés ejecutarlos múltiples veces)
- Si un recurso ya existe, el script lo va a detectar y continuar

## Limpieza de recursos

Para evitar costos después del taller, podés eliminar los recursos creados:

1. Eliminá la Knowledge Base desde la consola de AWS Bedrock
2. Eliminá el Vector Bucket desde la consola de S3 Vectors
3. Eliminá el bucket S3 si lo creaste para el taller
4. Eliminá los archivos JSON generados si querés

## Costos

Como se mencionó al principio, el costo total del taller es menos de un dólar USD. Los principales costos son:

- **S3 Vectors**: Almacenamiento de vectores (muy económico)
- **Bedrock**: Procesamiento de embeddings y consultas (tiene nivel gratuito)
- **S3**: Almacenamiento de documentos (muy económico)

Recordá eliminar los recursos al finalizar para evitar costos continuos.

