from llama_cpp import Llama
import os
import glob 
import sqlite3
import pandas as pd
import spacy
from fpdf import FPDF
from PyPDF2 import PdfReader

# ==========================================
# CONFIGURACIÓN 
# ==========================================
RUTA_MODELO_GGUF = r"D:\Llama-cpp\Models\Gemma 4 E4B\gemma-4-E4B-it-Q4_K_M.gguf" # Ruta IA Local
NOMBRE_BD = "rag_fraude.db"

# ==========================================
# 1. GENERACIÓN DE PDFs DE PRUEBA
# ==========================================
def crear_pdfs_prueba():
    print("1. Generando archivos PDF de prueba (complejos)...")
    textos = {
        "doc_01_auditoria.pdf": (
            "INFORME DE AUDITORÍA INTERNA - TECH CORP 2023\n\n"
            "1. RESUMEN EJECUTIVO\n"
            "Este informe presenta los hallazgos de la auditoría financiera realizada a TechCorp durante el ejercicio fiscal 2023. "
            "Se analizaron transacciones por un total de 4.200 millones de euros, identificando irregularidades en el 3,8 % de las operaciones revisadas. "
            "La principal preocupación radica en una serie de transferencias por valor de 78 millones de euros hacia cuentas opacas en Panamá, "
            "las cuales carecen de justificación contractual suficiente y podrían estar vinculadas a un esquema de evasión fiscal.\n\n"
            "2. HALLAZGOS DETALLADOS\n"
            "2.1 Transferencias a Panamá\n"
            "Entre marzo y septiembre de 2023 se ejecutaron 14 transferencias a la entidad 'Caribe Holdings Inc.', con sede en Ciudad de Panamá. "
            "Los conceptos registrados ('servicios de consultoría estratégica') no están respaldados por informes ni entregables verificables. "
            "Los beneficiarios finales no figuran en los registros de compliance de TechCorp.\n"
            "2.2 Facturación cruzada\n"
            "Se detectaron facturas emitidas por proveedores pantalla en Islas Caimán que coinciden con pagos realizados por la filial de TechCorp en Luxemburgo. "
            "La suma asciende a 12,5 millones de euros y se sospecha que podrían haber sido utilizadas para desviar beneficios antes de impuestos.\n\n"
            "3. CONCLUSIÓN\n"
            "Los movimientos inusuales detectados requieren una investigación forense independiente. Se recomienda congelar cualquier operación "
            "con las entidades mencionadas y notificar a las autoridades regulatorias competentes (CNMV y Agencia Tributaria).\n\n"
            "Firmado: Dpto. de Auditoría Interna, 15 de enero de 2024."
        ),
        "doc_02_noticias.pdf": (
            "DIARIO ECONÓMICO NACIONAL - 3 DE FEBRERO DE 2024\n\n"
            "Titular: EL CEO DE TECHCORP, PEDRO PÉREZ, BAJO INVESTIGACIÓN POR FRAUDE Y EVASIÓN FISCAL\n\n"
            "Por Marta Sánchez, corresponsal de Economía.\n\n"
            "La Fiscalía Anticorrupción ha abierto diligencias contra Pedro Pérez, director ejecutivo de TechCorp, por presuntos delitos "
            "de fraude financiero, falsedad documental y evasión de impuestos. Según fuentes cercanas al caso, la investigación se inició "
            "tras recibir un soplo de un exempleado de la compañía, quien aportó documentos internos que muestran una red de sociedades "
            "instrumentales en Panamá y las Islas Vírgenes.\n\n"
            "Pérez, de 54 años, es considerado uno de los empresarios más influyentes del sector tecnológico. Bajo su liderazgo, TechCorp "
            "pasó de ser una startup a una multinacional con más de 10 000 empleados y presencia en 30 países. Sin embargo, las prácticas "
            "que ahora se le atribuyen habrían comenzado en 2019, coincidiendo con la expansión internacional de la empresa.\n\n"
            "El abogado defensor de Pérez ha declarado que 'se trata de una campaña de desprestigio' y que su cliente colaborará plenamente "
            "con la justicia. Mientras tanto, las acciones de TechCorp cayeron un 8,7 % en la sesión de ayer. La junta directiva ha convocado "
            "una reunión extraordinaria para evaluar la situación y podría destituir al ejecutivo si las acusaciones se confirman.\n\n"
            "La investigación también alcanza al director financiero y a un despacho de abogados panameño que habría facilitado la creación "
            "de las sociedades offshore. Se espera que en las próximas semanas se produzcan las primeras citaciones judiciales."
        ),
        "doc_03_compra.pdf": (
            "COMUNICADO DE PRENSA - BANCO CENTRAL EUROPEO\n\n"
            "El Consejo de Supervisión del BCE ha aprobado hoy la adquisición del 100 % de la plataforma de pagos PayLink por parte de Apple Inc., "
            "tras verificar que la operación no compromete la estabilidad financiera de la zona euro. No obstante, en la misma sesión ha decidido "
            "suspender temporalmente la autorización de compra de TechCorp Europe por parte del fondo soberano noruego, a la espera de que se "
            "resuelva la investigación por fraude que afecta a la cúpula directiva de TechCorp.\n\n"
            "La compra de PayLink por Apple, valorada en 2.300 millones de euros, permitirá al gigante estadounidense reforzar su división de "
            "servicios financieros y competir directamente con bancos tradicionales en el segmento de pagos móviles. El BCE ha impuesto condiciones "
            "estrictas en materia de protección de datos y prevención del blanqueo de capitales.\n\n"
            "Respecto a TechCorp, la portavoz del organismo, Ana Keller, declaró: 'No podemos autorizar una transacción de esta envergadura mientras "
            "existan dudas razonables sobre la integridad de los responsables de la entidad. La lucha contra el fraude es una prioridad para el BCE, "
            "y cualquier decisión se tomará cuando las autoridades judiciales hayan concluido su labor'. La suspensión afecta a un acuerdo que "
            "rondaba los 5.000 millones de euros y que suponía la puerta de entrada del fondo noruego al mercado tecnológico europeo.\n\n"
            "Analistas del sector consideran que este varapalo podría desencadenar una reestructuración forzosa en TechCorp y acelerar la salida "
            "de Pedro Pérez de la dirección."
        ),
        "doc_04_receta.pdf": (
            "LA AUTÉNTICA PAELLA VALENCIANA: HISTORIA, INGREDIENTES Y ELABORACIÓN\n\n"
            "Introducción\n"
            "La paella es el plato más emblemático de la gastronomía española. Originaria de la Comunidad Valenciana, sus primeras referencias "
            "datan del siglo XVIII, cuando los campesinos cocinaban arroz en una sartén ancha ('paella' en valenciano) con los ingredientes "
            "que tenían a mano: conejo, pollo, verduras de temporada y, ocasionalmente, caracoles. Con el tiempo, la receta evolucionó hasta "
            "convertirse en un icono mundial, aunque la versión tradicional valenciana sigue rigiéndose por estrictos cánones.\n\n"
            "Ingredientes (para 6 personas)\n"
            "- 500 g de arroz bomba (o variedad de grano redondo)\n"
            "- 600 g de pollo troceado\n"
            "- 400 g de conejo troceado\n"
            "- 200 g de judías verdes planas (bajoqueta)\n"
            "- 100 g de garrofón (judión blanco)\n"
            "- 150 g de tomate triturado natural\n"
            "- 1 cucharadita de pimentón dulce\n"
            "- Aceite de oliva virgen extra, sal\n"
            "- Unas hebras de azafrán tostado\n"
            "- Opcional: caracoles serranos (vaquetes), romero fresco\n\n"
            "Elaboración paso a paso\n"
            "1. Calienta el aceite en la paella a fuego vivo y dora el pollo y el conejo durante 10 minutos, removiendo para que se sellen bien.\n"
            "2. Añade las judías verdes y sofríelas durante 5 minutos. Incorpora el tomate triturado y remueve hasta que reduzca y pierda el agua.\n"
            "3. Agrega el pimentón y, rápidamente (para que no se queme), vierte agua caliente hasta casi el borde de la paella (aproximadamente "
            "1,5 litros). Añade el garrofón y la sal. Deja hervir a fuego medio-alto durante 30-40 minutos para conseguir un buen caldo.\n"
            "4. Pasado ese tiempo, corrige de sal y añade el azafrán desmenuzado. Si usas caracoles, este es el momento de incorporarlos.\n"
            "5. Espolvorea el arroz formando un círculo desde el centro hacia el exterior, sin remover. Cocina a fuego alto los primeros 8-10 minutos "
            "y luego baja a fuego medio durante otros 8-10 minutos más.\n"
            "6. En los últimos minutos, puedes colocar unas ramitas de romero sobre la superficie para aromatizar. Retira del fuego cuando el caldo "
            "se haya consumido y deja reposar la paella tapada con un paño limpio durante 5 minutos antes de servir.\n\n"
            "Variantes y consejos\n"
            "La paella marinera sustituye la carne por marisco y pescado. La mixta combina ambos. Evita añadir cebolla (la tradición valenciana la "
            "prohíbe) y no remuevas el arroz una vez incorporado, pues perdería la textura deseada."
        ),
        "doc_05_espacio.pdf": (
            "PROGRAMA ARTEMIS: EL REGRESO DEL HOMBRE A LA LUNA\n\n"
            "1. Visión general\n"
            "Artemis es el programa espacial internacional liderado por la NASA con el objetivo de establecer una presencia humana sostenible en la Luna "
            "y preparar futuras misiones tripuladas a Marte. Su nombre rinde homenaje a la hermana gemela de Apolo en la mitología griega y simboliza "
            "el compromiso de llevar a la primera mujer y al próximo hombre a la superficie lunar en la década de 2020.\n\n"
            "2. Arquitectura tecnológica\n"
            "El programa se sustenta en tres pilares: el cohete SLS (Space Launch System), la cápsula Orion y el Gateway lunar. El SLS es el lanzador "
            "más potente jamás construido, capaz de enviar 26 toneladas a la órbita lunar en su versión Block 1. Orion proporciona soporte vital "
            "para una tripulación de hasta 4 astronautas durante 21 días. El Gateway será una estación orbital en la órbita de halo casi rectilínea "
            "(NRHO) que servirá como puerto de operaciones para alunizajes, experimentos científicos y acoplamiento de módulos internacionales.\n\n"
            "3. Misiones planificadas\n"
            "Artemis I (noviembre 2022) fue una prueba no tripulada que validó todos los sistemas. Artemis II (prevista para 2025) llevará a cuatro "
            "astronautas en una órbita lunar de 10 días. Artemis III (no antes de 2026) llevará a la superficie del polo sur selenita a dos "
            "astronautas, donde recogerán muestras de hielo de agua en zonas permanentemente sombreadas. Hasta la fecha, la NASA ha seleccionado "
            "el módulo de aterrizaje Starship de SpaceX para esa primera misión de descenso.\n\n"
            "4. Colaboración internacional\n"
            "La ESA, la JAXA, la CSA y otras agencias participan aportando módulos del Gateway, sistemas robóticos y experimentos. La cooperación "
            "se articula mediante los Acuerdos Artemis, firmados ya por más de 30 naciones, que establecen principios de transparencia, "
            "interoperabilidad y uso pacífico del espacio.\n\n"
            "5. Relevancia científica y económica\n"
            "Artemis permitirá estudiar la geología del polo sur lunar, evaluar recursos in situ (agua, regolito) y probar tecnologías de "
            "habitabilidad que reducirán el coste de futuras misiones marcianas. El retorno económico estimado de la exploración lunar supera "
            "los 60 mil millones de dólares en la próxima década, según la NASA."
        ),
        "doc_06_clima.pdf": (
            "IMPACTOS DEL CALENTAMIENTO GLOBAL EN EL ÁRTICO\n\n"
            "El Ártico se calienta al menos tres veces más rápido que la media mundial, un fenómeno conocido como amplificación ártica. "
            "Los datos del satélite CryoSat-2 de la ESA indican que el hielo marino estival ha disminuido un 13 % por década desde 1979, "
            "alcanzando mínimos históricos en 2023. Esta pérdida tiene consecuencias en cascada sobre los ecosistemas, las comunidades "
            "indígenas y el clima global.\n\n"
            "Deshielo acelerado y efecto albedo\n"
            "El hielo ártico refleja gran parte de la radiación solar; al derretirse, el océano oscuro absorbe más energía, lo que calienta "
            "aún más la región en un bucle de retroalimentación positiva. Las simulaciones climáticas del IPCC proyectan que el Ártico podría "
            "quedarse sin hielo en septiembre antes de 2050 si las emisiones continúan al ritmo actual.\n\n"
            "Impacto en la fauna\n"
            "Los osos polares (Ursus maritimus) dependen del hielo marino para cazar focas. Estudios de la Universidad de Alberta muestran "
            "que el período de ayuno de las osas preñadas se ha alargado, reduciendo la tasa de natalidad en un 20 % en los últimos 20 años. "
            "Otras especies como las morsas del Pacífico y las focas anilladas también sufren la pérdida de hábitat.\n\n"
            "Liberación de metano del permafrost\n"
            "El deshielo del permafrost, que cubre el 24 % de las tierras del hemisferio norte, libera metano, un gas de efecto invernadero "
            "80 veces más potente que el CO₂ en un horizonte de 20 años. La retroalimentación metano-permafrost podría añadir entre 0,2 y 0,5 °C "
            "al calentamiento global para 2100 (Nature Climate Change, 2022).\n\n"
            "Acciones y acuerdos internacionales\n"
            "La Cumbre de Glasgow reafirmó el objetivo de limitar el calentamiento a 1,5 °C, pero las políticas actuales nos sitúan en una "
            "trayectoria de 2,4 °C. La protección del Ártico requiere una reducción drástica de las emisiones de carbono negro (black carbon) "
            "y la creación de áreas marinas protegidas en el alto Ártico. La cooperación del Consejo Ártico es esencial, aunque las tensiones "
            "geopolíticas dificultan los consensos."
        ),
        "doc_07_historia.pdf": (
            "LA PAZ ROMANA: ESPLENDOR Y CONTRADICCIONES DEL IMPERIO\n\n"
            "Durante los siglos I y II d.C., el Imperio Romano gozó de un período de estabilidad conocido como la Pax Romana. Iniciado por Augusto "
            "en el 27 a.C., este largo paréntesis de paz interna y expansión territorial permitió un florecimiento cultural, económico y "
            "arquitectónico sin precedentes. Las calzadas romanas conectaban Hispania con Mesopotamia; el latín y el derecho romano unificaban "
            "desde Britania hasta el norte de África. Ciudades como Roma, Alejandría y Éfeso superaban los 500 000 habitantes.\n\n"
            "Sin embargo, la Pax Romana también se sostuvo mediante la represión de revueltas y la esclavitud. Las minas de plata de Cartagena "
            "y las canteras de mármol de Carrara funcionaban gracias a miles de trabajadores forzosos. El gasto militar, que llegó a absorber "
            "el 40 % del presupuesto imperial, se financiaba con tributos que gravaban sobre todo a las provincias conquistadas. Los emperadores "
            "difundían la idea de una 'misión civilizadora', pero la resistencia al dominio romano fue constante: los pueblos germanos, los partos "
            "y las tribus bereberes mantuvieron una presión fronteriza que finalmente contribuiría a la caída del Imperio de Occidente.\n\n"
            "El legado de la Pax Romana es ambivalente: por un lado, sentó las bases del derecho europeo, la ingeniería (acueductos, puentes) y la "
            "propagación del cristianismo; por otro, normalizó la explotación sistemática de territorios y poblaciones. Historiadores como Edward "
            "Gibbon vieron en esta época el germen de la decadencia posterior, mientras que otros destacan los avances en gobernanza, comercio y "
            "urbanismo. Sea como fuere, la Pax Romana sigue siendo un referente ineludible para entender la construcción de los imperios y su "
            "impacto a largo plazo."
        ),
        "doc_08_medicina.pdf": (
            "MÁS ALLÁ DEL COVID-19: EL FUTURO DE LAS VACUNAS DE ARNm\n\n"
            "La pandemia de COVID-19 catalizó una revolución en la tecnología de vacunas. Las vacunas basadas en ARN mensajero (ARNm) "
            "demostraron una eficacia y seguridad notables, allanando el camino para su aplicación en otras enfermedades. Actualmente, "
            "decenas de ensayos clínicos exploran el uso de ARNm contra el cáncer, enfermedades infecciosas y trastornos genéticos.\n\n"
            "Vacunas personalizadas contra el cáncer\n"
            "Empresas como BioNTech y Moderna están desarrollando vacunas terapéuticas oncológicas que se diseñan a partir de la secuenciación "
            "del tumor de cada paciente. Las mutaciones específicas del tumor (neoantígenos) se codifican en moléculas de ARNm que, al ser "
            "inyectadas, instruyen al sistema inmunitario para atacar selectivamente las células cancerosas. Resultados preliminares en melanoma "
            "y cáncer de pulmón no microcítico muestran reducciones de la recurrencia superiores al 40 % en combinación con inmunoterapia.\n\n"
            "Nuevas vacunas infecciosas\n"
            "Se investigan vacunas de ARNm para la gripe universal, el VIH, la tuberculosis y el citomegalovirus. La ventaja es la rapidez de "
            "producción: mientras las vacunas tradicionales requieren cultivar virus en huevos o células, la síntesis química del ARNm puede "
            "escalarse en semanas. Moderna ya ha anunciado resultados positivos en fase II para su vacuna combinada COVID-gripe.\n\n"
            "Aplicaciones en enfermedades raras\n"
            "La tecnología permite reemplazar proteínas defectuosas en trastornos metabólicos, como la fibrosis quística o la fenilcetonuria, "
            "administrando ARNm que codifica la proteína sana. Aunque los retos de administración y toxicidad hepática son significativos, "
            "los avances en nanopartículas lipídicas dirigidas a tejidos están abriendo nuevas posibilidades terapéuticas.\n\n"
            "Consideraciones éticas y regulatorias\n"
            "La rápida evolución de estas plataformas plantea preguntas sobre su acceso global, la farmacovigilancia a largo plazo y la posible "
            "confusión pública entre vacunas modificadoras de células y terapias génicas. La OMS ha instado a crear marcos regulatorios ágiles "
            "que garanticen la seguridad sin frenar la innovación."
        ),
        "doc_09_tecnologia.pdf": (
            "TUTORIAL: CÓMO MONTAR UN SERVIDOR CASERO CON DOCKER Y PORTAINER\n\n"
            "1. Introducción\n"
            "Docker permite empaquetar aplicaciones en contenedores ligeros, mientras que Portainer facilita su gestión mediante una interfaz web "
            "intuitiva. Montar tu propio servidor doméstico te permitirá alojar servicios como Nextcloud, Plex, Home Assistant o un gestor de "
            "descargas sin depender de la nube de terceros, mejorando la privacidad y el control sobre tus datos.\n\n"
            "2. Hardware mínimo recomendado\n"
            "Un mini PC de bajo consumo (Intel N100, Raspberry Pi 4/5 o un equipo antiguo) con al menos 4 GB de RAM y 64 GB de almacenamiento "
            "será suficiente para empezar. Se recomienda instalar Ubuntu Server 22.04 LTS como sistema operativo base.\n\n"
            "3. Instalación de Docker\n"
            "sudo apt update && sudo apt upgrade\n"
            "sudo apt install docker.io docker-compose\n"
            "sudo systemctl enable docker --now\n"
            "sudo usermod -aG docker $USER\n\n"
            "4. Despliegue de Portainer\n"
            "docker volume create portainer_data\n"
            "docker run -d -p 8000:8000 -p 9443:9443 --name=portainer --restart=always \\\n"
            "  -v /var/run/docker.sock:/var/run/docker.sock \\\n"
            "  -v portainer_data:/data portainer/portainer-ce:latest\n\n"
            "Accede a https://<IP_DEL_SERVIDOR>:9443, crea el usuario administrador y conecta al endpoint local.\n\n"
            "5. Primeros servicios recomendados\n"
            "- Pi-hole: bloqueador de anuncios a nivel de red.\n"
            "- Nginx Proxy Manager: gestiona certificados SSL y redirecciona dominios.\n"
            "- Paperless-ngx: digitaliza y organiza documentos escaneados automáticamente.\n"
            "- Uptime Kuma: monitoriza tus servicios y envía alertas si algo falla.\n\n"
            "6. Seguridad\n"
            "Configura un firewall (UFW), usa fail2ban para prevenir ataques de fuerza bruta y activa copias de seguridad automáticas con scripts "
            "simples. Recuerda que exponer servicios a Internet conlleva riesgos; una VPN como WireGuard es la forma más segura de acceder "
            "desde el exterior.\n\n"
            "Con este servidor autogestionado podrás ir añadiendo servicios según tus necesidades, aprendiendo sobre administración de sistemas "
            "en un entorno seguro y controlado."
        ),
        "doc_10_deporte.pdf": (
            "CRÓNICA: ARGENTINA CAMPEONA DEL MUNDO TRAS UNA FINAL ÉPICA\n\n"
            "Lusail, Catar — La selección argentina conquistó su tercera Copa del Mundo al vencer a Francia en una final que será recordada "
            "como una de las mejores de la historia. El encuentro, disputado el 18 de diciembre de 2022 ante 88 966 espectadores, terminó 3-3 "
            "tras la prórroga y se decidió por penaltis (4-2) a favor de la albiceleste.\n\n"
            "Primera parte\n"
            "Argentina dominó el primer tiempo con una presión alta y un Messi estelar. A los 23 minutos, el 10 transformó un penalti cometido "
            "sobre Di María. Poco después, una fulgurante contra culminó con un remate cruzado de Di María (min. 36) que puso el 2-0. Francia, "
            "sin apenas presencia ofensiva, se fue al descanso sin tirar a puerta.\n\n"
            "Reacción francesa\n"
            "En el minuto 80, un penalti por mano de Otamendi dio vida a Francia. Mbappé lo convirtió y, apenas 97 segundos después, empató "
            "con una volea espectacular. El ímpetu francés se estrelló contra un Dibu Martínez providencial, que en el último minuto de la prórroga "
            "sacó un mano a mano imposible a Kolo Muani.\n\n"
            "Definición desde los once metros\n"
            "Mbappé y Messi anotaron sus lanzamientos, pero el portero argentino detuvo el disparo de Coman y Tchouaméni lo mandó fuera. "
            "Montiel selló el triunfo para Argentina y desató la euforia en Buenos Aires.\n\n"
            "Impacto global\n"
            "Lionel Messi, que cumplió 35 años durante el torneo, culminó su carrera con el único título que le faltaba, consolidando "
            "su legado como uno de los mejores futbolistas de la historia. Los festejos en Argentina congregaron a 5 millones de personas "
            "en Buenos Aires, en una celebración que paralizó el país."
        ),
    }
    
    for nombre_archivo, texto in textos.items():
        pdf = FPDF()
        pdf.add_page()
        pdf.set_font("Arial", size=12)
        pdf.multi_cell(0, 10, txt=texto.encode('latin-1', 'replace').decode('latin-1'))
        pdf.output(nombre_archivo)
    return list(textos.keys())

