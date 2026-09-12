def log_count(count):
    with open("count_log.txt", "a") as f:
        f.write(f"Ürün sayısı: {count}\n")
