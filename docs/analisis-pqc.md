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
