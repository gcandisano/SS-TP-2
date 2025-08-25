package ar.edu.itba.ss;

import java.util.List;
import java.util.ArrayList;

public class VoterInteraction {
    private final int L;
    private final int N;
    private final double v;
    private final double r;
    private final double eta;
    private final double deltaT;
    Particle[] particles;

    public VoterInteraction(int L, int N, double v, double r, double eta, double deltaT) {
        this.L = L;
        this.N = N;
        this.v = v;
        this.r = r;
        this.eta = eta;
        this.deltaT = deltaT;
        this.particles = new Particle[N];
        initializeParticles();
    }

    private void initializeParticles() {
        for (int i = 0; i < N; i++) {
            double x = Math.random() * L;
            double y = Math.random() * L;
            double theta = (Math.random() * 2 * Math.PI) - Math.PI; // [-pi, pi]
            // Normalize to ensure it's in the correct range
            while (theta < -Math.PI) theta += 2 * Math.PI;
            while (theta >= Math.PI) theta -= 2 * Math.PI;
            particles[i] = new Particle(x, y, theta, i + 1);
        }
    }

    public void updateParticles() {
        Particle[] newParticles = new Particle[N];
        for (int i = 0; i < N; i++) {
            newParticles[i] = new Particle(particles[i].x, particles[i].y, particles[i].theta, particles[i].id);
        }
        for (int i = 0; i < N; i++) {
            double randomNeighborTheta = getRandomNeighborTheta(i);
            double noise = (Math.random() - 0.5) * eta;
            double newTheta = randomNeighborTheta + noise;
            while (newTheta < -Math.PI) newTheta += 2 * Math.PI;
            while (newTheta >= Math.PI) newTheta -= 2 * Math.PI;
            newParticles[i].setTheta(newTheta);
            newParticles[i].setX(particles[i].x + v * Math.cos(particles[i].theta) * deltaT);
            newParticles[i].setY(particles[i].y + v * Math.sin(particles[i].theta) * deltaT);
            newParticles[i].setX(((newParticles[i].x % L) + L) % L);
            newParticles[i].setY(((newParticles[i].y % L) + L) % L);
        }
        particles = newParticles;
    }

    private double getRandomNeighborTheta(int index) {
        List<Double> neighborThetas = new ArrayList<>();
        Particle p = particles[index];
        for (Particle other : particles) {
            if (distance(p, other) <= r) {
                neighborThetas.add(other.theta);
            }
        }
        if (neighborThetas.isEmpty()) {
            return p.theta;
        }
        int pick = (int) Math.floor(Math.random() * neighborThetas.size());
        return neighborThetas.get(pick);
    }

    private double distance(Particle p1, Particle p2) {
        double dx = Math.min(Math.abs(p1.x - p2.x), L - Math.abs(p1.x - p2.x));
        double dy = Math.min(Math.abs(p1.y - p2.y), L - Math.abs(p1.y - p2.y));
        return Math.sqrt(dx * dx + dy * dy);
    }
}