# ==========================================
# 2. LECTURA DE PDFs
# ==========================================
import re

def limpiar_texto(texto):
    # 1. Unir guiones de final de línea: "inves-\ntigación" -> "investigación"
    texto = re.sub(r'(\w+)-\n(\w+)', r'\1\2', texto)
    
    # 2. Reemplazar saltos de línea simples (dentro de párrafos) por espacio
    #    pero conservar saltos dobles (separación de párrafos)
    texto = re.sub(r'(?<!\n)\n(?!\n)', ' ', texto)
    
    # 3. Normalizar espacios múltiples y tabuladores a un solo espacio
    texto = re.sub(r'[ \t]+', ' ', texto)
    
    # 4. Eliminar caracteres de control excepto el salto de línea (\n)
    #    (quedan solo los saltos de línea que hemos respetado y los espacios)
    texto = re.sub(r'[\x00-\x08\x0b\x0c\x0e-\x1f\x7f]', '', texto)
    
    # 5. Eliminar espacios al principio o final, y asegurar que los párrafos queden bien
    texto = texto.strip()
    texto = re.sub(r' *\n *', '\n', texto)  # quitar espacios antes/después de cada salto
    
    return texto


def leer_pdfs(lista_archivos):
    print("2. Leyendo contenido de los PDFs...")
    documentos = []
    for archivo in lista_archivos:
        lector = PdfReader(archivo)
        texto_completo = ""
        for pagina in lector.pages:
            texto_completo += pagina.extract_text() + " "

        # Limpiamos el texto para mejorar la calidad de la extracción
        texto_completo = limpiar_texto(texto_completo)
        
        # Guardamos ambos para no tener fallos en SQL
        documentos.append({
            "doc_id": archivo,           # Ruta completa o ID
            "nombre_archivo": archivo,    # Nombre que usaremos en la consulta
            "texto": texto_completo.strip()
        })
    return documentos

