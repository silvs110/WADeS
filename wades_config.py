import logging

datetime_format = "%Y-%m-d %H:%M:%S:%f"
prohibited_files = {"/etc/passwd", "/etc/shadow", "/etc/bashrc"}
anomaly_detected_message = "Anomalies found."
app_profile_retrieval_chunk_size = 10 ** 6
minimum_retrieval_size_for_modelling = 10
retrieval_periodicity = 3 * 60
max_retrieval_periodicity_sec = 60 * 60  # One hour
logging_level = logging.INFO
log_file_extension = ".log"
pid_file_extension = ".pid"
log_file_max_size_bytes = 5 * 1024 * 1024
max_number_rotating_log_files = 10
