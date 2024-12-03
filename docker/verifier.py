import hashlib

def calculate_checksum(file_path, algorithm='md5'):
    hash_func = hashlib.new(algorithm)
    with open(file_path, 'rb') as f:
        while chunk := f.read(8192):
            hash_func.update(chunk)
    return hash_func.hexdigest()

original_file_checksum = calculate_checksum('file.mp3', 'md5')
received_file_checksum = calculate_checksum('hdd/file2.mp3', 'md5')

if original_file_checksum == received_file_checksum:
    print("Files are identical. All packets were sent and received correctly.")
else:
    print("Files are different. There was an error in transmission.")