import java.io.OutputStream;
import java.net.HttpURLConnection;
import java.net.URL;
import java.nio.charset.StandardCharsets;
import java.time.LocalDateTime;
import java.time.format.DateTimeFormatter;

public class client3 {

    public static void main(String[] args) {
        try {
            // 構建JSON數據
            String logTime = LocalDateTime.now().format(DateTimeFormatter.ofPattern("yyyy-MM-dd HH:mm:ss"));
            String logEntry = String.format(
                    "{\"HOST_NAME\": \"Test3 Java\", " +
                    "\"HOST_IP\": \"172.17.34.31\", " +
                    "\"SYSTEM_TYPE\": \"EBTS.P\", " +
                    "\"LEVEL\": \"INFO\", " +
                    "\"PROCESS_NAME\": \"E\", " +
                    "\"CONTENT\": \"This is a log entry content.\", " +
                    "\"LOG_TIME\": \"%s\"}", logTime);

            // 伺服器URL
            URL url = new URL("http://localhost:5000/log");
            HttpURLConnection conn = (HttpURLConnection) url.openConnection();

            // 設置請求方法和HTTP頭
            conn.setRequestMethod("POST");
            conn.setRequestProperty("Content-Type", "application/json; utf-8");
            conn.setRequestProperty("Accept", "application/json");
            conn.setDoOutput(true);

            // 發送請求數據
            try (OutputStream os = conn.getOutputStream()) {
                byte[] input = logEntry.getBytes(StandardCharsets.UTF_8);
                os.write(input, 0, input.length);
            }

            // 獲取響應狀態碼
            int responseCode = conn.getResponseCode();

            // 打印結果
            if (responseCode == HttpURLConnection.HTTP_CREATED) {
                System.out.println("Log entry sent successfully.");
            } else {
                System.out.println("Failed to send log entry. Status code: " + responseCode);
            }

        } catch (Exception e) {
            e.printStackTrace();
        }
    }
}

