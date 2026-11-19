# Análisis del impacto cuántico en la ciberseguridad
Sara Jaimes Castañeda · Arquitectura de Computadores

## 1. Inventario de algoritmos criptográficos vulnerables

Para el inventario se clasificaron los algoritmos criptográficos más usados según el ataque cuántico que los afecta. Los asimétricos se basan en la factorización de enteros o en el logaritmo discreto, dos problemas que el algoritmo de Shor resuelve en tiempo polinómico. En cambio, el cifrado simétrico y las funciones hash solo pierden parte de su margen de seguridad frente a la búsqueda de Grover.

| Algoritmo | Tipo | Vulnerabilidad cuántica | Algoritmo atacante | Acción recomendada |
|---|---|---|---|---|
| RSA-2048 / RSA-4096 | Cifrado y firma asimétricos | Roto completamente | Shor (factorización) | Reemplazar con ML-KEM para el intercambio de claves y con ML-DSA para las firmas |
| ECDSA (P-256, P-384) | Firma digital | Roto completamente | Shor (logaritmo discreto en curva elíptica) | Reemplazar con ML-DSA |
| ECDH / X25519 | Intercambio de clave | Roto completamente | Shor (logaritmo discreto en curva elíptica) | Reemplazar con ML-KEM, pasando primero por el modo híbrido X25519MLKEM768 |
| AES-128 | Cifrado simétrico | Debilitado (clave efectiva cercana a 64 bits) | Grover O(√N) | Migrar a AES-256 |
| AES-256 | Cifrado simétrico | Aceptable (clave efectiva cercana a 128 bits) | Grover O(√N) | Mantener |
| SHA-256 | Función hash | Debilitado en teoría (colisiones de 2¹²⁸ a 2⁸⁵) | Grover | Migrar a SHA-384 o SHA-512 en sistemas de larga vida |
| SHA3-256 | Función hash | Debilitado en teoría, en el mismo nivel que SHA-256 | Grover | Usar SHA3-384 o mayor en sistemas de larga vida |

La diferencia entre "roto completamente" y "debilitado" está en qué tanto se pierde. Un algoritmo roto permite que un atacante con un computador cuántico suficientemente grande recupere la clave privada, y con ella puede descifrar también todo el tráfico que haya guardado antes, así que se pierde la confidencialidad retroactiva. Como referencia del costo, Gidney y Ekerå (2021) estimaron que RSA-2048 se podría factorizar en 8 horas con 20 millones de qubits ruidosos, suponiendo una tasa de error físico por puerta de 10⁻³.

Un algoritmo debilitado, en cambio, sigue siendo seguro si se le da más margen. La regla práctica dice que Grover reduce a la mitad el tamaño efectivo de la clave, aunque el informe ETSI GR QSC 006 aclara que, al sumar el costo de la corrección de errores, romper una clave AES-128 tomaría el tiempo de unas 2⁸¹ operaciones y no de 2⁶⁴ (ETSI, 2017). Por eso basta con duplicar la longitud de la clave, y AES-256 se mantiene.

En las funciones hash el riesgo es todavía menor en la práctica. El mismo informe concluye que SHA-2 y SHA-3 con salidas de al menos 256 bits resistirán ataques cuánticos hasta mucho después de 2050, y que para buscar colisiones un computador cuántico no ofrece una ventaja real frente a un clúster clásico (ETSI, 2017). Aun así, la migración a salidas de 384 o 512 bits se recomienda para sistemas que deben protegerse durante décadas, ya que el costo de hacerlo es bajo.

## 2. Estándares NIST PQC 2024

El 13 de agosto de 2024 el NIST publicó tres estándares post-cuánticos. Dos se basan en retículos y uno solo en funciones hash. Cada estándar define varios conjuntos de parámetros que el NIST ubica en categorías de seguridad, donde la categoría 1 equivale a la dificultad de romper un cifrador por bloques con clave de 128 bits, la 3 a una de 192 bits y la 5 a una de 256 bits.

