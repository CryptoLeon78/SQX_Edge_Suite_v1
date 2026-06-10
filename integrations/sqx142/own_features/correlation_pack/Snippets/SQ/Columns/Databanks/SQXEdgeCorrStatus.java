package SQ.Columns.Databanks;

import com.strategyquant.lib.L;
import com.strategyquant.lib.SettingsMap;
import com.strategyquant.tradinglib.*;

public class SQXEdgeCorrStatus extends DatabankColumn {

    public SQXEdgeCorrStatus() {
        super(L.tsq("SQX Edge Corr Status"), DatabankColumn.Integer, ValueTypes.Maximize, 0, -1, 2);
        setWidth(120);
        setTooltip("SQX Edge correlation status: 2 available, 1 similarity-only, 0 not-comparable, -1 missing.");
    }

    @Override
    public String getValue(ResultsGroup results, String resultKey, byte direction, byte plType, byte sampleType) {
        return read(results, "SQXEdgeCorrStatusCode", "-1");
    }

    @Override
    public double compute(SQStats stats, StatsTypeCombination combination, OrdersList ordersList,
                          SettingsMap settings, SQStats statsLong, SQStats statsShort) throws Exception {
        return 0;
    }

    private String read(ResultsGroup results, String key, String fallback) {
        try {
            SettingsMap values = results.specialValues();
            return values != null && values.containsKey(key) ? values.getString(key, fallback) : fallback;
        } catch (Exception e) {
            return fallback;
        }
    }

    private double parse(String value, double fallback) {
        try { return Double.parseDouble(value); } catch (Exception e) { return fallback; }
    }
}
