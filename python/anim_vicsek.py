# anim_from_plain_txt.py
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
import math
from pathlib import Path

def read_frames_plain(path):
    """
    Lee un archivo con líneas: id x y theta
    Sin header, sin 't,'. Agrupa frames cuando el id disminuye o vuelve a 1.
    Devuelve: frames (lista de dicts) con keys: x, y, theta (np.ndarray)
    También retorna L (lado) estimado a partir del máximo x/y observado.
    """
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

    # ARREGLADO: Manejo correcto de ángulos
    all_theta = np.concatenate([fr["theta"] for fr in frames]) if frames else np.array([])
    if all_theta.size > 0:
        # Si hay valores fuera de [-pi, pi], asumimos que están en grados
        if np.nanmax(np.abs(all_theta)) > np.pi:
            print(f"Convirtiendo ángulos de grados a radianes (rango observado: {np.nanmin(all_theta):.1f} a {np.nanmax(all_theta):.1f})")
            for fr in frames:
                fr["theta"] = np.deg2rad(fr["theta"])

        # ARREGLADO: Wrapping correcto a [-pi, pi]
        for fr in frames:
            th = fr["theta"]
            # Wrapping simple a [-pi, pi]
            th = np.arctan2(np.sin(th), np.cos(th))
            fr["theta"] = th

    # si L no es conocido, usamos el máximo observado (con un margen)
    L = float(math.ceil(L_guess + 1))
    return frames, L

def animate_quiver_from_frames(frames, L, color_by_angle=True, skip=1, interval_ms=40, sub=1, save_mp4=None):
    """
    frames: lista de dicts con x,y,theta
    L: lado de la caja (para ejes 0..L)
    color_by_angle: colorear por ángulo
    skip: tomar 1 de cada 'skip' frames para la animación
    sub: submuestreo de partículas (1 = todas, 2 = una de cada 2, etc.)
    """
    assert frames, "No hay frames para animar"

    # primer frame (submuestreado si hace falta)
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

    # ARREGLADO: Escala más grande para vectores más visibles
    vector_scale = min(L/15, 3.0)  # Escala más grande
    
    if color_by_angle:
        # ARREGLADO: Coloreado más claro y vectores más grandes
        c = (th + np.pi) / (2*np.pi)  # Normalizar a [0,1]
        Q = ax.quiver(x, y, u, v, c, cmap="hsv", angles="xy", scale_units="xy", 
                     scale=vector_scale, width=0.008, alpha=0.9)  # width aumentado
        cb = fig.colorbar(Q, ax=ax, fraction=0.046, pad=0.04)
        cb.set_label("Ángulo (0=π, 0.5=0, 1=π)", fontsize=10)
        # Puntos coloreados por ángulo, sin radio (pixel)
        scatter = ax.scatter(x, y, c=c, cmap="hsv", s=1, marker=",", linewidths=0, alpha=1.0, zorder=5)
        scatter.set_clim(0.0, 1.0)
    else:
        Q = ax.quiver(x, y, u, v, angles="xy", scale_units="xy", 
                     scale=vector_scale, width=0.008, color="blue", alpha=0.9)  # width aumentado
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

    anim = FuncAnimation(fig, update, interval=interval_ms, blit=False)

    if save_mp4:
        anim.save(save_mp4, writer="ffmpeg", dpi=150, fps=int(1000/max(1,interval_ms)))
    else:
        plt.show()

def polarization_series(frames):
    """
    v_a(t) = |sum_i (cosθ_i, sinθ_i)| / N
    Devuelve np.array de v_a por frame.
    """
    va = []
    for fr in frames:
        th = fr["theta"]
        sx = np.sum(np.cos(th))
        sy = np.sum(np.sin(th))
        va.append(np.hypot(sx, sy) / len(th))
    return np.array(va, dtype=float)

def plot_va(va):
    import matplotlib.pyplot as plt
    fig, ax = plt.subplots()
    ax.plot(va, lw=1.5)
    ax.set_xlabel("t (frames)")
    ax.set_ylabel("v_a")
    ax.set_title("Polarización v_a(t)")
    ax.grid(True)
    plt.show()

if __name__ == "__main__":
    # Cambiá esto por tu ruta real:
    path = "output.txt"

    frames, L = read_frames_plain(path)
    print(f"Frames leídos: {len(frames)}; Partículas por frame: {frames[0]['x'].size if frames else 0}; L≈{L}")

    # Animación: color por ángulo, saltando 1 de cada 1, submuestreo de partículas opcional
    animate_quiver_from_frames(frames, L, color_by_angle=True, skip=1, interval_ms=40, sub=1, save_mp4=None)

    # Serie v_a(t)
    va = polarization_series(frames)
    plot_va(va)