| Estándar | Parámetro | Categoría NIST | Clave pública (bytes) | Clave privada (bytes) | Firma o ciphertext (bytes) | Velocidad relativa |
|---|---|---|---|---|---|---|
| ML-KEM (FIPS 203) | ML-KEM-512 | 1 | 800 | 1632 | 768 (ciphertext) | 45 000 / 70 000 op/s |
| ML-KEM (FIPS 203) | ML-KEM-768 | 3 | 1184 | 2400 | 1088 (ciphertext) | 29 000 / 45 000 op/s |
| ML-KEM (FIPS 203) | ML-KEM-1024 | 5 | 1568 | 3168 | 1568 (ciphertext) | 20 000 / 30 000 op/s |
| ML-DSA (FIPS 204) | ML-DSA-44 | 2 | 1312 | 2560 | 2420 (firma) | Firma 4.8, verificación 0.5 |
| ML-DSA (FIPS 204) | ML-DSA-65 | 3 | 1952 | 4032 | 3309 (firma) | Sin dato en la fuente |
| ML-DSA (FIPS 204) | ML-DSA-87 | 5 | 2592 | 4896 | 4627 (firma) | Sin dato en la fuente |
| SLH-DSA (FIPS 205) | SLH-DSA-128s | 1 | 32 | 64 | 7856 (firma) | Firma 8000, verificación 2.8 |
| SLH-DSA (FIPS 205) | SLH-DSA-128f | 1 | 32 | 64 | 17 088 (firma) | Firma 550, verificación 7 |

Los tamaños salen de la Tabla 3 de FIPS 203, la Tabla 2 de FIPS 204 y la Tabla 2 de FIPS 205 (NIST, 2024a, 2024b, 2024c). En SLH-DSA la clave privada mide cuatro veces el parámetro n, que es 16 bytes en los conjuntos de categoría 1. La velocidad viene de las mediciones de Cloudflare, que el propio autor presenta solo como una indicación aproximada (Westerbaan, 2024). Para ML-KEM se dan las operaciones por segundo del cliente y del servidor, frente a 19 000 de X25519, y para las firmas se da el tiempo de CPU relativo a Ed25519, que vale 1 y es comparable con ECDSA P-256, así que un número mayor significa más lento.

ML-KEM, derivado de CRYSTALS-Kyber, es un mecanismo de encapsulamiento de claves basado en el problema Module Learning With Errors (MLWE). Sus tres niveles cambian sobre todo en tamaño, ya que la clave pública pasa de 800 bytes en ML-KEM-512 a 1568 bytes en ML-KEM-1024 y el ciphertext de 768 a 1568 bytes. Aun en el nivel más alto sigue siendo más rápido que X25519 en las mediciones de Cloudflare. ML-KEM reemplaza a ECDH, X25519 y al transporte de claves con RSA.

ML-DSA, derivado de CRYSTALS-Dilithium, es un esquema de firma digital que también se basa en MLWE. La firma crece de 2420 bytes en ML-DSA-44 a 4627 bytes en ML-DSA-87, mientras que una firma ECDSA P-256 medida con OpenSSL ocupó entre 69 y 72 bytes. En velocidad, la verificación de ML-DSA-44 tardó la mitad que la de Ed25519 y la firma unas 4.8 veces más, de modo que el costo del cambio está más en los bytes que en el procesador. ML-DSA reemplaza a ECDSA y a las firmas RSA.

SLH-DSA, derivado de SPHINCS+, es un esquema de firma que solo depende de la seguridad de funciones hash. Por eso se considera más conservador que ML-DSA, ya que no supone que un problema de retículos como MLWE sea difícil, y un avance en el criptoanálisis de retículos no lo afectaría. A cambio, sus firmas son mucho más grandes (7856 bytes en la variante pequeña) y firmar con SLH-DSA-128s es unas 8000 veces más lento que con Ed25519. Por eso se recomienda como respaldo para firmas de larga vida o de bajo volumen, como certificados raíz o firmware, y no como firma principal en sistemas que firman miles de documentos al día.

## 3. Plan de migración para tres perfiles organizacionales

