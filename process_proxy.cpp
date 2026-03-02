#include <iostream>
#include <vector>
#include <sys/socket.h>
#include <netinet/in.h>
#include <arpa/inet.h>
#include <unistd.h>
#include <signal.h>
#include <fcntl.h>
#include <errno.h>
#include <netinet/tcp.h>

#define LOCAL_PORT 8000
#define REMOTE_PORT 8888
#define REMOTE_HOST "127.0.0.1"
#define BUFFER_SIZE 65536

void set_nodelay(int sockfd) {
    int flag = 1;
    setsockopt(sockfd, IPPROTO_TCP, TCP_NODELAY, (char *)&flag, sizeof(int));
}

int forward_data(int source_fd, int dest_fd) {
    char buffer[BUFFER_SIZE];
    ssize_t bytes_read = recv(source_fd, buffer, sizeof(buffer), 0);
    if (bytes_read <= 0) return -1; 
    
    ssize_t bytes_sent = 0;
    while (bytes_sent < bytes_read) {
        ssize_t sent = send(dest_fd, buffer + bytes_sent, bytes_read - bytes_sent, 0);
        if (sent <= 0) {
            if (errno == EAGAIN || errno == EWOULDBLOCK) continue;
            return -1;
        }
        bytes_sent += sent;
    }
    return 0;
}

int main() {
    signal(SIGPIPE, SIG_IGN); 
    int server_fd, client_fd, remote_fd;
    struct sockaddr_in address, serv_addr;
    int opt = 1;
    socklen_t addrlen = sizeof(address);

    server_fd = socket(AF_INET, SOCK_STREAM, 0);
    setsockopt(server_fd, SOL_SOCKET, SO_REUSEADDR, &opt, sizeof(opt));
    address.sin_family = AF_INET;
    address.sin_addr.s_addr = INADDR_ANY; 
    address.sin_port = htons(LOCAL_PORT);
    
    bind(server_fd, (struct sockaddr *)&address, sizeof(address));
    listen(server_fd, 3);
    
    std::cout << ">>> Silent Proxy Listening on 8000..." << std::endl;

    while (true) {
        client_fd = accept(server_fd, (struct sockaddr *)&address, &addrlen);
        if (client_fd < 0) continue;
        set_nodelay(client_fd);

        remote_fd = socket(AF_INET, SOCK_STREAM, 0);
        serv_addr.sin_family = AF_INET;
        serv_addr.sin_port = htons(REMOTE_PORT);
        inet_pton(AF_INET, REMOTE_HOST, &serv_addr.sin_addr);

        if (connect(remote_fd, (struct sockaddr *)&serv_addr, sizeof(serv_addr)) < 0) {
            close(client_fd);
            continue;
        }
        set_nodelay(remote_fd);

        fd_set readfds;
        while (true) {
            FD_ZERO(&readfds);
            FD_SET(client_fd, &readfds);
            FD_SET(remote_fd, &readfds);
            int max_sd = (client_fd > remote_fd) ? client_fd : remote_fd;

            if (select(max_sd + 1, &readfds, NULL, NULL, NULL) < 0) break;

            if (FD_ISSET(client_fd, &readfds)) {
                if (forward_data(client_fd, remote_fd) < 0) break;
            }
            if (FD_ISSET(remote_fd, &readfds)) {
                if (forward_data(remote_fd, client_fd) < 0) break;
            }
        }
        close(client_fd);
        close(remote_fd);
    }
    return 0;
}
