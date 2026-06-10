// SQXInfoBridge.mq5
// Version: sqx144-mt5-auto1-data-manager-bridge-v1
//
// Local MT5 bridge for SQX Edge Suite.
// Reads MQL5/Files/SQXInfoBridge.request.ini and writes JSON responses under MQL5/Files.
// It does not trade, place orders, import data into SQX, or write SQX files.
// Contract markers: "p50" "p75" "p90" "p95" "p99" "writesSqxHost":false "writesDataDb":false "writesUserProjects":false "mutatesDatabanks":false "runsSqxTasks":false "placesOrders":false "usesMigrationTool":false

#property strict
#property version   "1.000"
#property description "SQX Edge Suite MT5 instrument metadata bridge"

input string InpRequestFile = "SQXInfoBridge.request.ini";
input string InpLatestResponseFile = "SQXInfoBridge.latest.json";
input int InpPollSeconds = 2;
input ENUM_TIMEFRAMES InpDefaultSpreadTimeframe = PERIOD_M1;
input int InpFallbackStartYear = 2000;
input int InpMaxBars = 0; // 0 means all available bars returned by MT5.

string BRIDGE_VERSION = "sqx144-mt5-auto1-data-manager-bridge-v1";
string last_request_id = "";

struct SpreadStats
{
   int year;
   long samples;
   double min_value;
   double max_value;
   double mean;
   double p50;
   double p75;
   double p90;
   double p95;
   double p99;
};

int OnInit()
{
   EventSetTimer(MathMax(1, InpPollSeconds));
   Print("SQXInfoBridge initialized: ", BRIDGE_VERSION);
   return INIT_SUCCEEDED;
}

void OnDeinit(const int reason)
{
   EventKillTimer();
}

void OnTimer()
{
   ProcessRequest();
}

void ProcessRequest()
{
   string request_text = ReadTextFile(InpRequestFile);
   if(StringLen(request_text) == 0)
      return;

   string request_id = Trim(GetIniValue(request_text, "requestId", ""));
   string symbol = Trim(GetIniValue(request_text, "symbol", ""));
   string timeframe_text = Trim(GetIniValue(request_text, "spreadTimeframe", ""));
   int from_year = (int)StringToInteger(GetIniValue(request_text, "fromYear", "0"));
   int to_year = (int)StringToInteger(GetIniValue(request_text, "toYear", "0"));
   int max_bars = (int)StringToInteger(GetIniValue(request_text, "maxBars", IntegerToString(InpMaxBars)));

   if(request_id == "" || symbol == "")
      return;
   if(request_id == last_request_id)
      return;

   last_request_id = request_id;

   ENUM_TIMEFRAMES timeframe = ParseTimeframe(timeframe_text, InpDefaultSpreadTimeframe);
   string response = BuildResponseJson(request_id, symbol, timeframe, from_year, to_year, max_bars);
   string response_file = "SQXInfoBridge.response." + SafeFileToken(request_id) + ".json";
   WriteTextFile(response_file, response);
   WriteTextFile(InpLatestResponseFile, response);
   Print("SQXInfoBridge wrote response for ", symbol, " request ", request_id);
}

