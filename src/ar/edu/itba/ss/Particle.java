package ar.edu.itba.ss;

public class Particle {
    double x;
    double y;
    double theta;

    int id;

    public Particle(double x, double y, double theta, int id) {
        this.x = x;
        this.y = y;
        this.theta = theta;
        this.id = id;
    }
    public void setTheta(double theta) {
        this.theta = theta;
    }

    public void setX(double x) {
        this.x = x;
    }

    public void setY(double y) {
        this.y = y;
    }
}
