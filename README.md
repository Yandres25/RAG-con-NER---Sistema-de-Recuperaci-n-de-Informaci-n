# RAG con NER - Sistema de Recuperación de Información

Sistema de Retrieval Augmented Generation (RAG) con reconocimiento de entidades nombradas (NER) para análisis de documentos en español.

## Descripción

Este proyecto implementa un sistema RAG local que:
1. Genera documentos PDF de prueba con contenido diverso
2. Extrae texto de los PDFs
3. Identifica entidades nombradas (personas, organizaciones, lugares, etc.) usando spaCy
4. Almacena la información en una base de datos SQLite
5. Recupera contexto relevante según entidades buscadas
6. Genera respuestas usando un modelo de lenguaje local (Llama.cpp)

## Requisitos

```bash
pip install llama-cpp-python pandas spacy fpdf PyPDF2

# Descargar modelo spaCy en español
python -m spacy download es_core_news_lg
```

## Estructura del Proyecto

- **RAG con NER4.py** - Script principal del sistema
- **rag_fraude.db** - Base de datos SQLite (generada automáticamente)
- **doc_01-10_*.pdf** - Documentos PDF de prueba

## Configuración

En el archivo `RAG_con_NER.py`, configurar las rutas:

```python
RUTA_MODELO_GGUF = r".\Llama-cpp\Models\Gemma 4 E4B\gemma-4-E4B-it-Q4_K_M.gguf"
NOMBRE_BD = "rag_fraude.db"
```

## Uso

1. Ejecutar el script:
```bash
python "RAG_con_NER.py"
```

2. El sistema automáticamente:
   - Genera 10 PDFs de prueba (auditoría, noticias, clima, etc.)
   - Lee y procesa los documentos
   - Extrae entidades con spaCy
   - Crea la base de datos SQLite

3. Interactuar con el sistema:
   - Ingresar una entidad a buscar (ej: "TechCorp", "Pedro Pérez", "Panamá")
   - Escribir la pregunta sobre esa entidad
   - El sistema recupera el contexto y genera una respuesta

4. Escribir `salir` para terminar.

## Base de Datos

La base de datos SQLite (`rag_fraude.db`) contiene:
- **Tabla `documentos`**: doc_id, nombre_archivo, texto
- **Tabla `entidades`**: doc_id, entidad, etiqueta

## Ejemplo de Uso

```
🔍 ¿Sobre qué entidad quieres investigar?: Pedro Pérez
💬 ¿Qué quieres saber sobre 'Pedro Pérez'?: ¿Qué se sabe sobre él?

🤖 IA RESPONDE:
[Respuesta generada basada en los documentos]
✅ Se encontraron 2 fragmentos relacionados.

Según los documentos, se sabe que él es Pedro Pérez, el CEO de TechCorp.

*   **Investigación Legal:** La Fiscalía Anticorrupción ha abierto diligencias contra él por presuntos delitos de fraude financiero, falsedad documental y evasión de impuestos.
*   **Contexto de la Investigación:** La investigación se originó a partir de información proporcionada por un exempleado de la compañía, quien aportó documentos que evidencian una red de sociedades instrumentales en Panamá y las Islas Vírgenes.
*   **Perfil Empresarial:** Pedro Pérez es considerado uno de los empresarios más influyentes del sector tecnológico y fue el líder de TechCorp, empresa que creció hasta convertirse en una multinacional con más de 10 000 empleados y presencia en 30 países.
*   **Impacto Corporativo:** Las prácticas cuestionadas habrían comenzado en 2019. Además, las acciones de TechCorp cayeron un 8,7% en la sesión de ayer.
*   **Restricciones Financieras:** Debido a la investigación, el Banco Central Europeo (BCE) suspendió temporalmente la autorización de compra de TechCorp Europe por parte del fondo soberano noruego, a la espera de que se resuelva la investigación por fraude en la cúpula directiva.
*   **Defensa:** Su abogado afirma que se trata de una campaña de desprestigio.

La información se obtiene de doc_02_noticias.pdf y doc_03_compra.pdf.

## Notas

- Requiere modelo GGUF de Llama.cpp (configurable en línea 13)
- Modelo spaCy: es_core_news_lg (español)
- Los PDFs de prueba contienen información sobre un caso de fraude corporativo ficticio
