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
            long x = (long) (Math.random() * L);
            long y = (long) (Math.random() * L);
            long theta = (long) (Math.random() * 360);
            particles[i] = new Particle(x, y, theta, i + 1);
        }
    }

    public void updateParticles() {
        for (int i = 0; i < N; i++) {
            double avgTheta = calculateAverageTheta(i);
            double noise = (Math.random() - 0.5) * eta;
            double newTheta = avgTheta + noise;
            particles[i].setTheta((long) (newTheta % 360));

            long newX = (long) ((particles[i].x + v * Math.cos(Math.toRadians(newTheta)) * deltaT) % L);
            long newY = (long) ((particles[i].y + v * Math.sin(Math.toRadians(newTheta)) * deltaT) % L);
            particles[i].setX((newX + L) % L);
            particles[i].setY((newY + L) % L);
        }
    }

    private double calculateAverageTheta(int index) {
        Particle p = particles[index];
        double sumSin = 0;
        double sumCos = 0;
        for (Particle other : particles) {
            if (distance(p, other) <= r) {
                sumSin += Math.sin(Math.toRadians(other.theta));
                sumCos += Math.cos(Math.toRadians(other.theta));
            }
        }
        return Math.toDegrees(Math.atan2(sumSin, sumCos));
    }

    private double distance(Particle p1, Particle p2) {
        double dx = Math.min(Math.abs(p1.x - p2.x), L - Math.abs(p1.x - p2.x));
        double dy = Math.min(Math.abs(p1.y - p2.y), L - Math.abs(p1.y - p2.y));
        return Math.sqrt(dx * dx + dy * dy);
    }
}