# ==========================================
# 3. EXTRACCIÓN NER (spaCy)
# ==========================================
def extraer_entidades(documentos):
    print("3. Extrayendo entidades con spaCy...")
    nlp = spacy.load("es_core_news_lg")
    entidades = []
    
    for doc in documentos:
        analisis = nlp(doc["texto"])
        for ent in analisis.ents:
            entidades.append({
                "doc_id": doc["doc_id"],
                "entidad": ent.text,
                "etiqueta": ent.label_
            })
    return entidades

# ==========================================
# 4. CREACIÓN DE BASE DE DATOS (SQLite)
# ==========================================
def crear_base_datos(documentos, entidades):
    print("4. Creando base de datos tabular...")
    conexion = sqlite3.connect(NOMBRE_BD)
    
    # Si actualizaste el paso 2 (leer_pdfs), df_docs ahora 
    # tendrá automáticamente las columnas: doc_id, nombre_archivo y texto
    df_docs = pd.DataFrame(documentos)
    df_ents = pd.DataFrame(entidades)
    
    print(df_docs)
    print(df_ents)
    # Guardamos en la base de datos
    df_docs.to_sql("documentos", conexion, if_exists="replace", index=False)
    df_ents.to_sql("entidades", conexion, if_exists="replace", index=False)
    
    conexion.close()
    print("   ✅ Base de datos actualizada con éxito.")

