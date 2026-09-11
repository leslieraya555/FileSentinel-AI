#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>
#include <sys/inotify.h>
#include <time.h>
#include <limits.h>
#include <errno.h>

#define EVENT_SIZE  (sizeof(struct inotify_event))
#define BUF_LEN     (1024 * (EVENT_SIZE + NAME_MAX + 1))

void get_timestamp(char *buffer, size_t size) {
    time_t now = time(NULL);
    struct tm *t = localtime(&now);

    if (t == NULL) {
        snprintf(buffer, size, "UNKNOWN_TIME");
        return;
    }

    strftime(buffer, size, "%Y-%m-%d %H:%M:%S", t);
}

void ensure_csv_header(const char *csv_path) {
    FILE *file = fopen(csv_path, "r");

    if (file != NULL) {
        fclose(file);
        return;
    }

    file = fopen(csv_path, "w");

    if (file == NULL) {
        perror("Could not create events.csv");
        return;
    }

    fprintf(file, "timestamp,event_type,file_name,file_path\n");
    fclose(file);
}

void log_event(const char *csv_path, const char *event_type, const char *file_name, const char *watched_path) {
    FILE *file = fopen(csv_path, "a");

    if (file == NULL) {
        perror("Could not open events.csv");
        return;
    }

    char timestamp[64];
    get_timestamp(timestamp, sizeof(timestamp));

    fprintf(file, "%s,%s,%s,%s/%s\n",
            timestamp,
            event_type,
            file_name,
            watched_path,
            file_name);

    fclose(file);
}

const char* get_event_type(struct inotify_event *event) {
    if (event->mask & IN_CREATE) return "CREATE";
    if (event->mask & IN_MODIFY) return "MODIFY";
    if (event->mask & IN_DELETE) return "DELETE";
    if (event->mask & IN_MOVED_FROM) return "RENAMED_FROM";
    if (event->mask & IN_MOVED_TO) return "RENAMED_TO";
    if (event->mask & IN_ACCESS) return "ACCESS";
    return "UNKNOWN";
}

int main(int argc, char *argv[]) {
    if (argc < 2) {
        printf("Usage: %s <folder_to_watch>\n", argv[0]);
        printf("Example: ./monitor ~/watch_folder\n");
        return 1;
    }

    const char *watched_path = argv[1];
    const char *csv_path = "../data/events.csv";

    ensure_csv_header(csv_path);

    int fd = inotify_init();

    if (fd < 0) {
        perror("inotify_init failed");
        return 1;
    }

    int wd = inotify_add_watch(
        fd,
        watched_path,
        IN_CREATE | IN_MODIFY | IN_DELETE | IN_MOVED_FROM | IN_MOVED_TO | IN_ACCESS
    );

    if (wd == -1) {
        perror("inotify_add_watch failed");
        close(fd);
        return 1;
    }

    printf("FileSentinel AI agent is running...\n");
    printf("Watching folder: %s\n", watched_path);
    printf("Logging events to: %s\n", csv_path);
    printf("Press CTRL+C to stop.\n\n");

    char buffer[BUF_LEN];

    while (1) {
        ssize_t length = read(fd, buffer, BUF_LEN);

        if (length < 0) {
            if (errno == EINTR) {
                continue;
            }

            perror("read failed");
            break;
        }

        ssize_t i = 0;

        while (i < length) {
            struct inotify_event *event = (struct inotify_event *) &buffer[i];

            if (event->len > 0) {
                const char *event_type = get_event_type(event);

                printf("Event: %-12s | File: %s\n", event_type, event->name);
                log_event(csv_path, event_type, event->name, watched_path);
            }

            i += EVENT_SIZE + event->len;
        }
    }

    inotify_rm_watch(fd, wd);
    close(fd);

    return 0;
}