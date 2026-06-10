package SQ.CustomAnalysis;

import com.strategyquant.lib.*;
import com.strategyquant.tradinglib.*;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

import java.io.BufferedReader;
import java.nio.charset.StandardCharsets;
import java.nio.file.Files;
import java.nio.file.Path;
import java.nio.file.Paths;
import java.security.MessageDigest;
import java.util.HashMap;
import java.util.Map;

@ClassConfig(name = "SQX Edge Correlation Tagger", display = "SQX Edge Correlation Tagger")
@Help("Loads SQX Edge correlation decisions into specialValues. Lab-only visual tagger; it never rejects strategies.")
public class SQXEdgeCorrelationTagger extends CustomAnalysisMethod {

    public static final Logger Log = LoggerFactory.getLogger(SQXEdgeCorrelationTagger.class);

    private static final String VERSION = "sqx142-own-features1-correlation-pack-v1";
    private static final String ENV_CSV = "SQX_EDGE_CORRELATION_TAG_CSV";
    private static final String KEY_DECISION = "SQXEdgeCorrDecision";
    private static final String KEY_DECISION_TEXT = "SQXEdgeCorrDecisionText";
    private static final String KEY_RANK = "SQXEdgeCorrRank";
    private static final String KEY_SCORE = "SQXEdgeCorrScore";
    private static final String KEY_MAX_CORR = "SQXEdgeMaxCorr";
    private static final String KEY_STATUS = "SQXEdgeCorrStatus";
    private static final String KEY_STATUS_CODE = "SQXEdgeCorrStatusCode";
    private static final String KEY_NEAREST = "SQXEdgeNearestWinner";
    private static final String KEY_VERSION = "SQXEdgeCorrVersion";

    private static String cachedPath = "";
    private static long cachedMtime = -1L;
    private static Map<String, Map<String, String>> cachedRows = new HashMap<String, Map<String, String>>();

    public SQXEdgeCorrelationTagger() {
        super("SQXEdgeCorrelationTagger", TYPE_FILTER_STRATEGY);
    }

    @Override
    public boolean filterStrategy(String project, String task, String databankName, ResultsGroup rg) throws Exception {
        try {
            applyTag(rg);
        } catch (Exception e) {
            Log.warn("SQXEdgeCorrelationTagger failed open: {}", e.getMessage());
            safeSet(rg, KEY_DECISION, "-1");
            safeSet(rg, KEY_DECISION_TEXT, "missing");
            safeSet(rg, KEY_STATUS_CODE, "-1");
        }
        return true;
    }

    private void applyTag(ResultsGroup rg) throws Exception {
        String name = safeName(rg);
        String strategyRef = strategyRef(name);
        Map<String, String> row = loadRows().get(strategyRef);
        if (row == null) {
            safeSet(rg, KEY_DECISION, "-1");
            safeSet(rg, KEY_DECISION_TEXT, "missing");
            safeSet(rg, KEY_RANK, "-1");
            safeSet(rg, KEY_SCORE, "0");
            safeSet(rg, KEY_MAX_CORR, "-1");
            safeSet(rg, KEY_STATUS, "missing");
            safeSet(rg, KEY_STATUS_CODE, "-1");
            safeSet(rg, KEY_NEAREST, "");
            safeSet(rg, KEY_VERSION, VERSION);
            return;
        }
        String decision = value(row, "decision");
        String status = value(row, "correlationStatus");
        safeSet(rg, KEY_DECISION, String.valueOf(decisionCode(decision)));
        safeSet(rg, KEY_DECISION_TEXT, decision);
        safeSet(rg, KEY_RANK, valueOr(row, "portfolioRank", "-1"));
        safeSet(rg, KEY_SCORE, valueOr(row, "score", "0"));
        safeSet(rg, KEY_MAX_CORR, valueOr(row, "maxObservedCorrelation", "-1"));
        safeSet(rg, KEY_STATUS, status);
        safeSet(rg, KEY_STATUS_CODE, String.valueOf(statusCode(status)));
        safeSet(rg, KEY_NEAREST, value(row, "nearestWinnerId"));
        safeSet(rg, KEY_VERSION, valueOr(row, "version", VERSION));
    }

