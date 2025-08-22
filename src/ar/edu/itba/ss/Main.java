package ar.edu.itba.ss;

import java.io.File;

public class Main {
    public static final String txtFile = "output.txt";

    public static void main(String[] args) {
        int L = 10; // Size of the square domain
        int N = 300; // Number of particles
        double v = 0.3; // Speed of particles
        double r = 1.0; // Interaction radius
        double eta = 0.1; // Noise factor
        double deltaT = 1; // Time step

        Vicsek vicsekModel = new Vicsek(L, N, v, r, eta, deltaT);
        int totalSteps = 1000; // Total number of simulation steps
        File outputFile = new File(txtFile);

        try (java.io.PrintWriter writer = new java.io.PrintWriter(outputFile)) {
            writer.printf("id x y theta%n");
            for (int step = 0; step < totalSteps; step++) {
                vicsekModel.updateParticles();
                for (Particle p : vicsekModel.particles) {
                    writer.printf("%d %.6f %.6f %.6f%n", p.id, p.x, p.y, p.theta);
                }
                writer.println();
            }
        } catch (Exception e) {
            e.printStackTrace();
        }
    }
}
