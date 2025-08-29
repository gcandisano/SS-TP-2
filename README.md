# Simulación del Modelo Vicsek

Este proyecto implementa el modelo Vicsek para el estudio de sistemas de partículas autopropulsadas que exhiben comportamiento colectivo.

## Requisitos

### Para la simulación Java:
- Java JDK 8 o superior
- IntelliJ IDEA (recomendado) o cualquier IDE que soporte Java

### Para los scripts de Python:
- Python 3.7 o superior
- Dependencias de Python:
  ```bash
  pip install numpy matplotlib
  ```

## Compilación y Ejecución

### 1. Compilar el Proyecto Java

#### Opción A: Usando IntelliJ IDEA
1. Abrir el proyecto en IntelliJ IDEA
2. El proyecto debería compilar automáticamente
3. Si no, ir a `Build` → `Build Project`

#### Opción B: Usando línea de comandos
```bash
# Desde el directorio raíz del proyecto
javac -d out/production/SS-TP2 src/ar/edu/itba/ss/*.java
```

### 2. Ejecutar la Simulación

#### Ejecución Individual
```bash
java -cp out/production/SS-TP2 ar.edu.itba.ss.Main [opciones]
```

#### Parámetros Disponibles:
- `-L <int>`: Tamaño del dominio cuadrado (default: 10)
- `-N <int>`: Número de partículas (default: 300)
- `-V <double>`: Velocidad de las partículas (default: 0.03)
- `-eta <double>`: Factor de ruido (default: 3)
- `-o <filename>`: Nombre del archivo de salida (default: output.txt)
- `-voter`: Habilitar modelo de votación

#### Ejemplos de Ejecución:
```bash
# Simulación básica
java -cp out/production/SS-TP2 ar.edu.itba.ss.Main

# Simulación con parámetros personalizados
java -cp out/production/SS-TP2 ar.edu.itba.ss.Main -L 10 -N 100 -V 0.03 -eta 1 -o "mi_simulacion.txt"

# Simulación con modelo de votación
java -cp out/production/SS-TP2 ar.edu.itba.ss.Main -L 10 -N 300 -V 0.03 -eta 0 -o "voter_sim.txt" -voter
```



## Análisis y Visualización con Python

### 1. Animación de la Simulación (`anim_vicsek.py`)

Este script crea una animación de las partículas en movimiento.

#### Uso Básico:
```bash
cd python
python anim_vicsek.py --path "ruta/al/archivo.txt"
```

#### Opciones Disponibles:
- `--path` o `-p`: Ruta al archivo de datos (default: ultimo.txt)
- `--L` o `-l`: Tamaño de la grilla L (se estima automáticamente si no se especifica)

#### Ejemplos:
```bash
# Animación básica
python anim_vicsek.py --path "../ultimo.txt"

# Animación con parámetros personalizados
python anim_vicsek.py --path "../Densidad 5 -.txt" --L 10 --save "animacion.mp4"

# Animación sin colorear por ángulo
python anim_vicsek.py --path "../ultimo.txt" --no-color
```

### 2. Análisis de Polarización Promedio (`average_polarization.py`)

Este script calcula la polarización promedio vs densidad para múltiples archivos.

#### Uso:
```bash
cd python
python average_polarization.py
```

#### Funcionalidades:
- Procesa automáticamente archivos con nombres específicos (Densidad X -.txt)
- Calcula polarización promedio desde el frame 400
- Genera gráfico con barras de error
- Muestra tabla de resultados

#### Personalización:
```bash
# Especificar tamaño de grilla
python average_polarization.py --L 10
```

### 3. Gráficos de Series Temporales (`plot_polarization_series.py`)

Este script grafica la evolución temporal de la polarización.

#### Uso Básico:
```bash
cd python
python plot_polarization_series.py
```

#### Opciones:
- `--L` o `-l`: Tamaño de la grilla L
- `--files`: Lista de archivos a graficar

#### Ejemplos:
```bash
# Gráfico con archivos específicos
python plot_polarization_series.py --files "Densidad 0,1 -.txt" "Densidad 5 -.txt"

# Con tamaño de grilla específico
python plot_polarization_series.py --L 10
```

## Formato de Datos

Los archivos de salida de la simulación Java tienen el siguiente formato:

```
t1
x1 y1 vx1 vy1
x2 y2 vx2 vy2
...
t2
x1 y1 vx1 vy1
x2 y2 vx2 vy2
...
```

Donde:
- `tN`: Indica el inicio del frame N
- `x y vx vy`: Posición (x,y) y velocidad (vx,vy) de cada partícula

## Flujo de Trabajo Típico

1. **Ejecutar simulación Java:**
   ```bash
   java -cp out/production/SS-TP2 ar.edu.itba.ss.Main -L 10 -N 300 -V 0.03 -eta 3 -o "simulacion.txt"
   ```

2. **Crear animación:**
   ```bash
   cd python
   python anim_vicsek.py --path "../simulacion.txt" --save "animacion.mp4"
   ```

3. **Analizar polarización:**
   ```bash
   python plot_polarization_series.py --files "../simulacion.txt"
   ```

## Notas Importantes

- Los archivos de salida usan coma como separador decimal (formato europeo)
- Los scripts de Python manejan automáticamente la conversión de formato
- La simulación ejecuta 2000 pasos por defecto
- Los ángulos se normalizan automáticamente al rango [-π, π]

## Solución de Problemas

### Error de Compilación Java:
- Verificar que Java JDK esté instalado: `java -version`
- Asegurar que el classpath esté correcto
- Verificar que todos los archivos .java estén en el directorio correcto

### Error en Scripts Python:
- Instalar dependencias: `pip install numpy matplotlib`
- Verificar que Python 3.7+ esté instalado: `python --version`
- Asegurar que los archivos de datos existan y tengan el formato correcto

