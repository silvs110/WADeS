import logging

datetime_format = "%Y-%m-%d %H:%M:%S:%f"
prohibited_files = {"/etc/passwd", "/etc/shadow", "/etc/bashrc", "/etc/profile", "/etc/hosts", "/proc/cpuinfo",
                    "/proc/stat", "/proc/swaps", "/etc/aliases"}
anomaly_detected_message = "Anomalies found."
app_profile_retrieval_chunk_size = 10 ** 6
minimum_retrieval_size_for_modelling = 10
is_modelling = True
retrieval_periodicity_sec = 1.5 * 60
max_retrieval_periodicity_sec = 60 * 60  # One hour
logging_level = logging.INFO
log_file_extension = ".log"
pid_file_extension = ".pid"
log_file_max_size_bytes = 5 * 1024 * 1024
max_number_rotating_log_files = 10
modeller_thread_port = 7657
localhost_address = "127.0.0.1"
retrieval_timestamp_file_name = "retrieval_timestamp.txt"
app_profile_file_name = "app_profiles.csv"
abnormal_apps_file_name = "abnormal_apps.csv"
run_modeller_server = False