string BuildResponseJson(string request_id, string requested_symbol, ENUM_TIMEFRAMES timeframe, int from_year, int to_year, int max_bars)
{
   ResetLastError();
   string symbol = ResolveMt5Symbol(requested_symbol);
   bool selected = SymbolSelect(symbol, true);
   if(!selected)
      return ErrorJson(request_id, requested_symbol, symbol, "symbol_select_failed", GetLastError());

   double point = SymbolInfoDouble(symbol, SYMBOL_POINT);
   int digits = (int)SymbolInfoInteger(symbol, SYMBOL_DIGITS);
   double pip_size = PipSize(point, digits);
   double tick_size_raw = SymbolInfoDouble(symbol, SYMBOL_TRADE_TICK_SIZE);
   double tick_value = SymbolInfoDouble(symbol, SYMBOL_TRADE_TICK_VALUE);
   double contract_size = SymbolInfoDouble(symbol, SYMBOL_TRADE_CONTRACT_SIZE);
   double bid = SymbolInfoDouble(symbol, SYMBOL_BID);
   double ask = SymbolInfoDouble(symbol, SYMBOL_ASK);
   double point_value = ComputePointValue(symbol, tick_value, tick_size_raw, contract_size, bid);
   int spread_points_current = (int)SymbolInfoInteger(symbol, SYMBOL_SPREAD);
   double spread_current = PointsToPips(spread_points_current, point, pip_size);

   SpreadStats all_stats;
   SpreadStats yearly_stats[];
   string warnings = "";
   bool stats_ok = CollectSpreadStats(symbol, timeframe, point, pip_size, from_year, to_year, max_bars, all_stats, yearly_stats, warnings);

   string json = "{\n";
   json += "  \"version\":\"" + BRIDGE_VERSION + "\",\n";
   json += "  \"requestId\":\"" + JsonEscape(request_id) + "\",\n";
   json += "  \"status\":\"" + (stats_ok ? "ok" : "warning") + "\",\n";
   json += "  \"symbol\":\"" + JsonEscape(requested_symbol) + "\",\n";
   json += "  \"mt5Symbol\":\"" + JsonEscape(symbol) + "\",\n";
   json += "  \"serverTime\":\"" + JsonEscape(TimeToString(TimeCurrent(), TIME_DATE|TIME_SECONDS)) + "\",\n";
   json += "  \"spreadTimeframe\":\"" + JsonEscape(EnumToString(timeframe)) + "\",\n";
   json += "  \"properties\":{\n";
   json += "    \"digits\":" + IntegerToString(digits) + ",\n";
   json += "    \"point\":" + DoubleText(point, 10) + ",\n";
   json += "    \"pipSize\":" + DoubleText(pip_size, 10) + ",\n";
   json += "    \"tickSizeRaw\":" + DoubleText(tick_size_raw, 10) + ",\n";
   json += "    \"tickSizeForSqx\":" + DoubleText(pip_size, 10) + ",\n";
   json += "    \"tickStepForSqx\":" + DoubleText(point, 10) + ",\n";
   json += "    \"tickValue\":" + DoubleText(tick_value, 10) + ",\n";
   json += "    \"contractSize\":" + DoubleText(contract_size, 4) + ",\n";
   json += "    \"bid\":" + DoubleText(bid, 10) + ",\n";
   json += "    \"ask\":" + DoubleText(ask, 10) + ",\n";
   json += "    \"pointValue\":" + DoubleText(point_value, 6) + ",\n";
   json += "    \"spreadCurrent\":" + DoubleText(spread_current, 6) + "\n";
   json += "  },\n";
   json += "  \"spreadStats\":" + StatsJson(all_stats) + ",\n";
   json += "  \"yearlySpreadStats\":[\n";
   for(int i = 0; i < ArraySize(yearly_stats); i++)
   {
      json += "    " + StatsJson(yearly_stats[i]);
      if(i + 1 < ArraySize(yearly_stats))
         json += ",";
      json += "\n";
   }
   json += "  ],\n";
   json += "  \"warnings\":" + WarningArrayJson(warnings) + ",\n";
   json += "  \"privacy\":{\"localPathsReturned\":false,\"accountReturned\":false},\n";
   json += "  \"writesSqxHost\":false,\"writesDataDb\":false,\"writesUserProjects\":false,\"mutatesDatabanks\":false,\"runsSqxTasks\":false,\"placesOrders\":false,\"usesMigrationTool\":false\n";
   json += "}\n";
   return json;
}

