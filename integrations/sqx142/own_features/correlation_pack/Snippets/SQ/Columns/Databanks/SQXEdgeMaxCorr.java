package SQ.Columns.Databanks;

import com.strategyquant.lib.L;
import com.strategyquant.lib.SettingsMap;
import com.strategyquant.tradinglib.*;

public class SQXEdgeMaxCorr extends DatabankColumn {

    public SQXEdgeMaxCorr() {
        super(L.tsq("SQX Edge Max Corr"), DatabankColumn.Decimal2, ValueTypes.Minimize, 0, -1, 1);
        setWidth(100);
        setTooltip("SQX Edge max observed correlation to a selected portfolio winner.");
    }

    @Override
    public String getValue(ResultsGroup results, String resultKey, byte direction, byte plType, byte sampleType) {
        return read(results, "SQXEdgeMaxCorr", "-1");
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
