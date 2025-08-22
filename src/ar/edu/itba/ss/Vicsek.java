package ar.edu.itba.ss;

public class Vicsek {
    private final int L;
    private final int N;
    private final double v;
    private final double r;
    private final double eta;
    private final double deltaT;
    Particle[] particles;

    public Vicsek(int L, int N, double v, double r, double eta, double deltaT) {
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
            particles[i] = new Particle(x, y, theta, i + 1);
        }
    }

    public void updateParticles() {
        Particle[] newParticles = new Particle[N];
        for (int i = 0; i < N; i++) {
            newParticles[i] = new Particle(particles[i].x, particles[i].y, particles[i].theta, particles[i].id);
        }

        for (int i = 0; i < N; i++) {
            double avgTheta = calculateAverageTheta(i);
            double noise = (Math.random() - 0.5) * eta;
            double newTheta = avgTheta + noise;
            newParticles[i].setTheta(newTheta);

            newParticles[i].setX(particles[i].x + v * Math.cos(particles[i].theta) * deltaT);
            newParticles[i].setY(particles[i].y + v * Math.sin(particles[i].theta) * deltaT);
            
            newParticles[i].setX(((newParticles[i].x % L) + L) % L);
            newParticles[i].setY(((newParticles[i].y % L) + L) % L);
        }
        particles = newParticles;
    }

    private double calculateAverageTheta(int index) {
        Particle p = particles[index];
        double sumSin = 0;
        double sumCos = 0;
        int n = 0;
        for (Particle other : particles) {
            if (distance(p, other) <= r) {
                sumSin += Math.sin(other.theta);
                sumCos += Math.cos(other.theta);
                n++;
            }
        }
        return Math.atan2(sumSin/n, sumCos/n); // [-pi, pi]
    }

    private double distance(Particle p1, Particle p2) {
        double dx = Math.min(Math.abs(p1.x - p2.x), L - Math.abs(p1.x - p2.x));
        double dy = Math.min(Math.abs(p1.y - p2.y), L - Math.abs(p1.y - p2.y));
        return Math.sqrt(dx * dx + dy * dy);
    }
}