El plan sigue las tres etapas que propone ETSI TR 103 619, que son armar el inventario, preparar el plan y ejecutar la migración (ETSI, 2020), y las recomendaciones de CISA, NSA y NIST de crear una hoja de ruta, levantar un inventario criptográfico y pedir a los proveedores sus planes de PQC (CISA, 2023). La urgencia de cada perfil depende de cuántos años deben seguir protegidos sus datos, porque si ese horizonte es mayor que el tiempo que falta para que exista un computador cuántico capaz de romper la criptografía actual, lo que se capture hoy quedará expuesto después.

### Perfil A — Hospital universitario

1. **Inventario.** El portal de pacientes con TLS (intercambio X25519 o ECDHE y certificados ECDSA o RSA), la firma de prescripciones con ECDSA, el intercambio de historias clínicas con otras entidades, las VPN con sedes y aseguradoras y la PKI interna que emite los certificados.
2. **Clasificación de datos.** La historia clínica tiene una sensibilidad de 50 a 75 años y es el dato más crítico, porque un adversario puede guardarla cifrada hoy y descifrarla en 10 a 15 años cuando todavía sea sensible. Las prescripciones firmadas necesitan sobre todo autenticidad al momento de emitirse, y los datos administrativos tienen un horizonte mucho menor.
3. **Estrategia híbrida.** El portal y los enlaces que transportan historias clínicas pasan primero a X25519MLKEM768, que protege la confidencialidad contra la captura actual sin perder la seguridad clásica. Las firmas de prescripciones se emiten con ML-DSA en paralelo a ECDSA mientras todos los sistemas que las verifican se actualizan.
4. **Cronograma.**

| Fase | Periodo | Hito verificable |
|---|---|---|
| Inventario | Primer semestre de 2027 | Lista aprobada de sistemas, algoritmos y proveedores con criptografía asimétrica |
| TLS híbrido | Segundo semestre de 2027 | Todas las conexiones del portal y de intercambio de historias negocian X25519MLKEM768 |
| Firmas en paralelo | 2028 | Cada prescripción lleva firma ML-DSA y ECDSA, y los verificadores aceptan ambas |
| Retiro de lo clásico | 2029 a 2030 | Se desactiva ECDSA y RSA, y los certificados raíz de larga vida pasan a SLH-DSA |

5. **Riesgos y mitigaciones.** Los equipos médicos antiguos que no se pueden actualizar se aíslan en una red separada detrás de un proxy que sí use TLS híbrido. Si el proveedor de la historia clínica electrónica no tiene soporte PQC, se exige en el contrato una fecha de entrega. El aumento de tamaño de los certificados se prueba antes con los navegadores y dispositivos que usan los pacientes.

**Priorización.** Este perfil va primero porque la amenaza de capturar ahora y descifrar después ya está activa, y la confidencialidad de la historia clínica no se puede recuperar una vez filtrada.

### Perfil B — Startup de comercio electrónico

1. **Inventario.** TLS 1.3 de la tienda y de la API con X25519 y certificados ECDSA, la integración con la pasarela de pagos, los tokens firmados de sesión y la base de datos cifrada con AES-256.
2. **Clasificación de datos.** Los datos de tarjetas tienen una sensibilidad de 5 a 7 años, que corresponde al ciclo de vida de la tarjeta, y los datos de sesión duran mucho menos. El cifrado en reposo con AES-256 ya es suficiente frente a Grover.
3. **Estrategia híbrida.** Se activa X25519MLKEM768 en el servidor o en la CDN, ya que los navegadores principales lo soportan, y se mantienen los certificados ECDSA hasta que las autoridades de certificación ofrezcan certificados ML-DSA.
4. **Cronograma.**

| Fase | Periodo | Hito verificable |
|---|---|---|
| Inventario y TLS híbrido | 2027 | X25519MLKEM768 activo y medido el porcentaje de conexiones que lo negocian |
| Agilidad criptográfica | 2028 | Librerías actualizadas y algoritmos configurables sin cambiar código, validado con el auditor de PCI-DSS |
| Firmas post-cuánticas | 2030 a 2031 | Certificados ML-DSA en producción y evaluación de pasar a PQC puro |