bool CollectSpreadStats(
   string symbol,
   ENUM_TIMEFRAMES timeframe,
   double point,
   double pip_size,
   int from_year,
   int to_year,
   int max_bars,
   SpreadStats &all_stats,
   SpreadStats &yearly_stats[],
   string &warnings
)
{
   ArrayResize(yearly_stats, 0);
   double all_values[];
   ArrayResize(all_values, 0);

   datetime now = TimeCurrent();
   MqlDateTime now_dt;
   TimeToStruct(now, now_dt);
   int end_year = (to_year > 0 ? MathMin(to_year, now_dt.year) : now_dt.year);
   int start_year = from_year;
   if(start_year <= 0)
   {
      long first_date = 0;
      if(SeriesInfoInteger(symbol, timeframe, SERIES_FIRSTDATE, first_date) && first_date > 0)
      {
         MqlDateTime first_dt;
         TimeToStruct((datetime)first_date, first_dt);
         start_year = first_dt.year;
      }
      else
      {
         start_year = InpFallbackStartYear;
         AppendWarning(warnings, "series_firstdate_unavailable_used_fallback");
      }
   }
   if(start_year > end_year)
      start_year = end_year;

   int total_bars = 0;
   for(int year = start_year; year <= end_year; year++)
   {
      datetime from_time = YearStart(year);
      datetime to_time = YearStart(year + 1) - 1;
      if(to_time > now)
         to_time = now;

      MqlRates rates[];
      ResetLastError();
      int copied = CopyRates(symbol, timeframe, from_time, to_time, rates);
      if(copied <= 0)
      {
         AppendWarning(warnings, "copyrates_empty_" + IntegerToString(year));
         continue;
      }

      double year_values[];
      ArrayResize(year_values, 0, copied);
      for(int i = 0; i < copied; i++)
      {
         if(max_bars > 0 && total_bars >= max_bars)
            break;
         if(rates[i].spread < 0)
            continue;
         double spread_pips = PointsToPips((int)rates[i].spread, point, pip_size);
         if(spread_pips <= 0.0)
            continue;
         AppendDouble(year_values, spread_pips);
         AppendDouble(all_values, spread_pips);
         total_bars++;
      }

      if(ArraySize(year_values) > 0)
      {
         SpreadStats year_stats;
         ComputeStats(year_values, year, year_stats);
         AppendStats(yearly_stats, year_stats);
      }
      if(max_bars > 0 && total_bars >= max_bars)
      {
         AppendWarning(warnings, "max_bars_limit_reached");
         break;
      }
   }

   if(ArraySize(all_values) <= 0)
   {
      InitEmptyStats(all_stats, 0);
      AppendWarning(warnings, "spread_history_unavailable");
      return false;
   }
   ComputeStats(all_values, 0, all_stats);
   return true;
}

double PipSize(double point, int digits)
{
   if(digits == 3 || digits == 5)
      return point * 10.0;
   return point;
}

double PointsToPips(int spread_points, double point, double pip_size)
{
   if(pip_size <= 0.0)
      return 0.0;
   return ((double)spread_points * point) / pip_size;
}

double ComputePointValue(string symbol, double tick_value, double tick_size_raw, double contract_size, double bid)
{
   if(tick_value > 0.0 && tick_size_raw > 0.0)
      return tick_value / tick_size_raw;
   if(contract_size > 0.0 && bid > 0.0)
      return contract_size / bid;
   return 0.0;
}

void ComputeStats(double &values[], int year, SpreadStats &stats)
{
   int count = ArraySize(values);
   if(count <= 0)
   {
      InitEmptyStats(stats, year);
      return;
   }
   ArraySort(values);
   double sum = 0.0;
   for(int i = 0; i < count; i++)
      sum += values[i];
   stats.year = year;
   stats.samples = count;
   stats.min_value = values[0];
   stats.max_value = values[count - 1];
   stats.mean = sum / (double)count;
   stats.p50 = Percentile(values, 50.0);
   stats.p75 = Percentile(values, 75.0);
   stats.p90 = Percentile(values, 90.0);
   stats.p95 = Percentile(values, 95.0);
   stats.p99 = Percentile(values, 99.0);
}

