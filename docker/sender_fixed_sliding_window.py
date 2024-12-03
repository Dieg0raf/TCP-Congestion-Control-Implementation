import socket
import time

# total packet size
PACKET_SIZE = 1024
# bytes reserved for sequence id
SEQ_ID_SIZE = 4
# bytes available for message
MESSAGE_SIZE = PACKET_SIZE - SEQ_ID_SIZE
# total packets to send
WINDOW_SIZE = 100

# read data
# 5319693 bytes
with open('file.mp3', 'rb') as f:
    data = f.read()

# create a udp socket
with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as udp_socket:

    # Start the timer
    start_time = time.time()

    # bind the socket to a OS port
    udp_socket.bind(("0.0.0.0", 5000))
    udp_socket.settimeout(1)
    
    # start sending data from 0th sequence
    seq_id = 0

    # helper variables
    end_time = None
    packets_sent = 0
    per_packet_times = {}
    packet_delay = 0
    packet_delays = {}
    jitter_sum = 0
    length_of_data = len(data)
    jitter_count = 0
    last_packet_delay = None

    print("Start sending")
    while seq_id < length_of_data:
        
        # create messages
        messages = []
        acks = {}
        seq_id_tmp = seq_id
        
        for i in range(WINDOW_SIZE):
            # construct messages
            message = int.to_bytes(seq_id_tmp, SEQ_ID_SIZE, byteorder='big', signed=True) + data[seq_id_tmp : seq_id_tmp + MESSAGE_SIZE]
            messages.append((seq_id_tmp, message))
            acks[seq_id_tmp] = False

            # move seq_id tmp pointer ahead
            seq_id_tmp += MESSAGE_SIZE

            # break if end of data (Don't over send)
            if seq_id_tmp >= length_of_data:
                break

        # Keep track of last sequence id sent in window
        last_seq_id = seq_id_tmp

        # send messages
        for stid, message in messages:
            udp_socket.sendto(message, ('localhost', 5001))
            per_packet_times[stid] = time.time()
            packets_sent += 1
        
        consecutive_ack_count = 0
        last_ack_id = -1
        
        while True:
            try:
                # wait for ack
                ack, _ = udp_socket.recvfrom(PACKET_SIZE)
                
                # extract ack id
                ack_id = int.from_bytes(ack[:SEQ_ID_SIZE], byteorder='big')

                # mark all packets before ack_id as acknowledged
                for i in range(seq_id, ack_id, MESSAGE_SIZE):
                    if acks[i] == False:
                        acks[i] = True

                        # Calculate packet delay
                        current_delay = time.time() - per_packet_times[i]
                        packet_delay += current_delay
                        packet_delays[i] = current_delay

                        # Calculate jitter
                        if last_packet_delay is not None:
                            jitter = abs(current_delay - last_packet_delay)
                            jitter_sum += jitter
                            jitter_count += 1
                        
                        last_packet_delay = current_delay

                # received the last ack for the entire data
                if ack_id >= length_of_data:
                    end_time = time.time()   
                    break

                # all acks received in window, move on
                if ack_id == last_seq_id:
                    break
                
                # check for consecutive duplicate acks
                if ack_id == last_ack_id:
                    consecutive_ack_count += 1
                else:
                    last_ack_id = ack_id
                    consecutive_ack_count = 1
                
                # resend the message if 3 or more consecutive acks are received
                if consecutive_ack_count >= 3:
                    message = int.to_bytes(ack_id, SEQ_ID_SIZE, byteorder='big', signed=True) + data[ack_id : ack_id + MESSAGE_SIZE]
                    udp_socket.sendto(message, ('localhost', 5001))
                    consecutive_ack_count = 0
                
            except socket.timeout:
                # Resend all unacknowledged messages
                for sid, message in messages:
                    if not acks[sid]:
                        udp_socket.sendto(message, ('localhost', 5001))
                
                last_ack_id = -1
                consecutive_ack_count = 0
                
        # move sequence id forward
        seq_id += MESSAGE_SIZE * WINDOW_SIZE
        
    # send final closing message
    udp_socket.sendto(int.to_bytes(-1, 4, signed=True, byteorder='big') + b'==FINACK==', ('localhost', 5001))

# Calculate metrics
total_time = end_time - start_time
throughput = length_of_data / total_time
avgPacketDelay = packet_delay / packets_sent
avgJitter = jitter_sum / jitter_count
performanceMetric = (0.2 * (throughput/2000)) + (0.1/avgJitter) + (0.8/avgPacketDelay)

# Output format to read it better
# print("===============Metrics TCP Tahoe===============")
# print(f"Total Time --> {total_time:.7f} seconds")
# print(f"Throughput --> {throughput:.7f} Bytes/seconds")
# print(f"Average Packet Delay --> {avgPacketDelay:.7f} seconds")
# print(f"Average Jitter --> {avgJitter:.7f} seconds")
# print(f"Performance Metric --> {performanceMetric:.7f}")
# print("=====================================")

# Output format for the metrics (how they want it in the assignment)
print(f"{throughput:.7f},{avgPacketDelay:.7f},{avgJitter:.7f},{performanceMetric:.7f}")