    private static Map<String, Map<String, String>> loadRows() throws Exception {
        Path csv = csvPath();
        String absolute = csv.toAbsolutePath().normalize().toString();
        long mtime = Files.exists(csv) ? Files.getLastModifiedTime(csv).toMillis() : -1L;
        if (absolute.equals(cachedPath) && mtime == cachedMtime) {
            return cachedRows;
        }
        Map<String, Map<String, String>> rows = new HashMap<String, Map<String, String>>();
        if (Files.exists(csv)) {
            BufferedReader reader = Files.newBufferedReader(csv, StandardCharsets.UTF_8);
            try {
                String headerLine = reader.readLine();
                if (headerLine != null) {
                    String[] headers = parseCsvLine(headerLine);
                    String line;
                    while ((line = reader.readLine()) != null) {
                        if (line.trim().length() == 0) continue;
                        String[] values = parseCsvLine(line);
                        Map<String, String> row = new HashMap<String, String>();
                        for (int i = 0; i < headers.length; i++) {
                            row.put(headers[i], i < values.length ? values[i] : "");
                        }
                        String ref = value(row, "strategyRef");
                        if (ref.length() > 0) rows.put(ref, row);
                    }
                }
            } finally {
                reader.close();
            }
        }
        cachedPath = absolute;
        cachedMtime = mtime;
        cachedRows = rows;
        return rows;
    }

    private static Path csvPath() {
        String env = System.getenv(ENV_CSV);
        if (env != null && env.trim().length() > 0) {
            return Paths.get(env.trim());
        }
        return Paths.get(System.getProperty("user.dir"), "user", "extend", "SQXEdge", "Correlation", "correlation_decisions.csv");
    }

    private static String strategyRef(String name) throws Exception {
        MessageDigest digest = MessageDigest.getInstance("SHA-256");
        byte[] bytes = digest.digest(name.getBytes(StandardCharsets.UTF_8));
        StringBuilder hex = new StringBuilder();
        for (int i = 0; i < bytes.length && hex.length() < 16; i++) {
            String part = Integer.toHexString(bytes[i] & 0xff);
            if (part.length() == 1) hex.append('0');
            hex.append(part);
        }
        return "strategy_" + hex.substring(0, 16);
    }

    private static String[] parseCsvLine(String line) {
        java.util.List<String> values = new java.util.ArrayList<String>();
        StringBuilder current = new StringBuilder();
        boolean quoted = false;
        for (int i = 0; i < line.length(); i++) {
            char ch = line.charAt(i);
            if (ch == '"') {
                if (quoted && i + 1 < line.length() && line.charAt(i + 1) == '"') {
                    current.append('"');
                    i++;
                } else {
                    quoted = !quoted;
                }
            } else if (ch == ',' && !quoted) {
                values.add(current.toString());
                current.setLength(0);
            } else {
                current.append(ch);
            }
        }
        values.add(current.toString());
        return values.toArray(new String[values.size()]);
    }

    private static String safeName(ResultsGroup rg) {
        try {
            return rg != null && rg.getName() != null ? rg.getName() : "unknown";
        } catch (Exception e) {
            return "unknown";
        }
    }

    private static void safeSet(ResultsGroup rg, String key, String value) {
        try {
            if (rg != null && rg.specialValues() != null) {
                rg.specialValues().setString(key, value == null ? "" : value);
            }
        } catch (Exception ignored) {
        }
    }

    private static String value(Map<String, String> row, String key) {
        String value = row.get(key);
        return value == null ? "" : value.trim();
    }

    private static String valueOr(Map<String, String> row, String key, String fallback) {
        String value = value(row, key);
        return value.length() == 0 ? fallback : value;
    }

    private static int decisionCode(String value) {
        if ("portfolio".equalsIgnoreCase(value)) return 1;
        if ("similar".equalsIgnoreCase(value)) return 0;
        if ("review".equalsIgnoreCase(value)) return -1;
        return -1;
    }

    private static int statusCode(String value) {
        if ("available".equalsIgnoreCase(value)) return 2;
        if ("similarity_only".equalsIgnoreCase(value)) return 1;
        if ("not_comparable".equalsIgnoreCase(value)) return 0;
        return -1;
    }
}
