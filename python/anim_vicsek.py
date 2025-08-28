# anim_from_plain_txt.py
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
import math
from pathlib import Path
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

def animate_quiver_from_frames(frames, L, color_by_angle=True, skip=1, interval_ms=40, sub=1, save_mp4=None, arrow_scale=None, arrow_width=0.004):
    assert frames, "No hay frames para animar"

    def take_sub(fr):
        if sub <= 1: 
            return fr
        mask = np.arange(fr["x"].size) % sub == 0
        return {k: v[mask] for k, v in fr.items()}

    fr0 = take_sub(frames[0])
    x, y, th = fr0["x"], fr0["y"], fr0["theta"]
    u, v = np.cos(th), np.sin(th)

    fig, ax = plt.subplots(figsize=(10,10))
    ax.set_xlim(0, L); ax.set_ylim(0, L); ax.set_aspect("equal", adjustable="box")
    ax.set_title(f"Modelo Vicsek - t=0 (N={len(x)})", fontsize=14)
    ax.set_xlabel("x", fontsize=12); ax.set_ylabel("y", fontsize=12)
    ax.grid(True, alpha=0.3)

    vector_scale = arrow_scale if arrow_scale is not None else 5.0
    
    if color_by_angle:
        c = (th + np.pi) / (2*np.pi)  # Normalizar a [0,1]
        Q = ax.quiver(x, y, u, v, c, cmap="hsv", angles="xy", scale_units="xy", 
                     scale=vector_scale, width=arrow_width, alpha=0.9)
        cb = fig.colorbar(Q, ax=ax, fraction=0.046, pad=0.04)
        cb.set_label("Ángulo (0=π, 0.5=0, 1=π)", fontsize=10)
        # Puntos coloreados por ángulo, sin radio (pixel)
        scatter = ax.scatter(x, y, c=c, cmap="hsv", s=1, marker=",", linewidths=0, alpha=1.0, zorder=5)
        scatter.set_clim(0.0, 1.0)
    else:
        Q = ax.quiver(x, y, u, v, angles="xy", scale_units="xy", 
                     scale=vector_scale, width=arrow_width, color="blue", alpha=0.9)
        # Puntos rojos si no se colorea por ángulo, sin radio (pixel)
        scatter = ax.scatter(x, y, c='red', s=1, marker=",", linewidths=0, alpha=1.0, zorder=5)

    # iterador de frames
    def frame_iter():
        for t, fr in enumerate(frames):
            if t % skip != 0: 
                continue
            yield t, take_sub(fr)

    it = frame_iter()

    def update(_):
        try:
            t, fr = next(it)
        except StopIteration:
            return Q, scatter
        x, y, th = fr["x"], fr["y"], fr["theta"]
        u, v = np.cos(th), np.sin(th)
        if color_by_angle:
            c = (th + np.pi) / (2*np.pi)  # Normalizar a [0,1]
            Q.set_UVC(u, v, c)
        else:
            Q.set_UVC(u, v)
        Q.set_offsets(np.column_stack((x, y)))
        scatter.set_offsets(np.column_stack((x, y)))  # Actualizar posiciones de los puntos
        if color_by_angle:
            scatter.set_array(c)  # Actualizar color por ángulo
        ax.set_title(f"Modelo Vicsek - t={t} (N={len(x)})", fontsize=14)
        return Q, scatter

    frame_list = list(frame_iter())  # Convert generator to list to count frames
    it = iter(frame_list)            # Reset iterator

    anim = FuncAnimation(
        fig,
        update,
        frames=len(frame_list),      # Explicitly set number of frames
        interval=interval_ms,
        blit=False,
        cache_frame_data=False
    )

    if save_mp4:
        anim.save(save_mp4, writer="ffmpeg", dpi=150, fps=int(1000/max(1,interval_ms)))
    else:
        plt.show()

def polarization_series(frames):
    va = []
    for fr in frames:
        sum_cos = sum_sin = 0.0
        for i in range(fr["theta"].size):
            sum_cos += np.cos(fr["theta"][i])
            sum_sin += np.sin(fr["theta"][i])
        va.append(np.sqrt(sum_cos**2 + sum_sin**2) / fr["theta"].size)
    return np.array(va, dtype=float)

def plot_va(va):
    import matplotlib.pyplot as plt
    fig, ax = plt.subplots()
    ax.plot(va, lw=1.5)
    ax.set_xlabel("t (frames)")
    ax.set_ylabel("v_a")
    ax.set_title("Polarización v_a(t)")
    ax.set_ylim(0, 1)  # Eje y siempre de 0 a 1
    ax.grid(True)
    plt.show()

if __name__ == "__main__":
    # Configuración de argumentos de línea de comandos
    parser = argparse.ArgumentParser(description="Animador del modelo Vicsek")
    parser.add_argument("--path", "-p", default="output.txt", 
                       help="Ruta al archivo de datos (default: output.txt)")
    parser.add_argument("--L", "-l", type=float, default=None,
                       help="Tamaño de la grilla L (si no se especifica, se estima automáticamente)")


    parser.add_argument("--save", type=str, default=None,
                       help="Guardar animación como MP4 (ej: --save anim.mp4)")
    parser.add_argument("--no-color", action="store_true",
                       help="No colorear por ángulo (usar color azul uniforme)")
    
    args = parser.parse_args()

    frames, L = read_frames_plain(args.path, args.L)
    print(f"Frames leídos: {len(frames)}; Partículas por frame: {frames[0]['x'].size if frames else 0}; L={L}")

    # Animación: color por ángulo
    animate_quiver_from_frames(
        frames, L, 
        color_by_angle=not args.no_color, 
        skip=1, 
        interval_ms=40, 
        sub=1, 
        save_mp4=args.save,
    )

    # Serie v_a(t)
    va = polarization_series(frames)
    plot_va(va)