5. **Riesgos y mitigaciones.** Algunos clientes o equipos intermedios fallan cuando el handshake crece (Westerbaan, 2024), por lo que se deja X25519 como respaldo y se monitorean los errores de conexión. Además, cualquier cambio en el flujo de pago se coordina con el cumplimiento de PCI-DSS.

**Priorización.** Este perfil tiene menor urgencia porque sus datos dejan de ser sensibles en pocos años, pero el TLS híbrido cuesta poco y se puede activar desde ya como ventaja frente a la competencia.

### Perfil C — Entidad gubernamental de defensa

1. **Inventario.** Comunicaciones clasificadas, la PKI nacional que firma documentos oficiales, las VPN entre agencias y la firma de firmware y software de los equipos.
2. **Clasificación de datos.** La información clasificada tiene una sensibilidad de 25 a 50 años, por lo que todo el tráfico actual está expuesto a ser capturado y descifrado más adelante.
3. **Estrategia híbrida.** CNSA 2.0 exige ML-KEM-1024, ML-DSA-87, AES-256 y SHA-384 o SHA-512, además de LMS o XMSS para firmar firmware. La NSA no exige soluciones híbridas y solo acepta las que ella misma haya aprobado para protocolos específicos, así que el híbrido se usa solo donde la interoperabilidad lo obligue (NSA, 2026).
4. **Cronograma.** Este perfil sigue las fechas obligatorias de CNSA 2.0 (NSA, 2026).

| Fase | Fecha | Hito verificable |
|---|---|---|
| Adquisiciones | 1 de enero de 2027 | Toda compra nueva para sistemas de seguridad nacional soporta CNSA 2.0 |
| Retiro de equipos | 31 de diciembre de 2030 | Se retira el equipo que no soporte CNSA 2.0, salvo excepción aprobada |
| Uso obligatorio | 31 de diciembre de 2031 | Todos los sistemas usan los algoritmos de CNSA 2.0 |
| Meta nacional | 2035 | Todos los sistemas de seguridad nacional son resistentes a ataques cuánticos |

5. **Riesgos y mitigaciones.** Parte del hardware no se podrá actualizar y habrá que renovarlo, por lo que se presupuesta desde la fase de adquisiciones. La interoperabilidad entre agencias se resuelve acordando perfiles comunes, y como no se sabría si un adversario ya tiene un computador cuántico, no se espera a ver señales de amenaza para migrar.

**Priorización.** Este perfil comparte la prioridad máxima con el hospital, pero además la migración es obligatoria y tiene fechas fijas, lo que lo vuelve el más estricto de los tres.

## 4. Tamaños de clave y firma frente a la criptografía clásica e impacto en TLS 1.3 híbrido

Los tamaños post-cuánticos son los oficiales de los documentos FIPS. Los clásicos se midieron generando claves y firmas con OpenSSL 3.2.1, tomando las claves RSA en formato DER y repitiendo 20 firmas ECDSA, ya que su tamaño en DER cambia un poco en cada firma.

| Algoritmo | Tipo | Clave pública (bytes) | Clave privada (bytes) | Firma o ciphertext (bytes) | Nivel de seguridad | Fuente |
|---|---|---|---|---|---|---|
| RSA-3072 | Cifrado y firma clásicos | 422 (DER) | 1768 (DER) | 384 (firma) | Clásico de 128 bits, no post-cuántico | Medición con OpenSSL |
| ECDSA P-256 | Firma clásica | 64 (punto x, y) | 32 | 69 a 72 (firma DER) | Clásico de 128 bits, no post-cuántico | Medición con OpenSSL |
| X25519 | Intercambio de clave clásico | 32 | 32 | No aplica | Clásico de 128 bits, no post-cuántico | Medición con OpenSSL |
| ML-KEM-768 | KEM post-cuántico | 1184 | 2400 | 1088 (ciphertext) | Categoría 3 | FIPS 203, Tabla 3 (NIST, 2024a) |
| ML-DSA-65 | Firma post-cuántica | 1952 | 4032 | 3309 (firma) | Categoría 3 | FIPS 204, Tabla 2 (NIST, 2024b) |
| SLH-DSA-128s | Firma post-cuántica basada en hash | 32 | 64 | 7856 (firma) | Categoría 1 | FIPS 205, Tabla 2 (NIST, 2024c) |

