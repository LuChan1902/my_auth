#include <iostream>
#include <cstring>
#include <sys/socket.h>
#include <netinet/in.h>
#include <netinet/tcp.h>
#include <arpa/inet.h>
#include <unistd.h>
#include <thread>
#include <string>

#define PUBLIC_PORT 8000
#define INTERNAL_PORT 8888
#define BUFFER_SIZE 4194304

void set_nodelay(int sock) {
    int flag = 1;
    setsockopt(sock, IPPROTO_TCP, TCP_NODELAY, (char *)&flag, sizeof(int));
}

void forward_data(int source_fd, int dest_fd) {
    char* buffer = new char[BUFFER_SIZE]; 
    ssize_t bytes_read;
    while ((bytes_read = recv(source_fd, buffer, BUFFER_SIZE, 0)) > 0) {
        if (send(dest_fd, buffer, bytes_read, MSG_NOSIGNAL) <= 0) break;
    }
    delete[] buffer;
    close(source_fd);
    close(dest_fd);
}

int main() {
    int server_fd = socket(AF_INET, SOCK_STREAM, 0);
    int opt = 1;
    setsockopt(server_fd, SOL_SOCKET, SO_REUSEADDR, &opt, sizeof(opt));

    struct sockaddr_in address;
    address.sin_family = AF_INET;
    address.sin_port = htons(PUBLIC_PORT);
    address.sin_addr.s_addr = INADDR_ANY;

    bind(server_fd, (struct sockaddr *)&address, sizeof(address));
    listen(server_fd, 5);
    std::cout << "[INFO] Proxy listening on port " << PUBLIC_PORT << std::endl;

    while (true) {
        struct sockaddr_in client_addr;
        socklen_t len = sizeof(client_addr);
        int client_sock = accept(server_fd, (struct sockaddr *)&client_addr, &len);
        if (client_sock < 0) continue;
        set_nodelay(client_sock);

        char buffer[8192];
        ssize_t bytes_read = recv(client_sock, buffer, sizeof(buffer), 0);
        if (bytes_read <= 0) { close(client_sock); continue; }

        int server_sock = socket(AF_INET, SOCK_STREAM, 0);
        struct sockaddr_in b_addr;
        b_addr.sin_family = AF_INET;
        b_addr.sin_port = htons(INTERNAL_PORT);
        inet_pton(AF_INET, "127.0.0.1", &b_addr.sin_addr);

        if (connect(server_sock, (struct sockaddr *)&b_addr, sizeof(b_addr)) < 0) {
            close(client_sock); continue;
        }
        set_nodelay(server_sock);

        send(server_sock, buffer, bytes_read, MSG_NOSIGNAL);
        ssize_t ack_len = recv(server_sock, buffer, sizeof(buffer), 0);
        if (ack_len <= 0) { close(client_sock); close(server_sock); continue; }
        send(client_sock, buffer, ack_len, MSG_NOSIGNAL);

        bytes_read = recv(client_sock, buffer, sizeof(buffer), 0);
        if (bytes_read <= 0) { close(client_sock); close(server_sock); continue; }

        std::string cmd_payload(buffer, bytes_read);
        
        // 解析：提取双引号内的具体尝试密码
        std::string attempted_pass = "unknown";
        size_t start_quote = cmd_payload.find('"');
        if (start_quote != std::string::npos) {
            size_t end_quote = cmd_payload.find('"', start_quote + 1);
            if (end_quote != std::string::npos) {
                attempted_pass = cmd_payload.substr(start_quote + 1, end_quote - start_quote - 1);
            }
        }

        // 校验并输出具体密码状态
        if (attempted_pass == "654321") {
            std::cout << "[AUTH] Accepted: " << attempted_pass << std::endl;
            send(server_sock, buffer, bytes_read, MSG_NOSIGNAL);

            std::thread(forward_data, client_sock, server_sock).detach();
            std::thread(forward_data, server_sock, client_sock).detach();
        } else {
            std::cout << "[AUTH] Denied: " << attempted_pass << std::endl;
            close(client_sock);
            close(server_sock);
        }
    }
    return 0;
}
