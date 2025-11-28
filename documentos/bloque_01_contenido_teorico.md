# Bloque 1 · ¿Qué es Retrieval-Augmented Generation (RAG)?

Este bloque introduce los conceptos esenciales de un flujo RAG y cómo cada componente contribuye a obtener respuestas mejor informadas a partir de fuentes propias.

## ¿Por qué RAG?

Los modelos de lenguaje grandes (LLM) poseen conocimiento general, pero no siempre están actualizados ni conocen los detalles internos de una organización. Retrieval-Augmented Generation (RAG) permite enriquecer las respuestas de un modelo con información específica proveniente de una base de conocimiento curada.

En otras palabras, RAG combina dos mundos:
- **Recuperación**: localizar fragmentos relevantes en documentos propios.
- **Generación**: redactar una respuesta usando tanto la pregunta como los fragmentos recuperados.

## Componentes de un sistema RAG

1. **Fuentes de conocimiento**: documentos, páginas web, manuales o bases de datos que contienen la información confiable.
2. **Ingesta y limpieza**: procesos que normalizan, eliminan ruido y preparan el texto.
3. **Chunking**: división en fragmentos manejables (chunks) que capturen ideas completas.
4. **Modelos de embeddings**: convierten cada fragmento en un vector numérico que preserva significado.
5. **Base vectorial**: almacena los vectores y permite realizar búsquedas por similitud.
6. **Recuperador**: dada una consulta, encuentra los vectores más cercanos.
7. **Generador**: redacta la respuesta final usando la consulta y los fragmentos recuperados.

## Flujo típico de extremo a extremo

1. Se seleccionan y preparan las fuentes confiables.
2. Se crean fragmentos y sus embeddings.
3. Se almacenan en una base vectorial.
4. Una pregunta del usuario se transforma en vector.
5. Se recuperan los fragmentos más similares.
6. Un modelo genera una respuesta apoyándose en esos fragmentos.

## Actividad práctica: simulación de vector search

Trabajaremos con un ejemplo muy simple usando vectores predefinidos que preservan relaciones semánticas. En sistemas reales, estos vectores se generan mediante modelos de transformers entrenados que capturan el significado de las palabras, pero aquí usaremos vectores ya creados para entender el concepto sin ejecutar ningún modelo.

### Paso 1. Definir una base de conocimiento simple

Trabajaremos con un corpus muy básico de solo 3 documentos cortos para entender el concepto.

### Paso 2. Fragmentar y tokenizar

Cada documento ya es una frase completa, así que simplemente lo dividiremos en palabras (tokens). La tokenización separa el texto en palabras individuales que serán procesadas por el modelo de embeddings.

### Paso 3. Embeddings predefinidos

En sistemas reales, los modelos de transformers (como BERT, GPT, etc.) generan vectores que capturan el significado de las palabras. Palabras con significados similares tienen vectores cercanos en el espacio.

Aquí usaremos vectores predefinidos que ya preservan estas relaciones semánticas. Por ejemplo:
- "gatos" y "perros" (ambas son mascotas) tendrán vectores similares
- "mascotas" y "animales" tendrán vectores cercanos
- "programación" tendrá un vector diferente (tema distinto)

Los embeddings predefinidos preservan relaciones semánticas. En la práctica, estos vectores serían generados por un modelo transformer entrenado. Los vectores de dimensión 5 permiten una mejor diferenciación:
- Dimensión 1: Animal general / Ser vivo
- Dimensión 2: Característica de mascota
- Dimensión 3: Característica específica de GATO
- Dimensión 4: Característica específica de PERRO
- Dimensión 5: Característica específica de Programación

Los vectores de 'gatos' y 'perros' tienen valores más distintivos en sus dimensiones específicas (Dim3 para gatos, Dim4 para perros) aunque mantienen similitud en las dimensiones de 'animal' y 'mascota'. 'programación' sigue siendo un tema diferente con alta carga en Dim5.

### Paso 4. Convertir chunks en vectores

Para representar un fragmento completo (que tiene múltiples palabras), calcularemos el promedio de los vectores de todas sus palabras y luego lo normalizamos. Esto nos da un único vector que representa el significado del fragmento completo.

Si una palabra no está en el diccionario de embeddings, se omite. El proceso consiste en:
1. Obtener el vector de cada palabra del fragmento desde el diccionario de embeddings
2. Calcular el promedio de todos los vectores de palabras
3. Normalizar el vector resultante para que tenga norma unitaria