# ==========================================
# 5. RETRIEVER (Recuperación por Entidad)
# ==========================================
def recuperar_contexto(entidad_buscada):
    print(f"5. Buscando '{entidad_buscada}' en la base de datos...")
    conexion = sqlite3.connect(NOMBRE_BD)
    
    query = """
        SELECT DISTINCT d.texto, d.doc_id 
        FROM entidades e
        JOIN documentos d ON e.doc_id = d.doc_id
        WHERE e.entidad LIKE ?
    """
    
    df_resultados = pd.read_sql_query(query, conexion, params=(f'%{entidad_buscada}%',))
    conexion.close()
    
    if df_resultados.empty:
        return "No se encontró información sobre esta entidad en la base de datos."
    
    contexto_lista = []
    for _, row in df_resultados.iterrows():
        # Usamos doc_id como referencia
        bloque = f"--- FUENTE: {row['doc_id']} ---\n"
        bloque += f"{row['texto']}\n"
        contexto_lista.append(bloque)
    
    contexto_final = "\n\n".join(contexto_lista)
    print(f"   ✅ Se encontraron {len(df_resultados)} fragmentos relacionados.")
    return contexto_final
# ==========================================
# 6. GENERACIÓN (Llama.cpp)
# ==========================================
# --- CARGA GLOBAL (Solo se hace una vez al inicio) ---
print("Cargando modelo en la GPU...")
llm = Llama(
    model_path=RUTA_MODELO_GGUF, 
    n_ctx=16384, 
    n_gpu_layers=33, 
    verbose=False
)

