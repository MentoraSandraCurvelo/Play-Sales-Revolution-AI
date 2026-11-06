# Preferencias de Sandra Curvelo (IAM™)

## Regla: todo lo visual pasa por "Claude Design"
Todo lo que salga visual (tableros, mesas, reportes, páginas, presentaciones, piezas para redes) pasa siempre por el estándar que Sandra llama "Claude Design", sin que lo tenga que pedir:
- Estilo terminal de Wall Street: fondo oscuro, cinta de cotizaciones animada, verde para lo que sube, rojo para lo que baja, ámbar para lo neutro.
- KPIs dinámicos: las cifras cuentan hacia arriba al cargar y llevan un indicador ▲ o ▼ frente a la meta.
- Gráficos en 3D (barras con cara frontal, lateral y superior) y tarjetas 3D que se inclinan con el mouse, con animaciones de entrada.
- Un avatar de Isaía que camina de un lado a otro y va diciendo los hallazgos clave en un globo de texto.
- Identidad IAM™: anillo ⭕ y rojo IAM como acento.
- Respetar a quien desactiva animaciones (prefers-reduced-motion) y no inventar cifras: todo sale de datos reales, con fecha de corte.
- Tipografía de contraste (aprobada por Sandra, siempre así): títulos grandes en serif blanco con la segunda frase en degradado rojo IAM → ámbar; etiquetas y cifras en letra monoespaciada en mayúsculas con espaciado amplio; texto de apoyo en gris claro con lo clave en blanco negrita. Fondo casi negro.
- Piezas para Instagram (carruseles, historias, frases): no todo en negro. Alternar fondos: casi negro, blanco, gris claro y beige. En fondo claro se mantiene la misma tipografía de contraste, con el título en serif casi negro, la segunda frase en degradado rojo IAM → ámbar y el texto de apoyo en gris oscuro con lo clave en negro negrita. Ninguna semana repite el mismo fondo en todas sus piezas.
- Portadas de carruseles: montaje en ElevenLabs con temas de IA (saliendo de un deportivo rojo sin marcas visibles, puente de una nave espacial, tablero o hologramas en 3D, ciudad del futuro), siempre con su misma cara y su mismo pelo.
- Fotos: usar fotos reales de Sandra de Dropbox ("/Fotos Profesionales" y "/2-Contenido/Mujer radiante", las de escenario con traje rojo). Evitar fotos donde aparezcan otras personas reconocibles sin su permiso.
- Montajes con IA (aprobados por Sandra): para cada pieza, además de sus fotos reales, crear montajes en ElevenLabs a partir de sus fotos de Dropbox, cambiando atuendo, pose y escenario (oficina ejecutiva de noche, sala tipo Wall Street, escenario, y escenarios futuristas: puente de una nave espacial, hologramas, ciudad del futuro), manteniendo su misma cara y su mismo pelo. Generarlos en formato vertical para Instagram y mostrarle cada montaje antes de usarlo: si la cara no es fiel, no se usa.
- Sin avatares hablando: Sandra probó los avatares de foto con voz (4 nov 2026) y no le gustaron (dientes raros, ritmo pausado, se ven ficticios). Sus videos son tomas reales grabadas por ella; los montajes con IA son solo imágenes fijas o clips cortos sin habla.
- Cuerpo en los montajes: Sandra es delgada de cadera y de piernas. En todo montaje de cuerpo entero o de rodillas para arriba, pedir explícitamente cadera y piernas delgadas.
- Recorte de Sandra en los videos (6 nov 2026): siempre con el modelo de video RVM (`estrategia/instagram/herramientas/rvm_comp.py`): cabello y bordes cuadro por cuadro, color de piel sin el reflejo de la pared, luz del fondo que envuelve la silueta, fondo con profundidad de campo, nitidez suave y grano parejo. Nunca el recorte rápido de baja resolución.
- Antes de entregar, revisar el diseño completo una vez más contra esta lista.

## Regla: cada "Comenta [PALABRA]" lleva su guía y su respuesta automática
Siempre que una pieza pida comentar una palabra clave, antes de publicarla:
1. Crear la guía de esa palabra como página con el estilo de Sandra (por ejemplo, la guía de prompts para CLAUDE y LINKEDIN o la guía para vender con Claude para VENTA y VENTAS).
2. Agregar la palabra a `estrategia/instagram/automatizacion/responder_comentarios.py`, que cada hora responde en público y envía la guía por mensaje directo.
3. Recordarle a Sandra que comparta la guía con "cualquier persona con el enlace".

## Publicación
Sandra graba y aprueba el material; Claude decide la fecha y la hora de publicación de las piezas aprobadas, las programa y le avisa cada vez (4 nov 2026). Lo que no ha visto Sandra no se publica.

## Idioma y tono
Español de Colombia, tuteo. Sin guiones para separar ideas. Números y signos en su formato. "Dinero", no "plata".

## Frecuencia y pauta en Instagram (aprobado 5 nov 2026)
- 5 publicaciones por semana: lunes reel 12:30 p. m., martes carrusel 6:30 p. m., miércoles reel 12:30 p. m., viernes carrusel 6:30 p. m., sábado reel 12:30 p. m. (hora Colombia). Referencia: Eduardo Vázquez publica 4.8 por semana.
- Sandra graba un día por semana todas las tomas de los reels de esa semana; Claude edita y hace los carruseles.
- Pauta: solo se promociona lo que en sus primeras 48 horas supera la mediana de alcance (411 reels, 238 carruseles) o llega a 20 compartidos. Claude avisa con los números y Sandra decide el presupuesto. Claude nunca paga ni promociona por su cuenta.

## Historias y comentarios (aprobado 5 nov 2026)
- Claude publica historias por la API: una después de cada publicación del feed (aviso "Nuevo reel" o "Nuevo carrusel") y una de detrás de cámaras los domingos, con fotos y videos reales de Sandra de Dropbox. Fondos alternados y difuminar a otras personas reconocibles.
- La API no permite stickers ni compartir la publicación con enlace; eso lo hace Sandra en la app si quiere.
- Claude no comenta en cuentas ajenas (la API no lo permite y Instagram lo castiga como spam). Cada mañana le deja a Sandra 5 publicaciones de cuentas de su tema con un comentario sugerido para que ella lo pegue.

## Cifras de marca
De aquí en adelante (5 nov 2026): presencia en 8 países (Colombia, México, Perú, Argentina, Ecuador, Panamá, Costa Rica y Brasil). Las piezas ya hechas con "7 países" se dejan como están.

## Cliente privado
Comfacesar no se nombra en público: "una caja de compensación muy grande en Colombia". Cifras de cierre: 140 horas por semana, $255 millones a 12 meses.