La diferencia de escala es grande. La clave pública de ML-KEM-768 es 37 veces la de X25519 (1184 frente a 32 bytes), y la firma de ML-DSA-65 es entre 46 y 48 veces una firma ECDSA P-256, según si esta ocupa 72 o 69 bytes. SLH-DSA-128s es el caso opuesto, porque su clave pública mide lo mismo que la de X25519 pero su firma es más del doble que la de ML-DSA-65.

En TLS 1.3 el grupo híbrido X25519MLKEM768 envía en el key_share del cliente la clave de encapsulamiento de ML-KEM-768 seguida de la clave X25519, en total 1216 bytes (1184 + 32), y el servidor responde con el ciphertext de ML-KEM seguido de su clave X25519, en total 1120 bytes (1088 + 32) (Kwiatkowski et al., 2026). Frente a X25519 solo, el mensaje del cliente crece 1184 bytes y el del servidor 1088 bytes, así que entre los dos el intercambio pasa de 64 a 2336 bytes.

Ese crecimiento normalmente no agrega rondas de red. Cloudflare observó que el salto de latencia aparece cuando los datos superan la ventana de congestión inicial de TCP, alrededor de 10 kB con una ventana típica, porque ahí se necesita una ronda extra (Westerbaan, 2024). Los 2.3 kB del intercambio híbrido quedan muy por debajo de ese límite, y por eso Chrome y Cloudflare pudieron activarlo sin un costo notable.

El problema aparece al cambiar también las firmas. Según la misma fuente, en una primera visita a un sitio se envían seis firmas y dos claves públicas entre la cadena de certificados y el handshake. Si todas fueran ECDSA P-256 y se reemplazaran por ML-DSA-65, se sumarían unos 23 kB (6 × (3309 − 71) + 2 × (1952 − 64) = 23 204 bytes), lo que supera los 10 kB de una ventana típica. En redes con alta latencia o pérdida de paquetes eso significa al menos una ronda extra, y Cloudflare midió que cruzar ese límite puede hacer la conexión más de un 60% más lenta (Westerbaan, 2024). Además, encontró clientes y equipos intermedios que fallan cuando la cadena de certificados crece más de 10 kB o 30 kB, de modo que la migración de las firmas necesita más pruebas que la del intercambio de claves.

## 5. Decisión Técnica — Algoritmo NIST para firmar las prescripciones del Perfil A
ML-KEM queda descartado de entrada porque es un mecanismo de encapsulamiento de claves y no un esquema de firma. Solo sirve para acordar una clave secreta y no produce una firma que demuestre quién emitió la prescripción.

Para un volumen alto de prescripciones con baja latencia conviene ML-DSA-65. Su firma ocupa 3309 bytes frente a 7856 de SLH-DSA-128s, y en las mediciones de Cloudflare firmar con SLH-DSA-128s costó unas 8000 veces el tiempo de Ed25519, mientras que ML-DSA-44, el único nivel de ML-DSA que mide esa fuente, tardó 4.8 veces y verificó en la mitad del tiempo (Westerbaan, 2024).

Sí se justifica usar ML-DSA como algoritmo principal. La amenaza de capturar ahora y descifrar después afecta la confidencialidad de los datos cifrados, no la autenticidad de una firma, que se comprueba cuando la prescripción se emite y se dispensa. Por eso el horizonte de 50 a 75 años no obliga a usar aquí el esquema más conservador. SLH-DSA se reserva como respaldo para los certificados raíz y de larga vida, donde su seguridad basada solo en funciones hash pesa más que el rendimiento, y así el hospital gana diversidad criptográfica.

