import numpy as np
import matplotlib.pyplot as plt
from pathlib import Path
import math
import argparse
import sys
import os

# Import functions from average_polarization.py
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from average_polarization import read_frames_plain, polarization_series, calculate_polarization_stats

def main():
    parser = argparse.ArgumentParser(description="Comparación de polarización entre diferentes cantidades de partículas")
    parser.add_argument("--L", "-l", type=float, default=None, help="Tamaño de la grilla L. Si no se especifica se estima automáticamente")
    parser.add_argument("--start-frame", type=int, default=250, help="Frame inicial para el cálculo (default: 250)")
    args = parser.parse_args()

    # Archivos a procesar organizados por cantidad de partículas y Noise
    files_by_particles = {
        40: [
            ("../40Noise0.txt", 0, 3.1),
            ("../40Noise0.5.txt", 0.5, 3.1),
            ("../40Noise1.txt", 1, 3.1),
            ("../40Noise1.5.txt", 1.5, 3.1),
            ("../40Noise2.txt", 2, 3.1),
            ("../40Noise2.5.txt", 2.5, 3.1),
            ("../40Noise3.txt", 3, 3.1),
            ("../40Noise3.5.txt", 3.5, 3.1),
            ("../40Noise4.txt", 4, 3.1),
            ("../40Noise4.5.txt", 4.5, 3.1),
            ("../40Noise5.txt", 5, 3.1)
        ],
        100: [
            ("../100Noise0.txt", 0, 5),
            ("../100Noise0.5.txt", 0.5, 5),
            ("../100Noise1.txt", 1, 5),
            ("../100Noise1.5.txt", 1.5, 5),
            ("../100Noise2.txt", 2, 5),
            ("../100Noise2.5.txt", 2.5, 5),
            ("../100Noise3.txt", 3, 5),
            ("../100Noise3.5.txt", 3.5, 5),
            ("../100Noise4.txt", 4, 5),
            ("../100Noise4.5.txt", 4.5, 5),
            ("../100Noise5.txt", 5, 5)
        ],
        400: [
            ("../400Noise0.txt", 0, 10),
            ("../400Noise0.5.txt", 0.5, 10),
            ("../400Noise1.txt", 1, 10),
            ("../400Noise1.5.txt", 1.5, 10),
            ("../400Noise2.txt", 2, 10),
            ("../400Noise2.5.txt", 2.5, 10),
            ("../400Noise3.txt", 3, 10),
            ("../400Noise3.5.txt", 3.5, 10),
            ("../400Noise4.txt", 4, 10),
            ("../400Noise4.5.txt", 4.5, 10),
            ("../400Noise5.txt", 5, 10)
        ]
    }
    
    # Colores para cada cantidad de partículas
    colors = {40: 'blue', 100: 'red', 400: 'green'}
    markers = {40: 'o', 100: 's', 400: '^'}
    
    plt.figure(figsize=(12, 8))
    
    # Procesar cada cantidad de partículas
    for particle_count, files_list in files_by_particles.items():
        noise_values = []
        mean_polarizations = []
        std_polarizations = []
        
        print(f"\nProcesando archivos con {particle_count} partículas:")
        print("-" * 50)
        
        # Procesar cada archivo para esta cantidad de partículas
        for filename, noise, value in files_list:
            # Verificar si el archivo existe
            if not os.path.exists(filename):
                print(f"Archivo no encontrado: {filename}")
                continue
                
            mean_pol, std_pol = calculate_polarization_stats(filename, start_frame=args.start_frame, L=value)
            
            if mean_pol is not None and std_pol is not None:
                noise_values.append(noise)
                mean_polarizations.append(mean_pol)
                std_polarizations.append(std_pol)
        
        if noise_values:  # Solo graficar si hay datos válidos
            # Graficar puntos con barras de error
            plt.errorbar(noise_values, mean_polarizations, yerr=std_polarizations, 
                        fmt=f'{markers[particle_count]}-', 
                        color=colors[particle_count],
                        capsize=5, capthick=2, linewidth=2, markersize=8,
                        label=f'{particle_count} partículas')
            
            # Añadir etiquetas de valores en los puntos
            for i, (noise, mean_pol, std_pol) in enumerate(zip(noise_values, mean_polarizations, std_polarizations)):
                plt.annotate(f'{mean_pol:.3f}', 
                            xy=(noise, mean_pol), 
                            xytext=(0, 10), 
                            textcoords='offset points',
                            ha='center', 
                            fontsize=8,
                            color=colors[particle_count])
    
    # Configurar el gráfico
    plt.xlabel('Ruido (rad)', fontsize=12)
    plt.ylabel('Polarización promedio', fontsize=12)
    plt.title('Comparación de Polarización vs Noise para Diferentes Cantidades de Partículas', fontsize=14)
    plt.grid(True, alpha=0.3)
    plt.xlim(-0.2, 5.2)
    plt.ylim(0, 1.1)
    plt.legend(fontsize=11)
    
    plt.tight_layout()
    plt.show()
    
    # Imprimir resumen comparativo
    print("\n" + "="*60)
    print("RESUMEN COMPARATIVO")
    print("="*60)
    
    for particle_count, files_list in files_by_particles.items():
        print(f"\n{particle_count} PARTÍCULAS:")
        print("-" * 30)
        print("Ruido | Polarización promedio | Desvío estándar")
        print("-" * 45)
        
        for filename, noise, value in files_list:
            if os.path.exists(filename):
                mean_pol, std_pol = calculate_polarization_stats(filename, start_frame=args.start_frame, L=value)
                if mean_pol is not None and std_pol is not None:
                    print(f"{noise:5.1f} | {mean_pol:19.4f} | {std_pol:16.4f}")

if __name__ == "__main__":
    main()
