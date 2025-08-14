package ar.edu.itba.ss;

public class Particle {
    long x;
    long y;
    long theta;

    int id;

    public Particle(long x, long y, long theta, int id) {
        this.x = x;
        this.y = y;
        this.theta = theta;
        this.id = id;
    }
    public void setTheta(long theta) {
        this.theta = theta;
    }

    public void setX(long x) {
        this.x = x;
    }

    public void setY(long y) {
        this.y = y;
    }
}
