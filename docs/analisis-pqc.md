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
