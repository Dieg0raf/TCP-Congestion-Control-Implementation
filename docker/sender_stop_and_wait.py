import socket
import time

# total packet size
PACKET_SIZE = 1024
# bytes reserved for sequence id
SEQ_ID_SIZE = 4
# bytes available for message
MESSAGE_SIZE = PACKET_SIZE - SEQ_ID_SIZE

# read data
with open('file.mp3', 'rb') as f:
# with open('send.txt', 'rb') as f:
    data = f.read()

# create a udp socket
with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as udp_socket:

    # Start the timer
    start_time = time.time()

    # bind the socket to a OS port
    udp_socket.bind(("0.0.0.0", 5000))
    udp_socket.settimeout(1)

    # helper variables
    end_time = None
    packets_sent = 0
    per_packet_times = {}
    packet_delay = 0
    jitter_sum = 0
    jitter_count = 0
    last_packet_delay = None
    length_of_data = len(data)

    # start sending data from 0th sequence
    seq_id = 0

    print("Start sending")
    while seq_id < length_of_data:

        # construct message
        message = int.to_bytes(seq_id, SEQ_ID_SIZE, byteorder='big', signed=True) + data[seq_id : seq_id + MESSAGE_SIZE]

        # send message 
        udp_socket.sendto(message, ('localhost', 5001))
        per_packet_times[seq_id] = time.time()
        packets_sent += 1

        # wait for acknowledgement
        while True:
            try: 
                # wait for ack
                ack, _ = udp_socket.recvfrom(PACKET_SIZE)
                ack_id = int.from_bytes(ack[:SEQ_ID_SIZE], byteorder='big')
                print(ack_id, ack[SEQ_ID_SIZE:])


                # received the last ack for the entire data
                if ack_id >= length_of_data:
                    end_time = time.time()   
                    break

                # correct ack_id was received, move on
                if ack_id == (seq_id + len(data[seq_id : seq_id + MESSAGE_SIZE])):

                    # Calculate packet delay
                    current_delay = time.time() - per_packet_times[seq_id]
                    packet_delay += current_delay

                    # Calculate jitter
                    if last_packet_delay is not None:
                        jitter = abs(current_delay - last_packet_delay)
                        jitter_sum += jitter
                        jitter_count += 1
                    
                    last_packet_delay = current_delay
                    break

            except socket.timeout:

                # no ack received, resend unAcked message
                udp_socket.sendto(message, ('localhost', 5001))

        # move sequence id forward
        seq_id += MESSAGE_SIZE

    # send final closing message
    udp_socket.sendto(int.to_bytes(-1, 4, signed=True, byteorder='big') + b'==FINACK==', ('localhost', 5001))

# Calculate metrics
total_time = end_time - start_time
throughput = length_of_data / total_time
avgPacketDelay = packet_delay / packets_sent
avgJitter = jitter_sum / jitter_count
performanceMetric = (0.2 * (throughput/2000)) + (0.1/avgJitter) + (0.8/avgPacketDelay)

# Output format for the metrics
print(f"{throughput:.7f},{avgPacketDelay:.7f},{avgJitter:.7f},{performanceMetric:.7f}")