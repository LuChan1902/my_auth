#include <iostream>
#include <cstring>
#include <sys/socket.h>
#include <netinet/in.h>
#include <netinet/tcp.h>
#include <arpa/inet.h>
#include <unistd.h>
#include <thread>
#include <vector>
#include <signal.h>

#define PUBLIC_PORT 8000
#define INTERNAL_PORT 8888
#define BUFFER_SIZE 65535

void set_nodelay(int sock) {
    int flag = 1;
    setsockopt(sock, IPPROTO_TCP, TCP_NODELAY, (char *)&flag, sizeof(int));
}

void forward_data(int source_fd, int dest_fd, std::string direction) {
    char buffer[BUFFER_SIZE];
    ssize_t bytes_read;
    while (true) {
        bytes_read = recv(source_fd, buffer, BUFFER_SIZE, 0);
        if (bytes_read > 0) {
            std::cout << "[Data] " << direction << " " << bytes_read << " bytes" << std::endl;
            if (send(dest_fd, buffer, bytes_read, MSG_NOSIGNAL) <= 0) break;
        } else break;
    }
    shutdown(source_fd, SHUT_RDWR);
    shutdown(dest_fd, SHUT_RDWR);
    close(source_fd);
    close(dest_fd);
}

int main() {
    signal(SIGPIPE, SIG_IGN);
    int server_fd;
    struct sockaddr_in address;
    int opt = 1;

    if ((server_fd = socket(AF_INET, SOCK_STREAM, 0)) == 0) return 1;
    setsockopt(server_fd, SOL_SOCKET, SO_REUSEADDR, &opt, sizeof(opt));

    address.sin_family = AF_INET;
    address.sin_addr.s_addr = INADDR_ANY;
    address.sin_port = htons(PUBLIC_PORT);

    if (bind(server_fd, (struct sockaddr *)&address, sizeof(address)) < 0) {
        perror("Bind failed"); return 1;
    }
    listen(server_fd, 5);
    std::cout << ">>> Gateway Listening on 8000 <<<" << std::endl;

    while (true) {
        struct sockaddr_in client_addr;
        socklen_t len = sizeof(client_addr);
        int client_sock = accept(server_fd, (struct sockaddr *)&client_addr, &len);
        if (client_sock < 0) continue;
        set_nodelay(client_sock);

        int server_sock = socket(AF_INET, SOCK_STREAM, 0);
        struct sockaddr_in backend_addr;
        backend_addr.sin_family = AF_INET;
        backend_addr.sin_port = htons(INTERNAL_PORT);
        inet_pton(AF_INET, "127.0.0.1", &backend_addr.sin_addr);

        if (connect(server_sock, (struct sockaddr *)&backend_addr, sizeof(backend_addr)) < 0) {
            close(client_sock); continue;
        }
        set_nodelay(server_sock);

        std::cout << "[+] New Session" << std::endl;
        std::thread(forward_data, client_sock, server_sock, "GDL->MDS").detach();
        std::thread(forward_data, server_sock, client_sock, "MDS->GDL").detach();
    }
    return 0;
}
