package SQ.Columns.Databanks;

import com.strategyquant.lib.L;
import com.strategyquant.lib.SettingsMap;
import com.strategyquant.tradinglib.*;

public class SQXEdgeNearestWinner extends DatabankColumn {

    public SQXEdgeNearestWinner() {
        super(L.tsq("SQX Edge Nearest Winner"), DatabankColumn.Integer, ValueTypes.Maximize, 0, 0, 1);
        setWidth(150);
        setTooltip("SQX Edge nearest winner candidate id. Empty means no nearest winner.");
    }

    @Override
    public String getValue(ResultsGroup results, String resultKey, byte direction, byte plType, byte sampleType) {
        return read(results, "SQXEdgeNearestWinner", "");
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
}
