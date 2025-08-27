import numpy as np
import matplotlib.pyplot as plt
from pathlib import Path
import math
import argparse

def read_frames_plain(path, L=None):
    path = Path(path)
    frames = []
    L_guess = 0.0

    with path.open("r", encoding="utf-8") as f:
        lines = f.readlines()

    data_lines = lines
    
    current_frame_xs, current_frame_ys, current_frame_ths = [], [], []
    
    for line in data_lines:
        line = line.strip()
        if not line:
            continue
            
        # Si la línea empieza con 't', es un nuevo frame
        if line.startswith('t') :
            # Guardar el frame anterior si existe
            if current_frame_xs:
                frames.append({
                    "x": np.array(current_frame_xs, dtype=float),
                    "y": np.array(current_frame_ys, dtype=float),
                    "theta": np.array(current_frame_ths, dtype=float),
                })
                current_frame_xs, current_frame_ys, current_frame_ths = [], [], []
            continue
            
        # Procesar línea de partícula: x y vx vy (partícula id)
        parts = line.split()
        if len(parts) < 4:
            continue
            
        try:
            # Normalizar decimal: coma -> punto
            x_str = parts[0].replace(",", ".")
            y_str = parts[1].replace(",", ".")
            vx_str = parts[2].replace(",", ".")
            vy_str = parts[3].replace(",", ".")
            
            x = float(x_str)
            y = float(y_str)
            vx = float(vx_str)
            vy = float(vy_str)
            
            # Calcular theta a partir de vx y vy
            theta = np.arctan2(vy, vx)
            
            current_frame_xs.append(x)
            current_frame_ys.append(y)
            current_frame_ths.append(theta)
            
            L_guess = max(L_guess, x, y)
            
        except ValueError:
            continue
    
    # Guardar el último frame
    if current_frame_xs:
        frames.append({
            "x": np.array(current_frame_xs, dtype=float),
            "y": np.array(current_frame_ys, dtype=float),
            "theta": np.array(current_frame_ths, dtype=float),
        })

   
    all_theta = np.concatenate([fr["theta"] for fr in frames]) if frames else np.array([])
    if all_theta.size > 0:
        # Check if angles are in degrees (if max > pi, they might be in degrees)
        if np.nanmax(np.abs(all_theta)) > np.pi:
            print(f"Convirtiendo ángulos de grados a radianes (rango observado: {np.nanmin(all_theta):.1f} a {np.nanmax(all_theta):.1f})")
            for fr in frames:
                fr["theta"] = np.deg2rad(fr["theta"])

        # Normalize all angles to [-pi, pi] range
        for fr in frames:
            th = fr["theta"]
            # Normalize to [-pi, pi] range
            th = np.arctan2(np.sin(th), np.cos(th))
            fr["theta"] = th

    if L is None:
        L = float(math.ceil(L_guess + 1))
        print(f"L no especificado. Estimado automáticamente: L = {L}")
    else:
        print(f"Usando L especificado: L = {L}")
    
    return frames, L

def polarization_series(frames):
    va = []
    for fr in frames:
        sum_cos = sum_sin = 0.0
        for i in range(fr["theta"].size):
            sum_cos += np.cos(fr["theta"][i])
            sum_sin += np.sin(fr["theta"][i])
        va.append(np.sqrt(sum_cos**2 + sum_sin**2) / fr["theta"].size)
    return np.array(va, dtype=float)

def calculate_polarization_stats(filename, start_frame=250, L=None):
    """Calcula la polarización promedio y desvío estándar desde t=start_frame"""
    try:
        frames, L = read_frames_plain(filename, L)
        if len(frames) <= start_frame:
            print(f"Advertencia: {filename} tiene solo {len(frames)} frames, pero se requiere desde t={start_frame}")
            return None, None
        
        # Calcular polarización para todos los frames
        va = polarization_series(frames)
        
        # Tomar solo desde t=start_frame
        va_from_start = va[start_frame:]
        
        # Calcular promedio y desvío estándar
        mean_polarization = np.mean(va_from_start)
        std_polarization = np.std(va_from_start)
        
        print(f"{filename}: Polarización promedio = {mean_polarization:.4f}, Desvío = {std_polarization:.4f}")
        
        return mean_polarization, std_polarization
        
    except Exception as e:
        print(f"Error procesando {filename}: {e}")
        return None, None

def main():
    parser = argparse.ArgumentParser(description="Cálculo de polarización promedio vs ruido")
    parser.add_argument("--L", "-l", type=float, default=None, help="Tamaño de la grilla L. Si no se especifica se estima automáticamente")
    args = parser.parse_args()

    # Archivos a procesar y sus correspondientes ruidos
    files_and_noise = [
        ("Ruido0.txt", 0),
        ("Ruido0-5.txt", 0.5),
        ("Ruido1.txt", 1),
        ("Ruido1-5.txt", 1.5),
        ("Ruido2.txt", 2),
        ("Ruido2-5.txt", 2.5),
        ("Ruido3.txt", 3),
        ("Ruido3-5.txt", 3.5),
        ("Ruido4.txt", 4),
        ("Ruido4-5.txt", 4.5),
        ("Ruido5.txt", 5)
    ]
    
    noise_values = []
    mean_polarizations = []
    std_polarizations = []
    
    # Procesar cada archivo
    for filename, noise in files_and_noise:
        mean_pol, std_pol = calculate_polarization_stats(filename, start_frame=250, L=args.L)
        
        if mean_pol is not None and std_pol is not None:
            noise_values.append(noise)
            mean_polarizations.append(mean_pol)
            std_polarizations.append(std_pol)
    
    # Crear el gráfico
    plt.figure(figsize=(10, 6))
    
    # Graficar puntos con barras de error
    plt.errorbar(noise_values, mean_polarizations, yerr=std_polarizations, 
                fmt='o-', capsize=5, capthick=2, linewidth=2, markersize=8)
    
    # Configurar el gráfico
    plt.xlabel('Ruido (rad)')
    plt.ylabel('Polarización promedio')
    plt.grid(True, alpha=0.3)
    plt.xlim(-0.2, 5.2)
    plt.ylim(0, 1.1)
    
    # Añadir etiquetas de valores en los puntos
    for i, (noise, mean_pol, std_pol) in enumerate(zip(noise_values, mean_polarizations, std_polarizations)):
        plt.annotate(f'{mean_pol:.3f}', 
                    xy=(noise, mean_pol), 
                    xytext=(0, 10), 
                    textcoords='offset points',
                    ha='center', 
                    fontsize=9)
    
    plt.tight_layout()
    plt.show()
    
    # Imprimir resumen
    print("\nResumen de resultados:")
    print("Ruido | Polarización promedio | Desvío estándar")
    print("-" * 45)
    for noise, mean_pol, std_pol in zip(noise_values, mean_polarizations, std_polarizations):
        print(f"{noise:5.0f} | {mean_pol:19.4f} | {std_pol:16.4f}")

if __name__ == "__main__":
    main()
