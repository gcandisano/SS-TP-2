package ar.edu.itba.ss;

import java.io.File;

public class Main {
    public static final String txtFile = "output.txt";

    public static void main(String[] args) {
        Config cfg = parseArgs(args);

        Vicsek vicsekModel = new Vicsek(cfg.L, cfg.N, cfg.v, cfg.r, cfg.eta, cfg.deltaT, cfg.useVoterModel);
        int totalSteps = 2000; // Total number of simulation steps
        File outputFile = new File(cfg.outputName);

        try (java.io.PrintWriter writer = new java.io.PrintWriter(outputFile)) {
            for (int step = 0; step < totalSteps; step++) {
                vicsekModel.updateParticles();
                writer.printf("t%d%n", step + 1);
                for (Particle p : vicsekModel.particles) {
                    double vx = cfg.v * Math.cos(p.theta);
                    double vy = cfg.v * Math.sin(p.theta);
                    writer.printf("%.6f %.6f %.6f %.6f %n", p.x, p.y, vx, vy);
                }
            }
        } catch (Exception e) {
            e.printStackTrace();
        }
    }

    private static class Config {
        int L = 10; // Size of the square domain (default)
        int N = 300; // Number of particles (default)
        double v = 0.03; // Speed of particles (default)
        double r = 1.0; // Interaction radius (default)
        double eta = 3; // Noise factor (default)
        double deltaT = 1; // Time step (default)
        String outputName = txtFile; // Output file name (default)
        boolean useVoterModel = false; // Use voter model by default (can be enabled via -voter)
    }

    private static Config parseArgs(String[] args) {
        Config cfg = new Config();
        // Supported flags:
        // -L <int> -N <int> -V <double> -eta <double> -txtFile <name> -voter <bool>
        for (int i = 0; i < args.length; i++) {
            String arg = args[i];
            if (!arg.startsWith("-")) {
                continue;
            }
            String key = arg.replaceFirst("^-+", "").toLowerCase();
            String value = null;
            if (i + 1 < args.length && !args[i + 1].startsWith("-")) {
                value = args[++i];
            }

            try {
                switch (key) {
                    case "l":
                        if (value != null) cfg.L = Integer.parseInt(value);
                        break;
                    case "n":
                        if (value != null) cfg.N = Integer.parseInt(value);
                        break;
                    case "v":
                        if (value != null) cfg.v = Double.parseDouble(value);
                        break;
                    case "eta":
                    case "noise":
                        if (value != null) cfg.eta = Double.parseDouble(value);
                        break;
                    case "txtfile":
                    case "out":
                    case "output":
                    case "o":
                    case "txt":
                        if (value != null) cfg.outputName = value;
                        break;
                    case "voter":
                    case "vm":
                        // If provided without value (switch), enable voter model
                        if (value == null) {
                            cfg.useVoterModel = true;
                        } else {
                            cfg.useVoterModel = parseBoolean(value, cfg.useVoterModel);
                        }
                        break;
                    default:
                        // Unknown flag, ignore
                        break;
                }
            } catch (Exception ignored) {
                // Ignore parse errors and keep defaults
            }
        }
        return cfg;
    }

    private static boolean parseBoolean(String s, boolean defaultValue) {
        if (s == null) return defaultValue;
        String v = s.toLowerCase();
        if (v.equals("true") || v.equals("t") || v.equals("yes") || v.equals("y") || v.equals("1")) return true;
        if (v.equals("false") || v.equals("f") || v.equals("no") || v.equals("n") || v.equals("0")) return false;
        return defaultValue;
    }
}