void InitEmptyStats(SpreadStats &stats, int year)
{
   stats.year = year;
   stats.samples = 0;
   stats.min_value = 0.0;
   stats.max_value = 0.0;
   stats.mean = 0.0;
   stats.p50 = 0.0;
   stats.p75 = 0.0;
   stats.p90 = 0.0;
   stats.p95 = 0.0;
   stats.p99 = 0.0;
}

double Percentile(double &values[], double pct)
{
   int count = ArraySize(values);
   if(count <= 0)
      return 0.0;
   if(count == 1)
      return values[0];
   double pos = ((double)(count - 1)) * pct / 100.0;
   int lower = (int)MathFloor(pos);
   int upper = (int)MathCeil(pos);
   if(lower == upper)
      return values[lower];
   double weight = pos - (double)lower;
   return values[lower] * (1.0 - weight) + values[upper] * weight;
}

string StatsJson(SpreadStats &stats)
{
   string json = "{";
   json += "\"year\":" + IntegerToString(stats.year) + ",";
   json += "\"samples\":" + IntegerToString((int)stats.samples) + ",";
   json += "\"min\":" + DoubleText(stats.min_value, 6) + ",";
   json += "\"max\":" + DoubleText(stats.max_value, 6) + ",";
   json += "\"mean\":" + DoubleText(stats.mean, 6) + ",";
   json += "\"p50\":" + DoubleText(stats.p50, 6) + ",";
   json += "\"p75\":" + DoubleText(stats.p75, 6) + ",";
   json += "\"p90\":" + DoubleText(stats.p90, 6) + ",";
   json += "\"p95\":" + DoubleText(stats.p95, 6) + ",";
   json += "\"p99\":" + DoubleText(stats.p99, 6);
   json += "}";
   return json;
}

void AppendDouble(double &values[], double value)
{
   int size = ArraySize(values);
   ArrayResize(values, size + 1, size + 4096);
   values[size] = value;
}

void AppendStats(SpreadStats &values[], SpreadStats &value)
{
   int size = ArraySize(values);
   ArrayResize(values, size + 1, size + 16);
   values[size] = value;
}

void AppendWarning(string &warnings, string warning)
{
   if(warnings != "")
      warnings += "|";
   warnings += warning;
}

string WarningArrayJson(string warnings)
{
   if(warnings == "")
      return "[]";
   string parts[];
   int count = StringSplit(warnings, '|', parts);
   string json = "[";
   for(int i = 0; i < count; i++)
   {
      json += "\"" + JsonEscape(parts[i]) + "\"";
      if(i + 1 < count)
         json += ",";
   }
   json += "]";
   return json;
}

datetime YearStart(int year)
{
   MqlDateTime dt;
   dt.year = year;
   dt.mon = 1;
   dt.day = 1;
   dt.hour = 0;
   dt.min = 0;
   dt.sec = 0;
   return StructToTime(dt);
}

ENUM_TIMEFRAMES ParseTimeframe(string value, ENUM_TIMEFRAMES fallback)
{
   string upper = StringUpperCopy(Trim(value));
   if(upper == "M1") return PERIOD_M1;
   if(upper == "M5") return PERIOD_M5;
   if(upper == "M15") return PERIOD_M15;
   if(upper == "M30") return PERIOD_M30;
   if(upper == "H1") return PERIOD_H1;
   if(upper == "H4") return PERIOD_H4;
   if(upper == "D1") return PERIOD_D1;
   return fallback;
}

string ResolveMt5Symbol(string requested_symbol)
{
   string symbol = Trim(requested_symbol);
   if(SymbolSelect(symbol, true))
      return symbol;

   string upper = StringUpperCopy(symbol);
   if(StringFind(upper, "_DARWINEX") > 0)
   {
      int pos = StringFind(upper, "_DARWINEX");
      string base_symbol = StringSubstr(symbol, 0, pos);
      if(SymbolSelect(base_symbol, true))
         return base_symbol;
   }
   return symbol;
}

