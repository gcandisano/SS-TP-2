import numpy as np
import matplotlib.pyplot as plt
from pathlib import Path
import math

def read_frames_plain(path, L=10):
    path = Path(path)
    xs, ys, ths, ids = [], [], [], []
    frames = []
    L_guess = 0.0

    def flush_frame():
        nonlocal xs, ys, ths, frames
        if xs:
            frames.append({
                "x": np.array(xs, dtype=float),
                "y": np.array(ys, dtype=float),
                "theta": np.array(ths, dtype=float),
            })
            xs, ys, ths, = [], [], []

    last_id = None
    with path.open("r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue

            # 1) Intento por whitespace
            parts = line.split()
            # 2) Si no son 4, intento CSV
            if len(parts) != 4:
                parts = [p.strip() for p in line.split(",")]
            if len(parts) != 4:
                continue  # línea no válida

            i_str, x_str, y_str, th_str = parts

            # Normalización decimal: coma -> punto
            i_str  = i_str.replace(",", ".")
            x_str  = x_str.replace(",", ".")
            y_str  = y_str.replace(",", ".")
            th_str = th_str.replace(",", ".")

            try:
                i  = int(float(i_str))  # por si viene "1.0"
                x  = float(x_str)
                y  = float(y_str)
                th = float(th_str)
            except ValueError:
                continue

            # nuevo frame si el id "resetea"
            if last_id is not None and i <= last_id:
                flush_frame()
            last_id = i

            xs.append(x); ys.append(y); ths.append(th)
            L_guess = max(L_guess, x, y)

    flush_frame()

   
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

def calculate_polarization_stats(filename, start_frame=250):
    """Calcula la polarización promedio y desvío estándar desde t=start_frame"""
    try:
        frames, L = read_frames_plain(filename)
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
    # Archivos a procesar y sus correspondientes ruidos
    files_and_noise = [
        ("output.txt", 0),
        ("output2.txt", 1),
        ("output3.txt", 2),
        ("output4.txt", 3),
        ("output5.txt", 4),
        ("output6.txt", 5)
    ]
    
    noise_values = []
    mean_polarizations = []
    std_polarizations = []
    
    # Procesar cada archivo
    for filename, noise in files_and_noise:
        mean_pol, std_pol = calculate_polarization_stats(filename, start_frame=250)
        
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
    plt.title('Polarización promedio vs Ruido')
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
