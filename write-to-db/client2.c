#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <curl/curl.h>
#include <time.h>

void get_current_datetime(char *buffer, size_t size) {
    time_t now = time(NULL);
    struct tm *t = localtime(&now);
    strftime(buffer, size, "%Y-%m-%d %H:%M:%S", t);
}

int main(void) {
    CURL *curl;
    CURLcode res;

    curl_global_init(CURL_GLOBAL_DEFAULT);
    curl = curl_easy_init();

    if(curl) {
        char datetime[20];
        get_current_datetime(datetime, sizeof(datetime));

        char json_data[512];
        snprintf(json_data, sizeof(json_data),
                 "{\"HOST_NAME\": \"Test2 C\", \"HOST_IP\": \"192.168.1.1\", \"SYSTEM_TYPE\": \"example_system\", \"LEVEL\": \"INFO\", \"PROCESS_NAME\": \"example_process\", \"CONTENT\": \"This is a log entry sent by C client.\", \"LOG_TIME\": \"%s\"}",
                 datetime);

        curl_easy_setopt(curl, CURLOPT_URL, "http://localhost:5000/log");
        curl_easy_setopt(curl, CURLOPT_POSTFIELDS, json_data);

        struct curl_slist *headers = NULL;
        headers = curl_slist_append(headers, "Content-Type: application/json");
        curl_easy_setopt(curl, CURLOPT_HTTPHEADER, headers);

        res = curl_easy_perform(curl);
        if(res != CURLE_OK) {
            fprintf(stderr, "curl_easy_perform() failed: %s\n", curl_easy_strerror(res));
        }

        curl_slist_free_all(headers);
        curl_easy_cleanup(curl);
    }

    curl_global_cleanup();
    return 0;
}

