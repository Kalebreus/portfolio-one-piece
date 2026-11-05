import java.net.URI;
import java.net.http.HttpClient;
import java.net.http.HttpRequest;
import java.net.http.HttpResponse;
import java.time.Duration;

/**
 * Small Java example client for the optional, consent-based portfolio API.
 * Run manually for development; the website does not execute this program.
 */
public final class PortfolioAnalyticsClient {
    private PortfolioAnalyticsClient() {}

    public static void main(String[] args) throws Exception {
        String endpoint = System.getenv().getOrDefault(
            "PORTFOLIO_ANALYTICS_ENDPOINT",
            "http://127.0.0.1:8765/api/visit"
        );

        HttpRequest request = HttpRequest.newBuilder(URI.create(endpoint))
            .timeout(Duration.ofSeconds(5))
            .header("Content-Type", "application/json")
            .POST(HttpRequest.BodyPublishers.ofString("{\"event\":\"page_view\"}"))
            .build();

        HttpResponse<String> response = HttpClient.newHttpClient().send(
            request,
            HttpResponse.BodyHandlers.ofString()
        );

        System.out.println("API respondeu com HTTP " + response.statusCode());
        System.out.println(response.body());
    }
}