string ReadTextFile(string file_name)
{
   ResetLastError();
   int handle = FileOpen(file_name, FILE_READ | FILE_TXT | FILE_ANSI);
   if(handle == INVALID_HANDLE)
      return "";
   string text = "";
   while(!FileIsEnding(handle))
   {
      string token = FileReadString(handle);
      if(token != "")
         text += token + "\n";
   }
   FileClose(handle);
   return text;
}

bool WriteTextFile(string file_name, string text)
{
   ResetLastError();
   int handle = FileOpen(file_name, FILE_WRITE | FILE_TXT | FILE_ANSI);
   if(handle == INVALID_HANDLE)
   {
      Print("SQXInfoBridge FileOpen write failed: ", file_name, " error=", GetLastError());
      return false;
   }
   FileWriteString(handle, text);
   FileClose(handle);
   return true;
}

string GetIniValue(string text, string key, string fallback)
{
   string lines[];
   int count = StringSplit(text, '\n', lines);
   string prefix = key + "=";
   for(int i = 0; i < count; i++)
   {
      string line = Trim(lines[i]);
      if(StringFind(line, "#") == 0)
         continue;
      if(StringFind(line, prefix) == 0)
         return StringSubstr(line, StringLen(prefix));
   }
   return fallback;
}

string Trim(string value)
{
   string result = value;
   StringTrimLeft(result);
   StringTrimRight(result);
   return result;
}

string StringUpperCopy(string value)
{
   string result = value;
   StringToUpper(result);
   return result;
}

string SafeFileToken(string value)
{
   string result = "";
   for(int i = 0; i < StringLen(value); i++)
   {
      ushort ch = StringGetCharacter(value, i);
      bool ok = ((ch >= 'A' && ch <= 'Z') || (ch >= 'a' && ch <= 'z') || (ch >= '0' && ch <= '9') || ch == '_' || ch == '-');
      result += ok ? ShortToString(ch) : "_";
   }
   if(result == "")
      result = "request";
   return result;
}

string JsonEscape(string value)
{
   string result = "";
   for(int i = 0; i < StringLen(value); i++)
   {
      ushort ch = StringGetCharacter(value, i);
      if(ch == '\\')
         result += "\\\\";
      else if(ch == '"')
         result += "\\\"";
      else if(ch == '\n')
         result += "\\n";
      else if(ch == '\r')
         result += "\\r";
      else if(ch == '\t')
         result += "\\t";
      else
         result += ShortToString(ch);
   }
   return result;
}

string DoubleText(double value, int digits)
{
   if(!MathIsValidNumber(value))
      return "0";
   string text = DoubleToString(value, digits);
   while(StringFind(text, ".") >= 0 && StringSubstr(text, StringLen(text) - 1) == "0")
      text = StringSubstr(text, 0, StringLen(text) - 1);
   if(StringSubstr(text, StringLen(text) - 1) == ".")
      text = StringSubstr(text, 0, StringLen(text) - 1);
   if(text == "-0")
      text = "0";
   return text;
}

string ErrorJson(string request_id, string requested_symbol, string mt5_symbol, string code, int mt5_error)
{
   string json = "{\n";
   json += "  \"version\":\"" + BRIDGE_VERSION + "\",\n";
   json += "  \"requestId\":\"" + JsonEscape(request_id) + "\",\n";
   json += "  \"status\":\"error\",\n";
   json += "  \"symbol\":\"" + JsonEscape(requested_symbol) + "\",\n";
   json += "  \"mt5Symbol\":\"" + JsonEscape(mt5_symbol) + "\",\n";
   json += "  \"error\":\"" + JsonEscape(code) + "\",\n";
   json += "  \"mt5Error\":" + IntegerToString(mt5_error) + ",\n";
   json += "  \"writesSqxHost\":false,\"writesDataDb\":false,\"writesUserProjects\":false,\"mutatesDatabanks\":false,\"runsSqxTasks\":false,\"placesOrders\":false,\"usesMigrationTool\":false\n";
   json += "}\n";
   return json;
}
