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


def main():
    parser = argparse.ArgumentParser(description="Graficar v_a(t) para 6 archivos output*.txt")
    parser.add_argument("--L", "-l", type=float, default=None, help="Tamaño de la grilla L. Si no se especifica se estima automáticamente")
    parser.add_argument("--files", nargs='*', default=[
        "Ruido0.txt",
        "Ruido1.txt",
        "Ruido2.txt",
        "Ruido3.txt",
        "Ruido4.txt",
        "Ruido5.txt",
    ], help="Lista de archivos a graficar (por defecto los 6 output*.txt)")
    args = parser.parse_args()

    plt.figure(figsize=(10, 6))
    colors = [f"C{i}" for i in range(10)]

    for i, file in enumerate(args.files):
        try:
            frames, _ = read_frames_plain(file, args.L)
            if not frames:
                print(f"Advertencia: {file} no contiene frames válidos")
                continue
            va = polarization_series(frames)
            t = np.arange(va.size)
            label = Path(file).name
            plt.plot(t, va, label=label, color=colors[i % len(colors)], linewidth=1.5)
        except Exception as e:
            print(f"Error procesando {file}: {e}")
            continue

    plt.xlabel('t (frames)')
    plt.ylabel('v_a')
    plt.ylim(0, 1)
    plt.grid(True, alpha=0.3)
    plt.legend()
    plt.tight_layout()
    plt.show()


if __name__ == "__main__":
    main()


