/**
 * @file monitor.c
 * @brief Capture Linux inotify events as CSV security telemetry.
 *
 * Watches one directory for creates, modifications, deletions, renames, and
 * accesses. Records are escaped according to CSV rules so unusual filenames
 * cannot corrupt later analysis.
 *
 * @author Leslie Raya
 * @see https://github.com/leslieraya555/FileSentinel-AI
 */

#define _POSIX_C_SOURCE 200809L

#include <errno.h>
#include <limits.h>
#include <signal.h>
#include <stdbool.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <sys/inotify.h>
#include <sys/stat.h>
#include <time.h>
#include <unistd.h>

#define EVENT_BUFFER_SIZE (64 * 1024)
#define EVENT_MASK (IN_CREATE | IN_MODIFY | IN_DELETE | IN_MOVED_FROM | IN_MOVED_TO | IN_ACCESS)

static volatile sig_atomic_t keep_running = 1;

/** Request graceful shutdown after an interrupt or termination signal. */
static void handle_signal(int signal_number) {
    (void)signal_number;
    keep_running = 0;
}

/** Format the current UTC time using an ISO 8601 representation. */
static bool get_timestamp(char *buffer, size_t size) {
    const time_t now = time(NULL);
    struct tm utc_time;
    if (gmtime_r(&now, &utc_time) == NULL) {
        return false;
    }
    return strftime(buffer, size, "%Y-%m-%dT%H:%M:%SZ", &utc_time) > 0;
}

/** Write one escaped CSV field, including quotes when required. */
static void write_csv_field(FILE *file, const char *value) {
    const bool needs_quotes = strpbrk(value, ",\"\r\n") != NULL;
    if (needs_quotes) {
        fputc('"', file);
    }
    for (const char *cursor = value; *cursor != '\0'; ++cursor) {
        if (*cursor == '"') {
            fputc('"', file);
        }
        fputc(*cursor, file);
    }
    if (needs_quotes) {
        fputc('"', file);
    }
}

/** Initialize the event store when it is missing or empty. */
static bool ensure_csv_header(const char *csv_path) {
    struct stat details;
    if (stat(csv_path, &details) == 0 && details.st_size > 0) {
        return true;
    }

    FILE *file = fopen(csv_path, "w");
    if (file == NULL) {
        perror("Unable to initialize event store");
        return false;
    }
    fputs("timestamp,event_type,file_name,file_path\n", file);
    return fclose(file) == 0;
}

/** Convert one inotify mask into the normalized API event category. */
static const char *get_event_type(uint32_t mask) {
    if ((mask & IN_CREATE) != 0U) return "CREATE";
    if ((mask & IN_MODIFY) != 0U) return "MODIFY";
    if ((mask & IN_DELETE) != 0U) return "DELETE";
    if ((mask & IN_MOVED_FROM) != 0U) return "RENAMED_FROM";
    if ((mask & IN_MOVED_TO) != 0U) return "RENAMED_TO";
    if ((mask & IN_ACCESS) != 0U) return "ACCESS";
    return "UNKNOWN";
}

/** Append one validated event and flush it for near-real-time visibility. */
static bool log_event(
    FILE *event_file,
    const char *event_type,
    const char *file_name,
    const char *watched_path
) {
    char timestamp[32];
    char full_path[PATH_MAX];
    if (!get_timestamp(timestamp, sizeof(timestamp))) {
        fputs("Unable to create event timestamp\n", stderr);
        return false;
    }
    if (snprintf(full_path, sizeof(full_path), "%s/%s", watched_path, file_name) >= (int)sizeof(full_path)) {
        fputs("Event path exceeds PATH_MAX and was skipped\n", stderr);
        return false;
    }

    write_csv_field(event_file, timestamp);
    fputc(',', event_file);
    write_csv_field(event_file, event_type);
    fputc(',', event_file);
    write_csv_field(event_file, file_name);
    fputc(',', event_file);
    write_csv_field(event_file, full_path);
    fputc('\n', event_file);
    return fflush(event_file) == 0;
}

/** Validate arguments, register the watch, and stream kernel events. */
int main(int argc, char *argv[]) {
    if (argc < 2 || argc > 3) {
        fprintf(stderr, "Usage: %s <directory-to-watch> [events.csv]\n", argv[0]);
        return EXIT_FAILURE;
    }

    const char *watched_path = argv[1];
    const char *csv_path = argc == 3 ? argv[2] : "../data/events.csv";
    struct stat watched_details;
    if (stat(watched_path, &watched_details) != 0 || !S_ISDIR(watched_details.st_mode)) {
        fprintf(stderr, "Watch target is not an accessible directory: %s\n", watched_path);
        return EXIT_FAILURE;
    }
    if (!ensure_csv_header(csv_path)) {
        return EXIT_FAILURE;
    }

    FILE *event_file = fopen(csv_path, "a");
    if (event_file == NULL) {
        perror("Unable to open event store");
        return EXIT_FAILURE;
    }

    const int inotify_fd = inotify_init1(IN_CLOEXEC);
    if (inotify_fd == -1) {
        perror("inotify initialization failed");
        fclose(event_file);
        return EXIT_FAILURE;
    }
    const int watch_fd = inotify_add_watch(inotify_fd, watched_path, EVENT_MASK);
    if (watch_fd == -1) {
        perror("Unable to register watch directory");
        close(inotify_fd);
        fclose(event_file);
        return EXIT_FAILURE;
    }

    signal(SIGINT, handle_signal);
    signal(SIGTERM, handle_signal);
    printf("FileSentinel agent monitoring: %s\n", watched_path);
    printf("Telemetry destination: %s\n", csv_path);
    puts("Press Ctrl+C to stop safely.");

    char buffer[EVENT_BUFFER_SIZE] __attribute__((aligned(__alignof__(struct inotify_event))));
    while (keep_running) {
        const ssize_t length = read(inotify_fd, buffer, sizeof(buffer));
        if (length == -1) {
            if (errno == EINTR) continue;
            perror("Unable to read inotify events");
            break;
        }

        // A single read may contain several variable-length kernel records.
        for (char *cursor = buffer; cursor < buffer + length;) {
            const struct inotify_event *event = (const struct inotify_event *)cursor;
            if (event->len > 0 && (event->mask & IN_ISDIR) == 0U) {
                const char *event_type = get_event_type(event->mask);
                printf("%-12s %s\n", event_type, event->name);
                if (!log_event(event_file, event_type, event->name, watched_path)) {
                    fputs("Unable to persist event\n", stderr);
                }
            }
            cursor += sizeof(struct inotify_event) + event->len;
        }
    }

    inotify_rm_watch(inotify_fd, watch_fd);
    close(inotify_fd);
    fclose(event_file);
    puts("FileSentinel agent stopped.");
    return EXIT_SUCCESS;
}