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

En el archivo `RAG con NER4.py`, configurar las rutas:

```python
RUTA_MODELO_GGUF = r"D:\Llama-cpp\Models\Gemma 4 E4B\gemma-4-E4B-it-Q4_K_M.gguf"
NOMBRE_BD = "rag_fraude.db"
```

## Uso

1. Ejecutar el script:
```bash
python "RAG con NER4.py"
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
```

## Notas

- Requiere modelo GGUF de Llama.cpp (configurable en línea 13)
- Modelo spaCy: es_core_news_lg (español)
- Los PDFs de prueba contienen información sobre un caso de fraude corporativo ficticio