### Paso 5. Recuperar fragmentos por similitud

Compararemos la representación vectorial de la pregunta con cada chunk usando similitud coseno. Esta métrica mide el ángulo entre dos vectores: valores cercanos a 1 indican alta similitud, mientras que valores cercanos a 0 indican baja similitud.

El proceso de recuperación (retrieval) sigue estos pasos:

**Paso 1: Procesar la consulta**
- Se tokeniza la consulta: se convierte el texto de la consulta en una lista de palabras (tokens)
- Se convierte la consulta en un vector (embedding): se promedian los vectores de las palabras conocidas en el diccionario de embeddings. Este vector representa el significado semántico de la consulta
- Si ninguna de las palabras de la consulta está en el diccionario de embeddings, el vector será de ceros y la similitud coseno siempre será 0, lo que afectará los resultados de la recuperación

**Paso 2: Calcular similitud coseno**
- Se calcula la similitud coseno entre el vector de la consulta y cada vector de fragmento del corpus
- Una similitud cercana a 1.0 indica alta relación semántica
- Se obtienen puntuaciones de similitud para todos los fragmentos

**Paso 3: Ordenar por similitud**
- Los fragmentos se clasifican de mayor a menor similitud con la consulta
- Se crea una lista ordenada con los índices de los chunks y sus puntuaciones

**Paso 4: Seleccionar los fragmentos más relevantes**
- Se eligen los 'top_k' fragmentos con las puntuaciones de similitud más altas
- Cada resultado incluye: posición (rank), similitud con la consulta, documento ID y fragmento recuperado

## Conceptos clave sobre embeddings y similitud

### Embeddings

Los embeddings convierten palabras y fragmentos en vectores numéricos que preservan relaciones semánticas. En sistemas reales, estos vectores son generados por modelos de transformers entrenados (como BERT, GPT, etc.) que aprenden estas relaciones de millones de textos. Palabras con significados similares tienen vectores cercanos en el espacio vectorial.

### Similitud coseno

La similitud coseno es una métrica que mide el ángulo entre dos vectores:
- Una similitud cercana a 1 indica que las palabras tienen un significado similar en el espacio vectorial
- Una similitud cercana a 0 (o negativa) indica que son muy diferentes o no relacionadas
- Si una palabra no está en el diccionario de embeddings, la función indicará una advertencia y devolverá 0.0 de similitud

### Análisis de resultados

Al observar las similitudes calculadas, podemos entender:
- Por qué algunas preguntas recuperan mejor ciertos documentos: depende de las palabras que comparten la pregunta y los fragmentos, y de cómo los embeddings capturan el significado semántico
- Qué pasa cuando usas palabras que no están en el corpus: si las palabras no están en el diccionario de embeddings, no contribuyen al vector de la consulta, lo que puede afectar la calidad de la recuperación
- Hay información semántica en los vectores: los embeddings capturan significado, no solo palabras exactas. Fragmentos con temas similares tienen vectores cercanos, permitiendo que la búsqueda por similitud encuentre contenido relevante aunque use palabras diferentes

## Puntos clave aprendidos

- **Chunking**: Dividimos documentos en fragmentos manejables que preservan el contexto
- **Tokenización**: Convertimos texto en palabras individuales (tokens) que pueden ser procesadas
- **Embeddings**: Convertimos palabras en vectores numéricos que preservan relaciones semánticas. Los modelos como Word2Vec, BERT o GPT capturan estas relaciones, permitiendo que fragmentos con palabras diferentes pero significados similares tengan vectores cercanos
- **Búsqueda por coseno**: La similitud coseno nos permite encontrar fragmentos relevantes comparando vectores. Una pregunta sobre "mascotas" recupera documentos sobre gatos y perros, mientras que una pregunta sobre "programación" recupera el documento relevante

Los embeddings capturan significado, no solo palabras exactas. Fragmentos con temas similares tienen vectores cercanos. La búsqueda por similitud encuentra contenido relevante aunque use palabras diferentes.

En sistemas reales usaríamos modelos de embeddings entrenados y bases vectoriales optimizadas. Una vez recuperados los fragmentos, el siguiente paso sería pasarlos a un modelo generativo para redactar una respuesta final.

