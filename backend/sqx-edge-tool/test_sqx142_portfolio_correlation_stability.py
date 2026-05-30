from core.sqx142_portfolio_correlation_stability import (
    CAPA1_C2_CORRELATION_SELECTION_VERSION,
    PORTFOLIO_CORRELATION_STABILITY_VERSION,
    build_capa1_c2_correlation_selection_report,
    build_portfolio_correlation_stability_report,
    export_portfolio_correlation_stability_csv,
)


def test_portfolio_correlation_stability_selects_on_is_and_audits_oos3():
    candidates = "\n".join([
        "strategy,asset,timeframe,profitFactor,retDd,maxDd,trades,blockSetting",
        "AUDCAD_A,AUDCAD,H1,1.55,5.4,18,160,BS_Momentum_v6",
        "AUDCAD_B,AUDCAD,H1,1.48,4.9,20,150,BS_Momentum_v6",
        "AUDCAD_C,AUDCAD,H1,1.42,4.6,21,140,BS_Momentum_v6",
    ])
    is_series = "\n".join([
        "strategy,isReturnSeries",
        'AUDCAD_A,"0.01|-0.004|0.012|0.006|-0.003|0.009|0.004|-0.002|0.011|0.005|0.003|0.007"',
        'AUDCAD_B,"-0.003|0.008|-0.002|0.010|0.004|-0.001|0.006|0.003|-0.002|0.009|0.004|0.002"',
        'AUDCAD_C,"0.009|-0.003|0.011|0.005|-0.002|0.008|0.003|-0.001|0.010|0.004|0.002|0.006"',
    ])
    oos3_series = "\n".join([
        "strategy,oos3ReturnSeries",
        'AUDCAD_A,"0.006|0.004|-0.003|0.009|0.002|-0.001|0.008|0.004|-0.002|0.007|0.003|0.005"',
        'AUDCAD_B,"0.006|0.004|-0.003|0.009|0.002|-0.001|0.008|0.004|-0.002|0.007|0.003|0.005"',
        'AUDCAD_C,"0.006|0.004|-0.002|0.008|0.002|-0.001|0.007|0.004|-0.002|0.006|0.003|0.005"',
    ])
    report = build_portfolio_correlation_stability_report({
        "csv": candidates,
        "isSeriesCsv": is_series,
        "oos3SeriesCsv": oos3_series,
        "settings": {
            "maxIsCorrelation": 0.50,
            "maxOos3Correlation": 0.60,
            "minComparablePoints": 12,
        },
    })

    assert report["version"] == PORTFOLIO_CORRELATION_STABILITY_VERSION
    assert report["methodology"]["selectionBasis"] == "IS_CORR only"
    assert report["methodology"]["oos3MaySelectAlternates"] is False
    assert report["summary"]["selectedByIs"] >= 2
    assert report["summary"]["selectedPairs"] >= 1
    assert report["summary"]["oos3CorrelationBreaks"] >= 1
    assert report["summary"]["status"] == "blocked_oos3_correlation_break"
    assert report["summary"]["nearestOos3Comparable"] >= 1
    assert any(item["nearestOos3AuditFlags"] for item in report["items"])
    assert report["privacy"]["raw_strategy_names_returned"] is False

    csv_export = export_portfolio_correlation_stability_csv(report)
    assert "isCorrelation" in csv_export
    assert "oos3Correlation" in csv_export


def test_capa1_c2_correlation_selection_uses_template_labels():
    report = build_capa1_c2_correlation_selection_report({
        "rows": [
            {"strategy": "A", "asset": "AUDCAD", "timeframe": "H1", "profitFactor": 1.4, "retDd": 4.0, "trades": 100, "isReturnSeries": "0.01|0.02|-0.01|0.03", "oos3ReturnSeries": "0.01|0.00|0.02|-0.01"},
            {"strategy": "B", "asset": "AUDCAD", "timeframe": "H1", "profitFactor": 1.3, "retDd": 3.0, "trades": 90, "isReturnSeries": "-0.01|0.01|0.00|0.02", "oos3ReturnSeries": "0.00|0.01|-0.01|0.02"},
        ],
        "settings": {"minComparablePoints": 3},
    })

    assert report["version"] == CAPA1_C2_CORRELATION_SELECTION_VERSION
    assert report["legacyVersion"] == PORTFOLIO_CORRELATION_STABILITY_VERSION
    assert report["decisionDomain"] == "capa1_c2_template_selection"
    assert report["decisionLabels"]["selected"] == "c2_template_winner"
    assert report["summary"]["c2TemplateSelectedByIs"] == report["summary"]["selectedByIs"]
