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