# --- AHORA LA FUNCIÓN SOLO GENERA ---
def generar_respuesta(pregunta, contexto):
    
    prompt = f"""Eres un asistente experto en análisis de información. 
Tu tarea es responder de forma clara y objetiva basándote EXCLUSIVAMENTE en el contexto proporcionado.

CONTEXTO DE DOCUMENTOS:
{contexto}

PREGUNTA DEL USUARIO: {pregunta}

INSTRUCCIONES:
1. Usa un tono profesional y directo, se conciso, intenta no transcribir solo si es necesario extraer algo textual.
2. Si la información proviene de varios documentos, relaciónalos.
3. Si la respuesta no está en el texto, di simplemente que no hay datos suficientes.

RESPUESTA: """

    print("   Generando respuesta...")
    
    salida = llm(
        prompt, 
        max_tokens=512, 
        temperature=0.9,
        stop=["PREGUNTA:", "CONTEXTO:"]
    )
    
    texto = salida['choices'][0]['text'].strip()
    
    # DEBUG: Si sigue saliendo vacío, esto nos dirá por qué
    if not texto:
        print(f"⚠️ Alerta: La IA devolvió vacío. Info de salida: {salida['choices'][0]['finish_reason']}")
        
    return texto

# ==========================================
# FLUJO PRINCIPAL DE EJECUCIÓN
# ==========================================
if __name__ == "__main__":
    
    print("-" * 50)
    print("INICIANDO SISTEMA RAG LOCAL")
    print("-" * 50)
    
    archivos_generados = crear_pdfs_prueba()
    docs_leidos = leer_pdfs(archivos_generados)
    entidades_encontradas = extraer_entidades(docs_leidos)
    crear_base_datos(docs_leidos, entidades_encontradas)
    
    
    print("\n" + "="*50)
    print("SISTEMA RAG LISTO. Escribe 'salir' para terminar.")
    print("="*50)

    while True:
        entidad_a_buscar = input("\n🔍 ¿Sobre qué entidad quieres investigar?: ")
        
        if entidad_a_buscar.lower() == 'salir':
            break
            
        pregunta_usuario = input(f"💬 ¿Qué quieres saber sobre '{entidad_a_buscar}'?: ")

        # 1. Recuperar contexto basado en la entidad
        contexto = recuperar_contexto(entidad_a_buscar)
        
        if "No se encontró" in contexto:
            print("❌ No encontré esa entidad en los documentos. Intenta con otra.")
            continue

        # 2. Generar respuesta con la IA
        respuesta = generar_respuesta(pregunta_usuario, contexto)
        
        print("\n🤖 IA RESPONDE:")
        print(respuesta)
        print("-" * 30)