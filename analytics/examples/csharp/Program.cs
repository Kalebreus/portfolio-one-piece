using System.Net.Http.Json;

var endpoint = Environment.GetEnvironmentVariable("PORTFOLIO_ANALYTICS_ENDPOINT")
    ?? "http://127.0.0.1:8765/api/visit";

using var client = new HttpClient { Timeout = TimeSpan.FromSeconds(5) };
using var response = await client.PostAsJsonAsync(endpoint, new { @event = "page_view" });

Console.WriteLine($"API respondeu com HTTP {(int)response.StatusCode}");
Console.WriteLine(await response.Content.ReadAsStringAsync());