## 6. Decisión Técnica — Modo híbrido en TLS para el Perfil B
Lo que justifica adoptar el modo híbrido desde ahora es que cuesta muy poco. El key_share pasa de 64 a 2336 bytes sumando cliente y servidor, muy por debajo de los cerca de 10 kB donde aparece una ronda extra, así que el cliente no lo nota. Además, Chrome y Cloudflare ya lo usan en producción (Westerbaan, 2024).

La doble protección vale mucho mientras ML-KEM y ML-DSA siguen siendo jóvenes. Una conexión híbrida solo queda expuesta si se rompen los dos componentes a la vez, el clásico por un computador cuántico y el post-cuántico por alguna debilidad todavía no descubierta, y los algoritmos PQC llevan muchos menos años de análisis público que las curvas elípticas.

El modo híbrido no debería ser permanente. Es la transición correcta por ahora, pero la NSA advierte que agrega complejidad a los protocolos y obliga a una segunda transición cuando se abandonen los algoritmos clásicos (NSA, 2026). Por eso conviene planear el paso a PQC puro cuando ML-KEM y ML-DSA acumulen confianza, con 2031 como referencia, que es cuando CNSA 2.0 exige sus algoritmos. Como sus datos duran de 5 a 7 años y ninguna norma lo obliga, el Perfil B puede hacerlo después del Perfil C y con menos urgencia.

## 7. Conclusiones

La computación cuántica no afecta por igual a toda la criptografía. RSA, ECDSA y ECDH quedan rotos por el algoritmo de Shor y deben reemplazarse, mientras que AES y las funciones hash solo necesitan claves o salidas más largas para resistir a Grover.

Los estándares del NIST ya permiten hacer ese reemplazo, y su costo principal está en el tamaño y no en la velocidad. En el intercambio de claves el crecimiento es pequeño y el modo híbrido se puede activar sin rondas extra, en cambio las firmas post-cuánticas son decenas de veces más grandes y su migración exige más pruebas.

Por último, la prioridad de cada organización depende de cuánto tiempo deben seguir protegidos sus datos. El hospital y la entidad de defensa deben empezar ya por la amenaza de capturar ahora y descifrar después, y la startup puede avanzar con calma aprovechando que el TLS híbrido es barato.

## Referencias

CISA, NSA y NIST. (2023). *Quantum-readiness: Migration to post-quantum cryptography*. Cybersecurity and Infrastructure Security Agency. https://www.cisa.gov/resources-tools/resources/quantum-readiness-migration-post-quantum-cryptography

ETSI. (2017). *Quantum-Safe Cryptography (QSC); Limits to quantum computing applied to symmetric key sizes* (ETSI GR QSC 006 V1.1.1). European Telecommunications Standards Institute.

ETSI. (2020). *CYBER; Migration strategies and recommendations to Quantum Safe schemes* (ETSI TR 103 619 V1.1.1). European Telecommunications Standards Institute.

Gidney, C., y Ekerå, M. (2021). How to factor 2048 bit RSA integers in 8 hours using 20 million noisy qubits. *Quantum, 5*, 433. https://doi.org/10.22331/q-2021-04-15-433

Kwiatkowski, K., Kampanakis, P., Westerbaan, B. E., y Stebila, D. (2026). *Post-quantum traditional (PQ/T) hybrid key agreement mechanisms for TLS 1.3* (RFC 10024). Internet Engineering Task Force. https://www.rfc-editor.org/rfc/rfc10024.html

National Institute of Standards and Technology. (2024a). *Module-lattice-based key-encapsulation mechanism standard* (FIPS 203). https://doi.org/10.6028/NIST.FIPS.203

National Institute of Standards and Technology. (2024b). *Module-lattice-based digital signature standard* (FIPS 204). https://doi.org/10.6028/NIST.FIPS.204

National Institute of Standards and Technology. (2024c). *Stateless hash-based digital signature standard* (FIPS 205). https://doi.org/10.6028/NIST.FIPS.205

National Security Agency. (2026). *Commercial National Security Algorithm Suite 2.0 and quantum computing frequently asked questions* (versión 2.2). National Security Agency.

Westerbaan, B. (2024, 5 de marzo). *The state of the post-quantum Internet*. The Cloudflare Blog. https://blog.cloudflare.com/pq-2024/
